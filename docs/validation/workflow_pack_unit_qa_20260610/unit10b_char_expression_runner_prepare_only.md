# Unit 10B char_expression runner / prepare-only preflight — 2026-06-11

## Purpose

Continue the broad character workflow automation audit after Unit 10A.

Scope:

```text
workflow: char_expression
focus: expression variant preflight from an existing source character image
mode: automation audit, not production expression work
source: generic neutral char_base fixture
promotion: forbidden
live generation: not required for this unit
```

This unit intentionally does **not** optimize any named character's expression set. It adds the missing automation bridge for expression workflow preflight.

## Implementation

### New runner

Added:

```text
E:/workspace/vn-automation-toolkit/tools/run_char_expression_smoke.py
```

Supported source inputs:

```text
--source-image <project-confined image>
--source-metadata <project-confined metadata.json containing candidate_copies/output_paths>
```

Exactly one of the two is required.

Required prompt input:

```text
--prompt-slots <project/docs/production/prompt_slots/*.json>
```

Required prompt slots:

```json
{
  "prompt_slots": {
    "identity_tags": ["medium_hair", "brown_hair"],
    "expression_positive": ["happy", "smile"],
    "expression_negative": ["sad", "angry"]
  }
}
```

Runner behavior:

```text
1. Load selected project contract.
2. Resolve source image from --source-image or first usable image in --source-metadata.
3. Refuse source paths outside selected project root.
4. Require agent-authored prompt slots under docs/production/prompt_slots/.
5. Validate identity/expression positive/expression negative tags through workflow-pack Danbooru SQLite taxonomy.
6. Stage source image into ComfyUI input root.
7. Copy canonical char_expression workflow into run directory as patched workflow.
8. Patch LoadImage.inputs.image to staged source filename.
9. Patch CLIP positive/negative prompt nodes.
10. Patch KSampler seed/denoise.
11. Patch SaveImage filename_prefix.
12. In prepare-only, write metadata without submitting to ComfyUI.
```

Patched nodes:

```text
1.inputs.image
6.inputs.text
7.inputs.text
13.inputs.seed
13.inputs.denoise
19.inputs.filename_prefix
```

Metadata records:

```text
run_id
asset_id
scene_id
description
asset_type = character_expression
workflow_id = char_expression
expression_id
workflow_path
workflow_sha256
patched_workflow_path
source_image
source_metadata
source_run_id
staged_source_image
prompt_source
prompt_slots_path
prompt_slots
prompt_policy
taxonomy_source
taxonomy_db_path
taxonomy_placeholder_tags
identity_tags
expression_positive
expression_negative
positive_prompt
negative_prompt
seed
denoise
filename_prefix
qa_status
promotion_status
prepare_only
```

## Queue integration

Changed:

```text
E:/workspace/vn-automation-toolkit/tools/run_generation_queue.py
```

Added default runner:

```text
char_expression -> tools/run_char_expression_smoke.py
```

Added prompt-sensitive workflow classification:

```text
char_expression requires prompt_slots
```

Queue now passes source metadata/image for both `char_alpha` and `char_expression`:

```text
source_char_base_metadata or source_metadata -> --source-metadata
source_image -> --source-image
```

If neither source is present:

```text
status: failed_missing_source_metadata
reason: char_expression_requires_source_metadata_or_source_image
```

## Tests

Added:

```text
E:/workspace/vn-automation-toolkit/tests/test_char_expression_routing.py
```

Coverage:

```text
- prepare-only patches source image, prompts, seed, filename prefix, and metadata
- missing prompt slots fail closed with UNROUTED_CHAR_EXPRESSION
- expression prompt tags validate through SQLite taxonomy
```

Updated:

```text
E:/workspace/vn-automation-toolkit/tests/test_level4_generation_orchestrator.py
```

Coverage:

```text
- generation queue passes --prompt-slots and --source-metadata to char_expression runner
```

Verified:

```text
python -m pytest tests/test_char_alpha_routing.py \
  tests/test_char_expression_routing.py \
  tests/test_level4_generation_orchestrator.py::test_generation_orchestrator_passes_char_alpha_source_metadata \
  tests/test_level4_generation_orchestrator.py::test_generation_orchestrator_passes_char_expression_prompt_slots_and_source_metadata -q

7 passed in 1.16s

python -m pytest -q

145 passed in 42.00s
```

## Active-project prepare-only evidence

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/expr_unit10b_fixture_neutral_happy.json
```

Source fixture:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png
```

Command:

```bash
python tools/run_char_expression_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id expr_unit10b_fixture_neutral_happy \
  --scene-id workflow_pack_unit10b \
  --description 'Automation audit fixture: char_expression prepare-only from neutral char_base source' \
  --source-image E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png \
  --prompt-slots E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/expr_unit10b_fixture_neutral_happy.json \
  --seed 424242 \
  --prepare-only
```

Observed output:

```text
RUN_ID char_expression_expr_unit10b_fixture_neutral_happy_20260611_211419
WORKFLOW E:\workspace\comfyui-game-asset-workflows\char_expression\char_expression_workflow_api.json
SOURCE_IMAGE E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\generated_candidates\characters\char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248\candidate_01.png
STAGED_SOURCE_IMAGE E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\comfyui_input\char_expression_expr_unit10b_fixture_neutral_happy_20260611_211419_source.png
PROMPT_POLICY README wrapper + agent-authored SQLite-verified expression prompt slots only
TAXONOMY_SOURCE db
SEED 424242
DENOISE 0.4
PREPARE_ONLY
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_expression_expr_unit10b_fixture_neutral_happy_20260611_211419/metadata.json
```

Patched workflow:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_expression_expr_unit10b_fixture_neutral_happy_20260611_211419/char_expression_patched_workflow_api.json
```

Patch verification:

```text
LoadImage.inputs.image = char_expression_expr_unit10b_fixture_neutral_happy_20260611_211419_source.png
positive contains identity tags + happy/smile/open_mouth
negative contains sad/angry/crying/tears/expressionless
KSampler.seed = 424242
SaveImage.filename_prefix = hermes_vn_char_expression/char_expression_expr_unit10b_fixture_neutral_happy_20260611_211419_happy
```

Result:

```text
PASS: char_expression can now be preflighted from a generic char_base fixture using SQLite-verified expression prompt slots, without live generation or production promotion.
```

## README update

Updated:

```text
E:/workspace/comfyui-game-asset-workflows/char_expression/README.md
```

Added:

```text
- runner command examples
- source-image/source-metadata contract
- prompt_slots contract
- SQLite validation rule
- ComfyUI input staging rule
- prepare-only behavior
- QA/promotion gate reminder
```

## Current maturity after Unit 10B

| Area | Before | After Unit 10B |
| --- | --- | --- |
| char_expression runner | missing | present |
| char_expression prepare-only | missing | present |
| char_expression queue runner | missing | present |
| prompt-slot fail-closed | readme only | runner/test covered |
| source image confinement | manual/readme only | runner/test covered |
| taxonomy validation | readme only | runner/test covered |
| live expression generation | possible through runner but not exercised | pending platform/model/visual QA unit |
| promotion | forbidden without approval | unchanged |

## Remaining work

Next priority:

```text
Unit 10C — scene_event_cg canonical prompt policy cleanup
```

Potential follow-up after Unit 10C:

```text
Unit 10D — char_alpha live smoke + alpha visual QA using generic fixture
Unit 10E — char_expression live smoke + face-mask/platform preflight using generic fixture
```

Keep these fixture-only unless the user explicitly requests production character work.
