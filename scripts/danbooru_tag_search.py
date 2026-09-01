#!/usr/bin/env python3
"""Danbooru tag search/check helper for the VN ComfyUI workflow pack.

The local Danbooru taxonomy SQLite DB exported for ``cksdnfas/danbooru-db-viewer``
is the primary tag oracle when it is present next to this workflow pack.  The
legacy ``danbooru_tag.csv`` file is still supported as a compatibility/fallback
source, but the helper no longer requires it for normal search/check operation.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "danbooru_tag.csv"
DEFAULT_DB_CANDIDATES = (
    ROOT / "danbooru-taxonomy.release.sqlite",
    ROOT / "danbooru-taxonomy.sqlite",
    ROOT / "danbooru.sqlite",
)


@dataclass(frozen=True)
class CsvTag:
    tag: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class SearchResult:
    tag: str
    match: str
    score: int
    aliases: tuple[str, ...]
    category: str = ""
    post_count: str = ""
    source: str = "csv"


@dataclass(frozen=True)
class DbTag:
    tag: str
    category: str
    post_count: int
    match: str
    score: int


def normalize_search_key(value: str | None) -> str:
    """Normalize like danbooru-db-viewer: trim, lower, spaces to underscores."""
    return (value or "").strip().lower().replace(" ", "_")


def display_query(value: str | None) -> str:
    return normalize_search_key(value).replace("_", " ")


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def default_db_path() -> Path | None:
    for path in DEFAULT_DB_CANDIDATES:
        if path.exists():
            return path
    return None


def csv_path_is_default(path: Path) -> bool:
    try:
        return path.resolve() == DEFAULT_CSV.resolve()
    except OSError:
        return path == DEFAULT_CSV


def effective_db_path(args: argparse.Namespace) -> Path | None:
    """Return the SQLite DB path to use.

    Auto-detection is intentionally disabled when callers pass a non-default
    CSV path (unit tests or one-off legacy checks) unless they explicitly pass
    ``--db``.  Normal workflow-pack usage with the default root files gets the
    local release SQLite DB automatically.
    """
    if getattr(args, "no_db", False):
        return None
    explicit = getattr(args, "db", None)
    if explicit:
        return explicit
    if not csv_path_is_default(getattr(args, "csv", DEFAULT_CSV)):
        return None
    return default_db_path()


def load_csv_tags(path: Path, *, required: bool = False) -> list[CsvTag]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"CSV not found: {path}")
        return []
    rows: list[CsvTag] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required_columns = {"tag", "aliases"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(f"{path} must contain columns: tag, aliases")
        for row in reader:
            tag = (row.get("tag") or "").strip()
            if not tag:
                continue
            aliases = tuple(
                alias.strip()
                for alias in (row.get("aliases") or "").split(",")
                if alias.strip()
            )
            rows.append(CsvTag(tag=tag, aliases=aliases))
    return rows


def csv_index(rows: Iterable[CsvTag]) -> dict[str, CsvTag]:
    index: dict[str, CsvTag] = {}
    for row in rows:
        index[normalize_search_key(row.tag)] = row
        for alias in row.aliases:
            index.setdefault(normalize_search_key(alias), row)
    return index


def searchable_text(row: CsvTag) -> str:
    values = [row.tag, *row.aliases]
    # Parenthetical Danbooru disambiguators are useful search words; expose both
    # ``window_(computing)`` and a display-ish ``window computing`` surface.
    display_values = [value.replace("_", " ").replace("(", " ").replace(")", " ") for value in values]
    return " ".join([*values, *display_values]).lower()


def raw_search_tokens(value: str) -> list[str]:
    return [
        token.strip()
        for token in normalize_search_key(value).replace("(", "_").replace(")", "_").split("_")
        if token.strip()
    ]


def token_variants(token: str) -> set[str]:
    variants = {token}
    for suffix in ("ing", "er", "ers", "ed", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 3:
            variants.add(token[: -len(suffix)])
    return variants


def all_tokens_match_by_stem(query: str, haystack: str) -> bool:
    query_tokens = raw_search_tokens(query)
    row_variant_sets = [token_variants(token) for token in raw_search_tokens(haystack)]
    if not query_tokens or not row_variant_sets:
        return False
    for query_token in query_tokens:
        query_variants = token_variants(query_token)
        if not any(query_variants.intersection(row_variants) for row_variants in row_variant_sets):
            return False
    return True


def any_token_matches_by_stem(query: str, haystack: str) -> bool:
    query_variants = set().union(*(token_variants(token) for token in raw_search_tokens(query)))
    row_variants = set().union(*(token_variants(token) for token in raw_search_tokens(haystack)))
    return bool(query_variants and row_variants and query_variants.intersection(row_variants))


def classify_match(row: CsvTag, query_key: str) -> tuple[str, int] | None:
    tag_key = normalize_search_key(row.tag)
    alias_keys = [normalize_search_key(alias) for alias in row.aliases]
    all_keys = [tag_key, *alias_keys]
    haystack = searchable_text(row)

    if query_key == tag_key:
        return "exact", 1000
    if query_key in alias_keys:
        return "alias", 950
    if tag_key.startswith(query_key):
        return "prefix", 850
    if any(alias_key.startswith(query_key) for alias_key in alias_keys):
        return "alias_prefix", 825
    if query_key in tag_key:
        return "substring", 700
    if any(query_key in alias_key for alias_key in alias_keys):
        return "alias_substring", 675

    query_parts = [part for part in query_key.split("_") if part]
    if query_parts and all(any(part in key for key in all_keys) for part in query_parts):
        return "token", 600

    if all_tokens_match_by_stem(query_key, haystack):
        return "stem_token", 575

    if query_parts and any(part and any(part in key for key in all_keys) for part in query_parts):
        return "partial_token", 450
    if any_token_matches_by_stem(query_key, haystack):
        return "partial_stem", 425
    return None


def search_csv(rows: Iterable[CsvTag], query: str, limit: int) -> list[SearchResult]:
    query_key = normalize_search_key(query)
    if not query_key:
        return []
    results: list[SearchResult] = []
    for row in rows:
        match = classify_match(row, query_key)
        if match is None:
            continue
        match_name, score = match
        results.append(SearchResult(row.tag, match_name, score, row.aliases, source="csv"))
    results.sort(key=lambda r: (-r.score, len(r.tag), r.tag))
    return results[:limit]


def sqlite_available(db_path: Path | None) -> bool:
    if db_path is None or not db_path.exists():
        return False
    try:
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
            conn.execute("PRAGMA query_only = ON")
            return conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='tags'"
            ).fetchone() is not None
    except sqlite3.Error:
        return False


def search_sqlite(db_path: Path | None, query: str, limit: int) -> list[SearchResult]:
    query_key = normalize_search_key(query)
    if not query_key or not sqlite_available(db_path):
        return []
    assert db_path is not None
    pattern = f"%{escape_like(query_key)}%"
    display_pattern = f"%{escape_like(display_query(query))}%"
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        rows = list(
            conn.execute(
                """
                SELECT name, normalized_name, display_name, category_name, post_count
                FROM tags
                WHERE is_deprecated = 0
                  AND (normalized_name LIKE ? ESCAPE '\\' OR display_name LIKE ? ESCAPE '\\')
                ORDER BY
                  CASE
                    WHEN normalized_name = ? THEN 0
                    WHEN display_name = ? THEN 1
                    WHEN normalized_name LIKE ? ESCAPE '\\' THEN 2
                    ELSE 3
                  END,
                  post_count DESC,
                  name ASC
                LIMIT ?
                """,
                [
                    pattern,
                    display_pattern,
                    query_key,
                    display_query(query),
                    f"{escape_like(query_key)}%",
                    limit,
                ],
            )
        )
    results: list[SearchResult] = []
    for row in rows:
        csv_stub = CsvTag(tag=str(row["name"]), aliases=())
        match = classify_match(csv_stub, query_key) or ("db", 500)
        results.append(
            SearchResult(
                tag=str(row["name"]),
                match=match[0],
                score=match[1],
                aliases=(),
                category=str(row["category_name"]),
                post_count=str(int(row["post_count"])),
                source="db",
            )
        )
    return results


def lookup_sqlite_tag(db_path: Path | None, token: str) -> DbTag | None:
    token_key = normalize_search_key(token)
    if not token_key or not sqlite_available(db_path):
        return None
    assert db_path is not None
    token_display = token_key.replace("_", " ")
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only = ON")
        row = conn.execute(
            """
            SELECT name, category_name, post_count, 'db_exact' AS match, 1000 AS score
            FROM tags
            WHERE is_deprecated = 0
              AND (normalized_name = ? OR name = ? OR display_name = ?)
            ORDER BY post_count DESC, name ASC
            LIMIT 1
            """,
            [token_key, token_key, token_display],
        ).fetchone()
        if row is None:
            row = conn.execute(
                """
                SELECT t.name, t.category_name, t.post_count, 'db_alias' AS match, 950 AS score
                FROM tag_aliases a
                JOIN tags t ON t.id = a.target_tag_id
                WHERE a.status = 'active'
                  AND t.is_deprecated = 0
                  AND a.alias_normalized_name = ?
                ORDER BY t.post_count DESC, t.name ASC
                LIMIT 1
                """,
                [token_key],
            ).fetchone()
    if row is None:
        return None
    return DbTag(
        tag=str(row["name"]),
        category=str(row["category_name"]),
        post_count=int(row["post_count"]),
        match=str(row["match"]),
        score=int(row["score"]),
    )


def merge_results(csv_results: list[SearchResult], db_results: list[SearchResult], limit: int) -> list[SearchResult]:
    by_tag: dict[str, SearchResult] = {result.tag: result for result in csv_results}
    for db_result in db_results:
        existing = by_tag.get(db_result.tag)
        if existing:
            by_tag[db_result.tag] = SearchResult(
                tag=existing.tag,
                match=existing.match,
                score=max(existing.score, db_result.score),
                aliases=existing.aliases,
                category=db_result.category,
                post_count=db_result.post_count,
                source="csv+db",
            )
        else:
            by_tag[db_result.tag] = db_result
    results = list(by_tag.values())
    results.sort(
        key=lambda r: (
            -r.score,
            -(int(r.post_count) if r.post_count.isdigit() else 0),
            len(r.tag),
            r.tag,
        )
    )
    return results[:limit]


def parse_prompt_tokens(prompt: str) -> list[str]:
    return [normalize_search_key(token) for token in prompt.split(",") if normalize_search_key(token)]


def print_results(results: list[SearchResult], *, include_db_columns: bool) -> None:
    columns = ["tag", "match", "score", "aliases"]
    if include_db_columns:
        columns.extend(["category", "post_count", "source"])
    print("\t".join(columns))
    for result in results:
        values = [result.tag, result.match, str(result.score), ",".join(result.aliases)]
        if include_db_columns:
            values.extend([result.category, result.post_count, result.source])
        print("\t".join(values))


def command_search(args: argparse.Namespace) -> int:
    db_path = effective_db_path(args)
    rows = load_csv_tags(args.csv, required=not sqlite_available(db_path))
    csv_results = search_csv(rows, args.query, args.limit)
    db_results = search_sqlite(db_path, args.query, args.limit)
    results = merge_results(csv_results, db_results, args.limit)
    print_results(results, include_db_columns=sqlite_available(db_path))
    return 0 if results else 1


def command_check(args: argparse.Namespace) -> int:
    db_path = effective_db_path(args)
    db_ok = sqlite_available(db_path)
    rows = load_csv_tags(args.csv, required=args.mode == "csv" or (args.mode in {"auto", "csv-or-db"} and not db_ok))
    index = csv_index(rows)
    mode = args.mode
    if mode == "auto":
        mode = "db" if db_ok else "csv"
    had_missing = False
    for token in parse_prompt_tokens(args.prompt):
        db_found = lookup_sqlite_tag(db_path, token) if mode in {"db", "csv-or-db"} else None
        csv_found = index.get(token) if mode in {"csv", "csv-or-db"} else None
        if db_found:
            print(
                f"OK\t{db_found.tag}\tinput={token}\tsource=db\tcategory={db_found.category}\tpost_count={db_found.post_count}"
            )
            continue
        if csv_found:
            print(f"OK\t{csv_found.tag}\tinput={token}\tsource=csv")
            continue
        had_missing = True
        print(f"MISSING\t{token}")
        # DB suggestions first when available; they carry count/category evidence.
        for suggestion in search_sqlite(db_path, token, args.suggestions):
            print(
                f"SUGGEST\t{suggestion.tag}\t{suggestion.match}\t{suggestion.score}"
                f"\tsource=db\tcategory={suggestion.category}\tpost_count={suggestion.post_count}"
            )
        for suggestion in search_csv(rows, token, args.suggestions):
            print(f"SUGGEST\t{suggestion.tag}\t{suggestion.match}\t{suggestion.score}\tsource=csv")
    return 1 if had_missing else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search/check local Danbooru tags for workflow prompts.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Optional legacy CSV fallback path")
    parser.add_argument("--db", type=Path, help="Danbooru taxonomy SQLite DB from danbooru-db-viewer; auto-detected by default")
    parser.add_argument("--no-db", action="store_true", help="Disable SQLite auto-detection and use CSV only")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search local DB, optionally merged with legacy CSV aliases")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    # Keep historical placement working: `search QUERY --db path`.
    search.add_argument("--db", type=Path, help=argparse.SUPPRESS)
    search.add_argument("--no-db", action="store_true", help=argparse.SUPPRESS)
    search.set_defaults(func=command_search)

    check = subparsers.add_parser("check", help="Fail-closed check of comma-separated prompt tags")
    check.add_argument("prompt")
    check.add_argument("--suggestions", type=int, default=5)
    check.add_argument("--db", type=Path, help=argparse.SUPPRESS)
    check.add_argument("--no-db", action="store_true", help=argparse.SUPPRESS)
    check.add_argument(
        "--mode",
        choices=("auto", "db", "csv", "csv-or-db"),
        default="auto",
        help="Validation gate. auto uses DB when available, otherwise CSV.",
    )
    check.set_defaults(func=command_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (FileNotFoundError, ValueError, sqlite3.Error) as exc:
        print(f"ERROR\t{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
