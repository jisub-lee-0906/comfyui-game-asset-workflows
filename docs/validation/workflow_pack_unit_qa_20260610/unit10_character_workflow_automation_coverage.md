# Unit 10 character workflow automation coverage audit — 2026-06-11

## Purpose

Continue the broad VN project automation-level audit without focusing on a named character.

Scope:

```text
unit: Unit 10
focus: character workflow family automation coverage
workflows: char_base, char_expression, char_alpha, scene_event_cg handoff
mode: automation audit, not production asset work
named character optimization: forbidden
promotion: forbidden
generation: prepare-only / metadata-level unless required for coverage
```

This audit follows the scope-drift guard recorded in:

```text
E:/workspace/comfyui-game-asset-workflows/docs/validation/workflow_pack_unit_qa_20260610/automation_audit_scope_drift_guard.md
```

## Inventory

Character-family workflow pack folders currently observed:

| Workflow | README | API workflow | Toolkit runner | Prepare-only | Live generation runner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `char_base` | yes | yes | `tools/run_char_base_smoke.py` | yes | yes | mature smoke route |
| `char_expression` | yes | yes | no direct toolkit runner | no | no | coverage gap |
| `char_alpha` | yes | yes | no direct toolkit runner | no | no | coverage gap |
| `scene_event_cg` | yes | yes | `tools/run_scene_event_cg_smoke.py` | added in Unit 10 | yes | handoff route improved |

Generation queue default runner coverage:

```text
audio_bgm_with_sfx: yes
char_base: yes
scene_background: yes
scene_event_cg: yes
scene_prop_cg: yes
char_expression: no
char_alpha: no
```

## Existing strengths

### char_base

`char_base` is currently the strongest character-family automation route:

```text
- prompt-sensitive fail-closed routing
- agent-authored prompt_slots required
- SQLite taxonomy validation
- prepare-only metadata path
- source workflow copied to patched runtime file
- candidate copy path and metadata path recorded
- scene_event_cg_seed_to_reuse recorded for downstream handoff
- optional body_shape and negative_tags slots now supported
```

This is suitable as a cross-title fixture/source-character generator, with the caveat that approved production assets must not be auto-replaced by regenerated outputs.

### scene_event_cg before Unit 10

Already present before this unit:

```text
- runner existed
- agent-authored prompt_slots required
- SQLite taxonomy validation
- source char_base metadata required via --char-base-metadata
- stale hardcoded source fallback forbidden
- same seed reused from source char_base metadata unless explicitly overridden
- metadata records source_char_base_metadata and source_char_base_run_id
```

## Unit 10 implementation changes

### 1. scene_event_cg prepare-only support

Changed:

```text
E:/workspace/vn-automation-toolkit/tools/run_scene_event_cg_smoke.py
```

Added:

```text
--prepare-only
--out-metadata
```

Purpose:

```text
Validate event-CG prompt slots, source char_base metadata handoff, patched workflow construction, seed reuse, and metadata recording without submitting to ComfyUI.
```

This is important for broad automation audits because it avoids unnecessary production-like image generation while still proving the contract path.

Prepare-only metadata now records:

```text
asset_id
scene_id
description
workflow_id
workflow_path
workflow_sha256
patched_workflow_path
source_char_base_metadata
source_char_base_run_id
prompt_slots_path
prompt_slots
taxonomy_source
taxonomy_db_path
taxonomy_placeholder_tags
character_features_placeholder
outfit_detail_placeholder
scene_context_placeholder
positive_prompt
negative_prompt
negative_prompt_policy
seed
same_seed_as_char_base
qa_status = prepare_only
promotion_status = not_promoted
prepare_only = true
```

### 2. scene_event_cg positive/negative prompt conflict guard

During active-project prepare-only, the first generic fixture used:

```text
scene_context: indoors, standing, facing_viewer, looking_at_viewer
```

The runner built a valid prompt, but the canonical workflow negative prompt also contained:

```text
standing, sitting, facing_viewer, looking_at_viewer,
from_above, from_below, dutch_angle,
cowboy_shot, upper_body, full_body,
classroom, chalkboard, blackboard, whiteboard
```

This revealed a hidden prompt self-conflict: agent-authored positive placeholder tags could be simultaneously present in the canonical negative prompt.

Unit 10 added fail-closed validation:

```text
SCENE_EVENT_CG_PROMPT_CONFLICT:
positive placeholder tags also appear in canonical negative prompt
```

The guard checks only agent-authored placeholder tags against the canonical negative prompt. It does not currently rewrite the canonical workflow negative prompt.

### 3. scene_event_cg README warning

Changed:

```text
E:/workspace/comfyui-game-asset-workflows/scene_event_cg/README.md
```

Added a Unit 10 note warning that current canonical negative contains several composition/camera tags. Until the canonical negative policy is refactored, prompt slots should avoid putting those tags in `scene_context`.

Also recorded the remaining prompt-policy debt:

```text
README/model wrapper includes depth_of_field
canonical negative also includes depth_of_field
```

The new runner conflict guard catches placeholder conflicts, but the fixed wrapper-vs-negative `depth_of_field` contradiction remains a design debt for a later canonical prompt-policy cleanup.

## Active-project prepare-only evidence

### Conflict fixture — expected reject after guard

Prompt slots written:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10_fixture_neutral_character_handoff_smoke.json
```

Problem tags:

```text
standing
facing_viewer
looking_at_viewer
```

These conflict with the canonical negative prompt and are now refused by the runner.

### Safe fixture — prepare-only pass

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10_fixture_neutral_character_handoff_safe_smoke.json
```

