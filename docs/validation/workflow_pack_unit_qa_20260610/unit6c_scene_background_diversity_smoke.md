# Unit 6C Scene Background Diversity Smoke — 2026-06-11

## Purpose

After Unit 6B accepted the `tag segment + semantic/style prompt segment` correction, run two additional scene_background candidates before moving to prop QA.

## Candidate A — fantasy noble library

Intent:

```text
empty fantasy noble library / private mansion study, dark romantic interior, tall bookshelves, dark wood, candlelit
```

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6c_fantasy_library_smoke_20260611_004407/candidate_01.png
```

Run:

```text
prompt_id: 136f83ab-0b9d-4c92-bea6-4d005f0b6ff3
seed: 360610603
size: 1024x576
```

Agent visual QA:

```text
- Semantic fit is strong: reads as a noble/gothic private library or study.
- Bookshelves, arched windows, dark wood, candle/candelabra lighting are present.
- No obvious humans/faces/characters.
- No readable text/logos/watermarks visible; book spines are non-readable texture.
- Lower third is mostly polished floor and should be dialogue-box-safe.
```

## Candidate B — mystical rainy forest

Intent:

```text
empty mystical forest path after rain, dark romantic fantasy woodland, wet leaves, fog, blue-grey atmosphere
```

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6c_mystic_rain_forest_smoke_20260611_004413/candidate_01.png
```

Run:

```text
prompt_id: f46616f6-3674-40cd-be86-b7f0b040587f
seed: 360610604
size: 1024x576
```

Agent visual QA:

```text
- Semantic fit is mostly strong: empty foggy forest / wet woodland background.
- No obvious humans/faces/characters.
- No readable text/logos/watermarks visible.
- Lower third contains water/reflections and banks; likely usable but may be visually busier than the library for dialogue-box overlay.
- It reads more as a river/stream through forest than a distinct path. If a "walkable forest path" is required, prompt should emphasize trail/path and reduce stream/river cues.
```

## Automation conclusion

The semantic/style prompt correction generalizes beyond the hallway case. It works well for noble library interiors and produces a plausible empty forest background, with the caveat that outdoor prompts may need stricter path-vs-stream wording when a walkable path is required.
