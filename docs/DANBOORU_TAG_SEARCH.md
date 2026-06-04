# Danbooru tag search helper

This pack keeps image prompt slots fail-closed against the root `danbooru_tag.csv`: generation prompts should still use only canonical tags or aliases present in that file unless a workflow README explicitly says otherwise.

`./scripts/danbooru_tag_search.py` upgrades the discovery step before prompt authoring. It borrows the lightweight normalization/search pattern from `cksdnfas/danbooru-db-viewer` commit `147e1a605d9e9e35a28482e6a77f2ae840a0ef64`:

- normalize user text by trimming, lowercasing, and replacing spaces with underscores;
- search canonical tags and aliases;
- rank exact matches before alias, prefix, substring, token, lightweight stem-token, and partial-token suggestions;
- optionally enrich results with read-only `tags.category_name` and `tags.post_count` when a `danbooru-taxonomy.sqlite` database from the viewer project is available.

## CSV-only search

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
python scripts/danbooru_tag_search.py check "red border, train station"
```

Exit code:

- `0`: every token resolves to a CSV tag/alias.
- `1`: at least one token is missing; suggestions may be printed.
- `2`: input/CSV/SQLite error.

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

The helper opens SQLite with `mode=ro` and `PRAGMA query_only = ON`, ignores deprecated rows, and adds `category`/`post_count` columns. This metadata is advisory for search/rationale only; it does not expand the local CSV validation gate.

## Intended VN workflow use

1. Search candidate tags with this helper.
2. Prefer `exact`/`alias`/`prefix` results over weak partial-token suggestions.
3. Run `check` on the final comma-separated prompt slot.
4. Record rationale in metadata (`tag_rationale`, `negative_rationale`, etc.) when prompt changes are made after semantic misses.
5. Keep the runner dumb: it validates and records; the agent/human chooses tags.
