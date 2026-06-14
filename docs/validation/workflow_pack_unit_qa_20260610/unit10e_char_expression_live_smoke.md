# Unit 10E char_expression live smoke + face/expression QA — 2026-06-11

## Purpose

Continue broad character workflow automation audit after Unit 10D.

Scope:

```text
workflow: char_expression
mode: live ComfyUI smoke, not production expression work
source: generic Unit 9A neutral schoolgirl char_base fixture
prompt: happy/smile/open_mouth expression fixture
promotion: forbidden
```

## Source fixture

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png
```

## Prompt slots

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/expr_unit10e_fixture_neutral_happy_live.json
```

Prompt slots:

```json
{
  "identity_tags": ["medium_hair", "straight_hair", "blunt_bangs", "brown_hair", "brown_eyes"],
  "expression_positive": ["happy", "smile", "open_mouth"],
  "expression_negative": ["sad", "angry", "crying", "tears", "expressionless"]
}
```

## Live run

Command:

```bash
python tools/run_char_expression_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id expr_unit10e_fixture_neutral_happy_live \
  --scene-id workflow_pack_unit10e \
  --description 'Automation audit fixture: char_expression live smoke from neutral char_base source' \
  --source-image E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png \
  --prompt-slots E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/expr_unit10e_fixture_neutral_happy_live.json \
  --seed 719251301 \
  --denoise 0.4
```

Observed:

```text
RUN_ID char_expression_expr_unit10e_fixture_neutral_happy_live_20260611_223902
ENDPOINT http://127.0.0.1:8000
prompt_submit_status 200
PROMPT_ID 5364edd2-fba3-4c58-8872-59cc006f245f
OUTPUT_PATH C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_char_expression\char_expression_expr_unit10e_fixture_neutral_happy_live_20260611_223902_happy_00001_.png exists= True
CANDIDATE_COPY E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\generated_candidates\characters\char_expression_expr_unit10e_fixture_neutral_happy_live_20260611_223902\candidate_01.png
GENERATION_OUTPUT_VERIFIED
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_expression_expr_unit10e_fixture_neutral_happy_live_20260611_223902/metadata.json
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_expression_expr_unit10e_fixture_neutral_happy_live_20260611_223902/candidate_01.png
```

Source/candidate comparison sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_expression_expr_unit10e_fixture_neutral_happy_live_20260611_223902/unit10e_expression_source_compare_sheet.jpg
```

QA report:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10e_char_expression_live_smoke/unit10e_char_expression_file_visual_qa_pass_with_caveats.json
```

## File QA

```text
mode: RGB
size: 1152 x 1536
diff_mean_rgb vs source: [0.22, 0.24, 0.24]
diff_rms_rgb vs source: [3.38, 3.44, 3.43]
```

Interpretation:

```text
PASS: output is a real verified image copied from ComfyUI history/output.
The diff is localized and small globally, which is expected for face-expression inpaint/composite.
```

## Visual QA

Result:

```text
PASS with caveats
```

Observed:

```text
- target expression changed from neutral to happy/smile/open_mouth
- body/outfit/hair silhouette mostly preserved
- no obvious mask seam at review scale
- no major platform/node artifacts
- face/eye style shifts slightly
- eye color becomes more amber/orange than source brown
- mild identity drift exists, so this is not production-approved
```

Promotion:

```text
not_promoted_pending_owner_approval
```

This is an automation fixture only.

## Outcome

```text
PASS: char_expression live route works end-to-end with the active ComfyUI stack.
```

The workflow validated:

```text
- source image staging into contract comfyui_input_root
- prompt slot validation through SQLite taxonomy
- YOLO/SAM/mask/inpaint/composite node path availability
- ControlNet/repaint path availability
- output verification via /history and filesystem
- candidate copy and metadata recording
```

## Technical caveat / future tuning

For production-grade expression sets, the current `denoise=0.4` successfully changes expression but may introduce mild face/eye identity drift.

Future production tuning candidates:

```text
- lower denoise sweep, e.g. 0.25 / 0.3 / 0.35
- stronger identity-preservation prompt slots
- source-seed handoff if the expression workflow gains seed policy from char_base metadata
- face crop/mask expansion review per expression intensity
```

Do not apply those production tuning changes during automation-audit mode unless explicitly requested.
