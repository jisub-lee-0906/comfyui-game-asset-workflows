# Unit 1 — Workflow Pack Static Inventory QA

## Scope

Root: `E:\workspace\comfyui-game-asset-workflows`

No ComfyUI generation was run in this unit. This only checks the pack map and static files.

## Result

- Workflow count in index: **8**
- Errors: **0**
- Warnings: **0**
- Active old audio refs: **0**

## Canonical workflows

| # | workflow_id | folder | API | README | input image? | editable fields | node count |
|---:|---|---|---|---|---:|---:|---:|
| 1 | `char_base` | OK | OK | OK | False | 8 | 7 |
| 2 | `char_expression` | OK | OK | OK | True | 13 | 18 |
| 3 | `char_alpha` | OK | OK | OK | True | 2 | 3 |
| 4 | `scene_background` | OK | OK | OK | False | 8 | 8 |
| 5 | `scene_event_cg` | OK | OK | OK | False | 12 | 9 |
| 6 | `scene_prop_cg` | OK | OK | OK | False | 8 | 8 |
| 7 | `ui_system_alert_frame` | OK | OK | OK | False | 8 | 8 |
| 8 | `audio_bgm_with_sfx` | OK | OK | OK | False | 13 | 21 |

## Actual workflow-like folders found

- `audio_bgm_with_sfx`
- `char_alpha`
- `char_base`
- `char_expression`
- `scene_background`
- `scene_event_cg`
- `scene_prop_cg`
- `ui_system_alert_frame`

## Deleted/legacy audio workflow active-reference check

- PASS: no active refs to `audio_bgm_ace`, `audio_sfx_mmaudio`, or `run_audio_sfx_mmaudio`.

## Placeholder inventory for later runtime tests

- `char_base` / `char_base\README.md`: `{의상 디테일(의상 이름, 색상_의상종류)}`, `{의상 디테일}`, `{의상 이름, 색상_의상종류}`, `{캐릭터 특징(연령대, 헤어스타일, 머리길이, 머리색, 눈매, 눈색)}`
- `char_expression` / `char_expression\char_expression_workflow_api.json`: `TEMPLATE_CHARACTER_happy_composited`, `TEMPLATE_character_anchor_source.png`, `{감정표현}`, `{눈색}`, `{머리색}`, `{상극 감정표현}`, `{헤어 길이}`, `{헤어 스타일}`
- `char_expression` / `char_expression\README.md`: `{감정표현}`, `{상극 감정표현}`
- `char_alpha` / `char_alpha\char_alpha_workflow_api.json`: `TEMPLATE_CHARACTER_VARIANT_b1_ref1`, `TEMPLATE_source_image.png`
- `scene_background` / `scene_background\scene_background_workflow_api.json`: `{배경 테마 및 장소}`, `{시간대 및 분위기 태그}`
- `scene_background` / `scene_background\README.md`: `{배경 테마 및 장소}`, `{시간대 및 분위기 태그}`
- `scene_event_cg` / `scene_event_cg\README.md`: `{prompt_id}`, `{연령대, 헤어스타일, 눈매, 머리색, 눈색}`, `{의상 디테일(의상 이름, 색상_의상종류)}`, `{의상 이름, 색상_의상종류}`, `{캐릭터 특징(연령대, 헤어스타일, 눈매, 머리색, 눈색)}`
- `scene_prop_cg` / `scene_prop_cg\scene_prop_cg_workflow_api.json`: `{놓여있는 장소/배경}`, `{아이템 이름 및 형태}`, `{재질 및 질감 디테일}`
- `scene_prop_cg` / `scene_prop_cg\README.md`: `{놓여있는 장소/배경}`, `{아이템 이름 및 형태}`, `{재질 및 질감 디테일}`
- `audio_bgm_with_sfx` / `audio_bgm_with_sfx\README.md`: `{prompt_id}`

## Errors

- None.

## Warnings

- None.

## User QA request

Please confirm whether this canonical list and scope are correct before Unit 2. Unit 2 will check ComfyUI endpoint/object_info/model availability without generating assets.
