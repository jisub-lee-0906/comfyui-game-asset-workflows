# Danbooru tag search helper

This pack keeps image prompt slots fail-closed against the local Danbooru taxonomy SQLite DB (`danbooru-taxonomy.release.sqlite`). The old CSV flow is retained only as an explicit compatibility mode for tests or external one-off inputs; the root CSV file is no longer required for normal pack operation.

`./scripts/danbooru_tag_search.py` is the primary local tag oracle before prompt authoring. It borrows the lightweight normalization/search pattern from `cksdnfas/danbooru-db-viewer`:

- normalize user text by trimming, lowercasing, and replacing spaces with underscores;
- search canonical tags and aliases;
- rank exact matches before alias, prefix, substring, token, lightweight stem-token, and partial-token suggestions;
- read-only SQLite validation/search against `tags.name`, `tags.normalized_name`, `tags.display_name`, and active `tag_aliases`;
- category/post-count evidence from `tags.category_name` and `tags.post_count`.

## Primary DB search/check with legacy CSV fallback

```bash
python scripts/danbooru_tag_search.py search "computer window" --limit 10
python scripts/danbooru_tag_search.py search "red border" --limit 10
python scripts/danbooru_tag_search.py search "bus interior" --limit 10
```

Output is tab-separated:

```text
tag	match	score	aliases
window_(computing)	alias	950	computer_window
```

## Prompt fail-closed check

Use `check` on a comma-separated prompt slot before placing it into a workflow README/runtime JSON:

```bash
python scripts/danbooru_tag_search.py check "red border, train station" --mode auto
```

Exit code:

- `0`: every token resolves to a SQLite tag/alias.
- `1`: at least one token is missing; suggestions may be printed.
- `2`: input/SQLite/legacy CSV error.

The command prints canonicalized OK tags and suggestions for missing tokens:

```text
OK	red_border	input=red_border
MISSING	train_station
SUGGEST	train_interior	partial_token	450
```

Do not automatically insert suggestions into generation prompts. Treat them as candidate evidence for the agent/human prompt-authoring step.

## Optional danbooru-db-viewer SQLite enrichment

If a viewer database exists, pass it explicitly:

```bash
python scripts/danbooru_tag_search.py search "red border" --db /path/to/danbooru-taxonomy.sqlite --limit 20
```

The helper opens SQLite with `mode=ro` and `PRAGMA query_only = ON`, ignores deprecated rows, and uses `category`/`post_count` columns as first-class prompt-selection evidence. With `--mode auto`, `check` validates against SQLite when the local DB is available; CSV is only an explicit legacy fallback.

## Intended VN workflow use

1. Search candidate tags with this helper.
2. Prefer `exact`/`alias`/`prefix` results over weak partial-token suggestions.
3. Run `check` on the final comma-separated prompt slot.
4. Record rationale in metadata (`tag_rationale`, `negative_rationale`, etc.) when prompt changes are made after semantic misses.
5. Keep the runner dumb: it validates and records; the agent/human chooses tags.
