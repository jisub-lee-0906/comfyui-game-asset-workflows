# Unit 10D char_alpha live smoke + alpha QA — 2026-06-11

## Purpose

Continue broad character workflow automation audit after Unit 10A/10B/10C.

Scope:

```text
workflow: char_alpha
mode: live ComfyUI smoke, not production sprite work
source: generic Unit 9A neutral schoolgirl char_base fixture
promotion: forbidden
```

## Source fixture

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png
```

## First live-run blocker

Initial live run failed:

```text
/prompt HTTP 400
LoadImage image - Invalid image file: char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_221952_source.png
```

Cause:

```text
project_contract lacked comfyui_input_root.
runner fallback staged source image under project/docs/automation/comfyui_input,
but live ComfyUI LoadImage resolves files under the actual ComfyUI input directory.
```

Verified actual input root:

```text
C:/Users/Desktop/Documents/ComfyUI/input
```

Updated active project contract:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/project_contract.json
```

Added/updated:

```json
{
  "comfyui_input_root": "C:/Users/Desktop/Documents/ComfyUI/input",
  "automation": {
    "toolkit_handoff_policy": {
      "prompt_slot_runners": [
        "char_base",
        "char_expression",
        "char_alpha",
        "scene_background",
        "scene_prop_cg",
        "scene_event_cg",
        "ui_system_alert_frame",
        "audio_bgm_with_sfx"
      ],
      "char_alpha_live_requires_comfyui_input_root": true,
      "char_expression_requires_prompt_slots_and_source_metadata": true,
      "updated_at": "2026-06-11"
    }
  }
}
```

## Successful live run

Command:

```bash
python tools/run_char_alpha_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id alpha_unit10d_fixture_neutral_schoolgirl_live \
  --scene-id workflow_pack_unit10d \
  --description 'Automation audit fixture: char_alpha live smoke from neutral char_base source' \
  --source-image E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png
```

Observed output:

```text
RUN_ID char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_222059
ENDPOINT http://127.0.0.1:8000
prompt_submit_status 200
PROMPT_ID ab5c8a85-f6a1-45f3-b297-25d633e3ca73
OUTPUT_PATH C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_char_alpha\char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_222059_00001_.png exists= True
CANDIDATE_COPY E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\generated_candidates\characters\char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_222059\candidate_01.png
GENERATION_OUTPUT_VERIFIED
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_222059/metadata.json
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_222059/candidate_01.png
```

Edge QA sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_alpha_alpha_unit10d_fixture_neutral_schoolgirl_live_20260611_222059/unit10d_alpha_edge_qa_sheet.jpg
```

QA report:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10d_char_alpha_live_smoke/unit10d_char_alpha_file_visual_qa_pass.json
```

## File QA

```text
mode: RGBA
size: 1152 x 1536
alpha_bbox: (224, 31, 896, 1536)
transparent_pct: 58.73
opaque_pct: 40.14
partial_alpha_pct: 1.13
```

Interpretation:

```text
PASS: candidate has real alpha channel and usable transparent cutout.
```

## Visual QA

Result:

```text
PASS with caveats
```

Observed:

```text
- single character preserved
- source identity/outfit preserved
- background removed
- no major missing body/hair parts
- no major cutout holes
- thin gray/dark fringe remains around outer hair/cardigan edges, especially visible on dark red/blue backgrounds
- lower body crop is inherited from source fixture, not caused by alpha workflow
```

Promotion:

```text
not_promoted_pending_owner_approval
```

This is an automation fixture only.

## Outcome

```text
PASS: char_alpha live route now works end-to-end after contract input-root repair.
```

## Follow-ups

Recommended next unit:

```text
Unit 10E — char_expression live smoke + face-mask/platform QA using generic fixture
```

Potential technical debt:

```text
- Ensure future project contracts always include comfyui_input_root when workflows use LoadImage.
- Consider adding a contract/init validator that warns when workflow pack has LoadImage workflows but project_contract lacks comfyui_input_root.
```
