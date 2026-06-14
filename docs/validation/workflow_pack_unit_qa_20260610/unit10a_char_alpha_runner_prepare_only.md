# Unit 10A char_alpha runner / prepare-only preflight — 2026-06-11

## Purpose

Continue the broad character workflow automation audit after Unit 10.

Scope:

```text
workflow: char_alpha
focus: transparent/dialogue sprite alpha-cutout preflight
mode: automation audit, not production sprite work
source: generic neutral char_base fixture
promotion: forbidden
live generation: not required for this unit
```

This unit intentionally does **not** optimize any named character. It only adds the missing automation bridge for the transparent sprite workflow.

## Why char_alpha first

`char_alpha` was prioritized before `char_expression` because:

```text
- it is source-image transformation, not creative prompt generation
- it is required before VN dialogue sprites can be considered production-ready
- it is simpler than YOLO/SAM/inpaint expression generation
- it is reusable across future games
```

## Implementation

### New runner

Added:

```text
E:/workspace/vn-automation-toolkit/tools/run_char_alpha_smoke.py
```

Supported inputs:

```text
--source-image <project-confined image>
--source-metadata <project-confined metadata.json containing candidate_copies/output_paths>
```

Exactly one of the two is required.

Supported mode:

```text
--prepare-only
--out-metadata <project-confined output metadata path>
```

Runner behavior:

```text
1. Load selected project contract.
2. Resolve source image from --source-image or first usable image in --source-metadata.
3. Refuse source paths outside selected project root.
4. Stage source image into ComfyUI input root.
   - If contract has comfyui_input_root, use it.
   - Otherwise fallback to docs/automation/comfyui_input/ under project root.
5. Copy canonical char_alpha workflow into run directory as patched workflow.
6. Patch LoadImage.inputs.image to staged source filename.
7. Patch SaveImage.inputs.filename_prefix to hermes_vn_char_alpha/<run_id>.
8. Write metadata recording source/staged/workflow/provenance.
9. In prepare-only, do not submit to ComfyUI.
```

Metadata records:

```text
run_id
asset_id
scene_id
description
asset_type = transparent_sprite
workflow_id = char_alpha
workflow_path
workflow_sha256
patched_workflow_path
source_image
source_metadata
source_run_id
staged_source_image
comfyui_input_root
filename_prefix
prompt_policy = no_prompt_or_minimal; source-image alpha cutout only
output_paths
candidate_copies
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
char_alpha -> tools/run_char_alpha_smoke.py
```

Queue now passes source metadata/image for `char_alpha`:

```text
source_char_base_metadata or source_metadata -> --source-metadata
source_image -> --source-image
```

If neither is present:

```text
status: failed_missing_source_metadata
reason: char_alpha_requires_source_metadata_or_source_image
```

## Tests

Added:

```text
E:/workspace/vn-automation-toolkit/tests/test_char_alpha_routing.py
```

Coverage:

```text
- prepare-only patches LoadImage and SaveImage and writes metadata
- source image is staged into ComfyUI input root
- external source images are refused
- source metadata resolves first usable candidate_copies/output_paths image
```

Updated:

```text
E:/workspace/vn-automation-toolkit/tests/test_level4_generation_orchestrator.py
```

Coverage:

```text
- generation queue passes --source-metadata to char_alpha runner
```

Verified:

```text
python -m pytest tests/test_char_alpha_routing.py \
  tests/test_level4_generation_orchestrator.py::test_generation_orchestrator_passes_char_alpha_source_metadata -q

4 passed in 0.62s

python -m pytest -q

142 passed in 41.42s
```

## Active-project prepare-only evidence

Source fixture:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png
```

Command:

```bash
python tools/run_char_alpha_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id alpha_unit10a_fixture_neutral_schoolgirl \
  --scene-id workflow_pack_unit10a \
  --description 'Automation audit fixture: char_alpha prepare-only from neutral char_base source' \
  --source-image E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png \
  --prepare-only
```

Observed output:

```text
RUN_ID char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639
WORKFLOW E:\workspace\comfyui-game-asset-workflows\char_alpha\char_alpha_workflow_api.json
SOURCE_IMAGE E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\generated_candidates\characters\char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248\candidate_01.png
STAGED_SOURCE_IMAGE E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\comfyui_input\char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639_source.png
PATCHED_WORKFLOW E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\generation_runs\char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639\char_alpha_patched_workflow_api.json
PROMPT_POLICY no_prompt_or_minimal; source-image alpha cutout only
PREPARE_ONLY
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639/metadata.json
```

Patched workflow:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639/char_alpha_patched_workflow_api.json
```

Patch verification:

```text
LoadImage.inputs.image = char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639_source.png
SaveImage.inputs.filename_prefix = hermes_vn_char_alpha/char_alpha_alpha_unit10a_fixture_neutral_schoolgirl_20260611_210639
```

Result:

```text
PASS: char_alpha can now be preflighted from a generic char_base fixture without live generation or production promotion.
```

## README update

Updated:

```text
E:/workspace/comfyui-game-asset-workflows/char_alpha/README.md
```

Added:

```text
- runner command examples
- source-image/source-metadata contract
- project confinement rule
- ComfyUI input staging rule
- prepare-only behavior
- promotion gate reminder
```

## Current maturity after Unit 10A

| Area | Before | After Unit 10A |
| --- | --- | --- |
| char_alpha runner | missing | present |
| char_alpha prepare-only | missing | present |
| char_alpha queue runner | missing | present |
| source image confinement | manual/readme only | test-covered |
| input staging | manual | runner-managed |
| live alpha generation | possible through runner but not exercised in this unit | pending visual/file QA unit |
| promotion | forbidden without approval | unchanged |

## Remaining work

Next priority:

```text
Unit 10B — char_expression runner/prepare-only preflight
```

Then:

```text
Unit 10C — scene_event_cg canonical prompt policy cleanup
```

Potential follow-up after 10B/10C:

```text
Unit 10D — char_alpha live smoke + alpha visual QA using generic fixture
```

This should remain fixture-only unless the user explicitly requests production sprite work.
