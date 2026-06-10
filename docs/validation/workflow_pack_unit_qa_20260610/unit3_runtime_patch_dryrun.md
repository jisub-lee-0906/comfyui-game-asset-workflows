# Unit 3 — Runtime Patch Dry-run QA

## Scope

No generation was run and `/prompt` was not called. This unit only writes runtime workflow copies and verifies patch safety.

- Endpoint locked for later generation: `http://127.0.0.1:8000`
- Runtime payload root: `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads`

## Summary

- Workflows patched: **8**
- Errors: **0**
- Warnings: **0**

## Per-workflow dry-run result

| workflow_id | changed fields | disallowed changes | unresolved placeholders | canonical unchanged | runtime path |
|---|---:|---:|---:|---|---|
| `char_base` | 6 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\char_base\char_base_unit3_dryrun_workflow_api.json` |
| `char_expression` | 6 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\char_expression\char_expression_unit3_dryrun_workflow_api.json` |
| `char_alpha` | 2 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\char_alpha\char_alpha_unit3_dryrun_workflow_api.json` |
| `scene_background` | 6 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\scene_background\scene_background_unit3_dryrun_workflow_api.json` |
| `scene_event_cg` | 6 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\scene_event_cg\scene_event_cg_unit3_dryrun_workflow_api.json` |
| `scene_prop_cg` | 6 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\scene_prop_cg\scene_prop_cg_unit3_dryrun_workflow_api.json` |
| `ui_system_alert_frame` | 6 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\ui_system_alert_frame\ui_system_alert_frame_unit3_dryrun_workflow_api.json` |
| `audio_bgm_with_sfx` | 8 | 0 | 0 | True | `docs\validation\workflow_pack_unit_qa_20260610\unit3_runtime_payloads\audio_bgm_with_sfx\audio_bgm_with_sfx_unit3_dryrun_workflow_api.json` |

## Errors

- None.

## Warnings

- None.

## User QA request

Please confirm whether these runtime patch dry-runs are acceptable before Unit 4. Unit 4 will be the first actual generation smoke, starting with the smallest audio SFX smoke unless you choose otherwise.
