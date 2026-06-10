# Unit 7D Scene Prop CG Neutral Diversity Smoke — 2026-06-11

## Purpose

Correct for title-specific bias by testing neutral, cross-genre prop CG generation.

## Candidate A — old brass key

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7d_old_brass_key_smoke_20260611_010752/candidate_01.png
```

Run:

```text
prompt_id: 55120dc8-0a37-4a16-9c0c-22af0745ac9e
seed: 360610704
size: 1024x576
```

Agent visual QA:

```text
- Key appears and has no text/logos.
- No humans/hands/faces.
- Problem: a large extra metal object/book/lockbox appears behind the key.
- This weakens the single-prop/object-focus criterion.
- Usable as an item cut-in only if extra object is acceptable as context; not clean single-object automation pass.
```

## Candidate B — blank smartphone

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7d_blank_smartphone_smoke_20260611_010803/candidate_01.png
```

Run:

```text
prompt_id: 9efb30ca-6425-463b-994b-a634345fba1f
seed: 360610705
size: 1024x576
```

Agent visual QA:

```text
- Smartphone shape and desk placement are good.
- No humans/hands/faces.
- Problem: screen contains an Apple-like logo/icon and small UI/text-like marks.
- This fails the blank screen / no fake UI / no logo criterion.
- Modern screen props behave like document props: text/UI/logo risk remains high.
```

## Additional automation finding

The first Unit 7D attempt also revealed stale README tag examples under current SQLite oracle:

```text
missing in current SQLite oracle: metallic_luster, blank_screen, black_screen, screen_turned_off
```

Corrected prompt slots now use only validated structural tags and carry non-taxonomy meaning through semantic/style prompt.

## Conclusion

```text
scene_prop_cg neutral diversity is not yet fully finalized.
Key: needs stricter single-object / no extra object guidance.
Smartphone: needs stronger no-logo/no-icon/no-UI handling; may require overlay/post-edit strategy for screen contents.
```
