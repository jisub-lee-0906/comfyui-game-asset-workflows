# Unit 10C scene_event_cg canonical prompt policy cleanup — 2026-06-11

## Purpose

Continue the broad character workflow automation audit after Unit 10A/10B.

Scope:

```text
workflow: scene_event_cg
focus: canonical positive/negative prompt self-conflict cleanup
mode: automation audit, not production event CG work
live generation: not required
promotion: forbidden
```

## Problem

Unit 10 found two prompt-conflict classes:

```text
1. Agent-authored positive placeholder tags could overlap with canonical negative prompt.
2. The fixed README/model positive wrapper itself contained depth_of_field while canonical negative also contained depth_of_field.
```

The first class had already been partially guarded by `assert_no_positive_negative_conflicts()`.

Unit 10C fixed the second class and made it test-covered.

## Changes

### Runner guard

Updated:

```text
E:/workspace/vn-automation-toolkit/tools/run_scene_event_cg_smoke.py
```

Added:

```python
assert_no_prompt_text_conflicts(positive_prompt, negative_prompt, context='prompt')
```

Behavior:

```text
- tokenizes comma-separated positive/negative prompt text
- normalizes spaces to underscores
- strips simple weight parentheses and :weight suffixes
- fails closed if any positive token also appears in negative
```

The runner now calls this after formatting the final scene_event_cg positive prompt and before writing/submitting the patched workflow.

### Canonical workflow cleanup

Updated:

```text
E:/workspace/comfyui-game-asset-workflows/scene_event_cg/scene_event_cg_workflow_api.json
```

Removed from canonical negative prompt:

```text
depth_of_field
```

Reason:

```text
README_POSITIVE intentionally keeps depth_of_field as a positive quality/composition cue.
Having the same tag in canonical negative created a fixed wrapper self-conflict.
```

Composition/camera/body-pose negative-reserved tags intentionally remain:

```text
cowboy_shot
upper_body
full_body
standing
sitting
facing_viewer
looking_at_viewer
from_above
from_below
dutch_angle
```

These remain to prevent placeholder-driven pose/camera drift. The runner will fail closed if agent-authored prompt_slots try to put them back into positive placeholders.

### Tests

Updated:

```text
E:/workspace/vn-automation-toolkit/tests/test_scene_event_cg_routing.py
```

Added/kept coverage:

```text
- placeholder positive tags conflict with canonical negative -> fail closed
- non-conflicting placeholder tags pass
- fixed positive/negative text conflict helper detects depth_of_field overlap
- canonical scene_event_cg README_POSITIVE + workflow negative now has no conflict
```

## Active-project prepare-only evidence

Command rerun after cleanup:

```bash
python tools/run_scene_event_cg_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id event_unit10_fixture_neutral_character_handoff_safe_smoke \
  --scene-id workflow_pack_unit10c \
  --description 'Automation audit fixture: Unit 10C canonical prompt conflict cleanup prepare-only' \
  --char-base-metadata E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/metadata.json \
  --prompt-slots E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10_fixture_neutral_character_handoff_safe_smoke.json \
  --prepare-only
```

Observed:

```text
RUN_ID scene_event_cg_event_unit10_fixture_neutral_character_handoff_safe_smoke_20260611_221309
TAXONOMY_SOURCE db
POSITIVE ... indoors, auditorium, spotlight, depth_of_field
NEGATIVE_UNCHANGED ... shadow, cowboy_shot, upper_body, full_body, standing, sitting, facing_viewer, looking_at_viewer, from_above, from_below, dutch_angle, classroom, chalkboard, blackboard, whiteboard
SEED 260529202
PREPARE_ONLY
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10_fixture_neutral_character_handoff_safe_smoke_20260611_221309/metadata.json
```

Patched workflow:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10_fixture_neutral_character_handoff_safe_smoke_20260611_221309/scene_event_cg_patched_workflow_api.json
```

Result:

```text
PASS: fixed wrapper depth_of_field no longer conflicts with canonical negative prompt, and safe fixture prepare-only succeeds.
```

## README update

Updated:

```text
E:/workspace/comfyui-game-asset-workflows/scene_event_cg/README.md
```

Clarified:

```text
- depth_of_field conflict has been resolved by removing it from canonical negative
- composition/camera/body-pose tags remain negative-reserved
- runner fails closed for positive/negative overlap
- old candidate sets containing reserved tags are unsafe historical presets unless policy changes deliberately
```

## Verification

Targeted:

```text
python -m pytest tests/test_scene_event_cg_routing.py \
  tests/test_prompt_slots_fail_closed.py::test_scene_event_cg_refuses_missing_source_char_base_metadata \
  tests/test_prompt_slots_fail_closed.py::test_scene_event_cg_prepare_only_records_source_metadata_and_seed -q

6 passed in 0.35s
```

Full suite:

```text
python -m pytest -q

147 passed in 42.66s
```

## Remaining follow-ups

Optional future units:

```text
Unit 10D — char_alpha live smoke + alpha visual/file QA using generic fixture
Unit 10E — char_expression live smoke + face-mask/platform QA using generic fixture
Unit 10F — scene_event_cg pose/camera policy redesign, if event CG needs positive pose control rather than negative-reserved defaults
```

Keep follow-ups fixture-only unless the user explicitly requests production character/event-CG work.