Source char_base metadata fixture:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/metadata.json
```

Command shape:

```bash
python tools/run_scene_event_cg_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id event_unit10_fixture_neutral_character_handoff_safe_smoke \
  --scene-id workflow_pack_unit10 \
  --prompt-slots E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10_fixture_neutral_character_handoff_safe_smoke.json \
  --char-base-metadata E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/metadata.json \
  --prepare-only
```

Observed output:

```text
RUN_ID scene_event_cg_event_unit10_fixture_neutral_character_handoff_safe_smoke_20260611_204839
PROMPT_POLICY README positive exact; fill only brace placeholders with agent-authored SQLite-verified prompt slots; leave workflow negative unchanged
TAXONOMY_SOURCE db
TAXONOMY_PLACEHOLDER_TAGS medium_hair, straight_hair, blunt_bangs, brown_hair, brown_eyes, school_uniform, white_shirt, blue_skirt, indoors, auditorium, spotlight
SEED 260529202
PREPARE_ONLY
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10_fixture_neutral_character_handoff_safe_smoke_20260611_204839/metadata.json
```

Patched workflow:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10_fixture_neutral_character_handoff_safe_smoke_20260611_204839/scene_event_cg_patched_workflow_api.json
```

Result:

```text
PASS: scene_event_cg metadata/source/seed/prompt-slot preflight works without production generation.
```

## Tests added/updated

Changed:

```text
E:/workspace/vn-automation-toolkit/tests/test_prompt_slots_fail_closed.py
E:/workspace/vn-automation-toolkit/tests/test_scene_event_cg_routing.py
```

Coverage:

```text
- missing source char_base metadata still refused
- scene_event_cg prepare-only records source metadata and seed handoff
- positive placeholder tags conflicting with canonical negative are refused
- non-conflicting tags are accepted
```

Verified:

```text
python -m pytest tests/test_scene_event_cg_routing.py \
  tests/test_prompt_slots_fail_closed.py::test_scene_event_cg_refuses_missing_source_char_base_metadata \
  tests/test_prompt_slots_fail_closed.py::test_scene_event_cg_prepare_only_records_source_metadata_and_seed -q

4 passed in 0.34s

python -m pytest -q

138 passed in 40.76s
```

## Character workflow maturity matrix

| Area | Current maturity | Evidence | Main gap |
| --- | --- | --- | --- |
| char_base generation | high | runner + prepare-only + taxonomy + metadata + tests | visual quality remains owner/QA gated |
| approved char_base reuse | medium-high | metadata seed handoff exists | regenerated outputs must not replace approved assets automatically |
| scene_event_cg handoff | medium-high after Unit 10 | source metadata required + prepare-only added + conflict guard | canonical negative policy still has fixed-wrapper conflict (`depth_of_field`) |
| char_expression | low-medium | workflow README/API exists | no toolkit runner, no queue route, no prepare-only metadata contract |
| char_alpha / transparent sprite | low-medium | workflow README/API exists | no toolkit runner, no queue route, no prepare-only metadata contract |
| end-to-end character sprite route | incomplete | char_base source exists; expression/alpha workflows exist | missing automated runner bridge from base/expression to alpha/dialogue sprite |
| queue integration | partial | `run_generation_queue.py` routes char_base and scene_event_cg | char_expression/char_alpha skipped as no runner |

## Recommended next automation units

### Unit 10A — char_alpha runner preflight

Add a metadata-only / prepare-only runner for `char_alpha` first because it is mechanically simpler than expression inpaint.

Minimal contract:

```text
input: --source-image or --source-metadata
validate: path under project root or ComfyUI input staging policy
patch: char_alpha workflow LoadImage + filename_prefix
metadata: source image, source metadata, workflow sha, output target, alpha model defaults
prepare-only: yes
live generation: optional after preflight
```

Why first:

```text
Transparent sprite route is required before VN dialogue sprites can be considered production-ready.
char_alpha is source-image transformation, not creative prompt generation.
It is safer and more reusable cross-title than char_expression.
```

### Unit 10B — char_expression runner preflight

Add only after char_alpha preflight is stable.

Minimal contract:

```text
input: source char_base/source image metadata
emotion_id / expression_slot
positive expression tags or small fixed emotion policy
YOLO/SAM model availability check
prepare-only metadata
live smoke only with generic fixture
```

Known risk:

```text
Expression workflows use face detection + SAM/inpaint and are more platform/model-dependent.
This should not be treated as mature until a real preflight checks model files and node availability.
```

### Unit 10C — canonical scene_event_cg prompt policy cleanup

Resolve the fixed wrapper / canonical negative contradiction:

```text
positive wrapper contains depth_of_field
negative prompt also contains depth_of_field
```

Also consider whether composition tags belong in negative by default or should be prompt-shape-specific.

## Conclusion

Unit 10 improved the character workflow automation audit posture without drifting into named-character production.

Concrete improvements:

```text
- scene_event_cg can now be preflighted without live generation
- source char_base metadata/seed handoff is test-covered
- positive/negative placeholder conflicts now fail closed
- active-project safe handoff fixture passed prepare-only
```

Remaining broad gaps:

```text
- char_expression lacks toolkit runner/prepare-only
- char_alpha lacks toolkit runner/prepare-only
- scene_event_cg canonical prompt policy still needs cleanup around fixed-wrapper negatives
```
