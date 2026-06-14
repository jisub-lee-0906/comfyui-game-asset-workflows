# Unit 8 UI System Alert Frame Smoke — 2026-06-11

## Purpose

Validate `ui_system_alert_frame` as a reusable textless VN system alert frame/backdrop workflow.

User directive applied:

```text
Find an intended-output direction first, reproduce it with the same direction, and only then reflect automation.
```

## Unit 8A — Prompt shape probe

Generated three same-seed variants:

```text
A. minimal red/gold border
B. minimal red/gold border + dark_background
C. canonical corner alert backdrop
```

Candidate files:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8a_ui_alert_prompt_shape_probe/unit8a_01_A_minimal_red_gold_border.png
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8a_ui_alert_prompt_shape_probe/unit8a_02_B_minimal_red_gold_border_dark_background.png
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8a_ui_alert_prompt_shape_probe/unit8a_03_C_canonical_corner_backdrop.png
```

QA:

```text
A/B: very clean and readable but too plain as a reusable VN alert frame.
C: textless pass, clear red/dark/corner VN alert backdrop identity, no characters/logos/text/symbols.
```

## Unit 8B — Reproduction check

Reused the winning canonical corner alert prompt with new seeds:

```text
260604913
260604914
260604915
```

Candidate files:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8b_ui_alert_corner_backdrop_repro/unit8b_01_corner_backdrop_seed_260604913.png
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8b_ui_alert_corner_backdrop_repro/unit8b_02_corner_backdrop_seed_260604914.png
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8b_ui_alert_corner_backdrop_repro/unit8b_03_corner_backdrop_seed_260604915.png
```

QA:

```text
260604913: strongest reusable candidate. Clean red/dark alert frame, no text/logo/characters, high overlay readability.
260604914: ornate border, usable but busier and more style-specific.
260604915: readable backdrop, but weaker frame identity.
```

## Korean overlay preview

Created Korean overlay previews and contact sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/unit8_overlay_preview/unit8_overlay_preview_contact_sheet.jpg
```

Overlay QA ranking:

```text
1. 8B seed 260604913 — best balance of clean frame identity and readability.
2. 8A-C seed 260604912 — stronger dark fantasy vibe.
3. 8B seed 260604914 — ornate/special-scene candidate.
4. 8B seed 260604915 — usable backdrop, weaker frame.
```

## Automation reflection

Added dedicated runner:

```text
E:/workspace/vn-automation-toolkit/tools/run_ui_system_alert_frame_smoke.py
```

Added tests:

```text
E:/workspace/vn-automation-toolkit/tests/test_ui_system_alert_frame_routing.py
```

Supported prompt shapes:

```text
minimal_red_gold_border
corner_alert_backdrop
```

Runner validates prompt-shape tags through the workflow pack Danbooru SQLite oracle and saves generated candidates plus metadata without promotion.

## Test results

```text
python -m pytest tests/test_ui_system_alert_frame_routing.py -q
2 passed in 0.03s

python -m pytest -q
133 passed in 35.40s
```

## Unit 8C — Final runner smoke

Command:

```bash
PROJECT='E:/workspace/renpy-project/sihanbu_villainess_badend'
python tools/run_ui_system_alert_frame_smoke.py \
  --project-root "$PROJECT" \
  --asset-id unit8c_ui_alert_runner_smoke \
  --prompt-shape corner_alert_backdrop \
  --seed 260604913
```

Output:

```text
RUN_ID ui_system_alert_frame_unit8c_ui_alert_runner_smoke_20260611_183948
PROMPT_SHAPE corner_alert_backdrop
TAXONOMY_SOURCE db
GENERATION_OUTPUT_VERIFIED
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/ui/ui_system_alert_frame_unit8c_ui_alert_runner_smoke_20260611_183948/candidate_01.png
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/ui_system_alert_frame_unit8c_ui_alert_runner_smoke_20260611_183948/metadata.json
```

Final QA:

```text
Pass as a reusable textless VN alert frame/backdrop candidate.
No baked/fake/readable text.
No logo/icon/symbol.
No characters/people/scenery.
Central area is dark and readable for later Korean overlay.
Frame identity is clean and less style-specific than ornate variants.
```

## Conclusion

`ui_system_alert_frame` is now automation-ready for smoke generation with the `corner_alert_backdrop` prompt shape.

Recommended default:

```text
prompt_shape=corner_alert_backdrop
seed=260604913 as known-clean smoke seed
```

Do not promote any generated UI asset to `game/images/ui/` without owner approval tied to exact metadata/run id.
