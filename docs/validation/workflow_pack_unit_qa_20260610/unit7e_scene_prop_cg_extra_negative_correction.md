# Unit 7E Scene Prop CG Extra-Negative Corrective Smoke — 2026-06-11

## Purpose

Correct Unit 7D neutral prop issues with per-item `extra_negative_prompt` support.

## Automation update

`run_scene_prop_cg_smoke.py` now supports:

```text
prompt_slots.extra_negative_prompt
```

This is appended to the live negative prompt for item-specific failure controls.

## Candidate A — single old key

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7e_single_old_key_smoke_20260611_011250/candidate_01.png
```

Run:

```text
prompt_id: 87695bad-6b33-406b-bb42-ad98c702b138
seed: 360610706
size: 1024x576
```

Extra negative:

```text
lock, box, book, stack, extra objects, multiple objects, jewelry, pendant
```

Agent visual QA:

```text
- Strong improvement over Unit 7D key.
- Reads as one old/brass key on wooden table.
- No lockbox/book/large extra prop.
- No humans/hands/faces.
- No readable text/logos.
- Clean enough as a generic VN item/evidence cut-in candidate.
```

## Candidate B — logo-free blank smartphone

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7e_logo_free_smartphone_smoke_20260611_011300/candidate_01.png
```

Run:

```text
prompt_id: cfff1a84-689b-4a89-9fe9-f6d21c1731da
seed: 360610707
size: 1024x576
```

Extra negative:

```text
logo, icon, app icon, apple logo, user interface, letters, numbers, text, status bar, notification, symbol
```

Agent visual QA:

```text
- Strong improvement over Unit 7D smartphone.
- Screen is black/blank with no visible logo, fake app UI, readable text, status bar, or icons.
- No humans/hands/faces.
- Smartphone is the main focus and usable as modern item/evidence cut-in.
- Remaining issue: glass/cup and background objects appear beside the phone, so this is not a strict isolated single-object prop. It is acceptable if contextual desk props are allowed; stricter isolation would need more negative controls like cup, glass, drink, background object.
```

## Automation conclusion

`scene_prop_cg` should use three layers:

```text
1. SQLite-validated structural tags: item/material/placement
2. semantic_prompt + style_prompt for story identity and target shape
3. extra_negative_prompt for item-specific drift control
```

Known caveat:

```text
Text-prone props: document/book/phone screen need strict no-text/no-UI handling and may still require overlay/post-edit.
Strict single-object isolation may need per-item negatives for common co-occurring objects.
```
