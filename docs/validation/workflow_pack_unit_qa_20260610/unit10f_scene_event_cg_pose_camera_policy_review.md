# Unit 10F scene_event_cg pose/camera policy review — 2026-06-11

## Purpose

Continue broad character/event-CG workflow automation audit after Unit 10E.

Scope:

```text
workflow: scene_event_cg
focus: decide whether to redesign pose/camera prompt policy now
mode: policy review + documentation cleanup
live generation: not required
promotion: forbidden
```

## Background

Unit 10C fixed a fixed-wrapper self-conflict by removing `depth_of_field` from the canonical negative prompt.

Remaining issue:

```text
scene_event_cg README still contained old cinematic candidate recipes that included tags now intentionally reserved in canonical negative.
```

Examples:

```text
cowboy_shot
upper_body
standing
facing_viewer
looking_at_viewer
from_above
from_below
dutch_angle
```

The runner now fails closed if agent-authored positive placeholders overlap with canonical negative prompt. Therefore the old cinematic blocks were no longer executable as current `prompt_slots.scene_context` examples.

## Current canonical negative reserved set

Still intentionally reserved:

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

These are reserved to prevent placeholder-driven pose/camera/body-framing drift in the conservative no-ref event-CG route.

## Decision

Unit 10F decision:

```text
Do not redesign pose/camera policy immediately.
Keep current fail-closed conservative route.
Document old cinematic pose/camera presets as disabled historical examples.
```

Reasoning:

```text
- Current runner behavior is internally consistent and test-covered.
- Safe fixture prepare-only already passes with non-conflicting scene_context tags.
- Re-enabling pose/camera tags requires a deliberate policy choice, not a quick negative-prompt edit.
- Prompt-only pose/camera control may reintroduce identity/anatomy/composition drift.
```

## README update

Updated:

```text
E:/workspace/comfyui-game-asset-workflows/scene_event_cg/README.md
```

Changed section:

```text
#### 4. Cinematic pose/camera policy status
```

Clarified:

```text
- old cinematic presets are disabled historical examples
- do not paste them into prompt_slots.scene_context under current policy
- current safe scene_context should use non-conflicting setting/mood/time/lighting tags
- production pose/camera control requires a separate redesign unit
```

Current safe scene_context examples:

```text
indoors
auditorium
stage
curtains
spotlight
podium
presentation
night
sunset
window
sunlight
```

## Future redesign options

If production event CGs need explicit pose/camera control, choose one of these deliberately:

```text
1. Remove selected pose/camera tags from canonical negative and allow them as positive slots.
2. Split prompt slots into setting_context and pose_camera_context with separate allow/deny lists.
3. Add a dedicated pose/control workflow instead of relying on prompt-only tags.
4. Keep no-ref event CG conservative and use Ren'Py staging/character sprites for pose-specific beats.
```

## Outcome

```text
PASS: policy is now explicit and no longer presents disabled pose/camera tags as current safe recipes.
```

No new generation was required for this unit.

## Verification expectation

Existing test coverage remains responsible for enforcing:

```text
- positive placeholder vs canonical negative conflict fail-closed
- fixed wrapper positive vs negative conflict fail-closed
- current canonical wrapper has no depth_of_field conflict
```
