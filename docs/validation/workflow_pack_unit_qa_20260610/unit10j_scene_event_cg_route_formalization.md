# Unit 10J scene_event_cg route formalization — 2026-06-12

## Purpose

Implement the next engineering step from the final VN automation pipeline audit:

```text
Formalize the Unit 10I upper-body production event-CG direction in the canonical runner/pipeline instead of relying on the experimental framing runner.
```

## Scope

```text
workflow: scene_event_cg
component: E:/workspace/vn-automation-toolkit/tools/run_scene_event_cg_smoke.py
mode: prepare-only verified against active project
canonical workflow JSON: unchanged
promotion: none
```

## Implemented route modes

`run_scene_event_cg_smoke.py` now supports route modes:

```text
conservative
production_character
production_character_front
cut_in
```

Route behavior:

```text
conservative:
  removes no canonical negative tokens; broad fixture/smoke route

production_character:
  permits upper_body + looking_at_viewer by removing only those exact tokens from the runtime negative copy when requested in scene_context

production_character_front:
  permits upper_body + looking_at_viewer + facing_viewer for direct front-facing VN event CGs

cut_in:
  permits portrait + close-up + solo_focus for intentional face/cut-in shots
```

The runner still blocks unapproved conflicts. Example: `standing`, `sitting`, `cowboy_shot`, `from_above`, `from_below`, and `dutch_angle` remain blocked unless a future route explicitly allows them.

## Route mode sources

Route mode can be supplied by either:

```text
--route-mode production_character
```

or prompt slots:

```json
{
  "scene_event_route_mode": "production_character"
}
```

CLI value takes precedence over prompt-slot value. If neither is present, route mode defaults to:

```text
conservative
```

## Queue integration

`run_generation_queue.py` now forwards scene event route mode from resolved asset requests via any of these fields:

```text
scene_event_route_mode
event_cg_route_mode
route_mode
```

The queue appends:

```text
--route-mode <mode>
```

to the `scene_event_cg` runner command.

## Tests added/updated

Updated:

```text
E:/workspace/vn-automation-toolkit/tests/test_scene_event_cg_routing.py
E:/workspace/vn-automation-toolkit/tests/test_level4_generation_orchestrator.py
```

Coverage:

```text
- production_character removes upper_body/looking_at_viewer from runtime negative copy
- production_character keeps unapproved pose conflicts blocked
- cut_in permits portrait/close-up/solo_focus only
- route mode resolves from CLI first, then prompt_slots.scene_event_route_mode, then conservative
- generation queue forwards scene_event_route_mode to runner as --route-mode
```

## Active project prepare-only verification

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10j_production_upper_body_route.json
```

Prepare-only run:

```text
run_id: scene_event_cg_event_unit10j_production_upper_body_route_20260612_002412
route_mode: production_character
seed: 260529202
```

Verified effective behavior:

```text
positive contains upper_body: yes
positive contains looking_at_viewer: yes
negative original contains upper_body: yes
negative original contains looking_at_viewer: yes
negative effective contains upper_body: no
negative effective contains looking_at_viewer: no
negative effective still contains standing: yes
prepare_only: true
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10j_production_upper_body_route_20260612_002412/metadata.json
```

Patched workflow:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10j_production_upper_body_route_20260612_002412/scene_event_cg_patched_workflow_api.json
```

## Recommended production prompt policy

From Unit 10I I1, now formalized as production_character route:

```json
{
  "scene_event_route_mode": "production_character",
  "prompt_slots": {
    "character_features": [
      "brown_eyes",
      "tareme",
      "blunt_bangs",
      "brown_hair",
      "medium_hair",
      "straight_hair"
    ],
    "outfit_detail": [
      "red_bow",
      "brown_cardigan",
      "white_shirt",
      "blue_skirt",
      "brown_pantyhose",
      "school_uniform"
    ],
    "scene_context": [
      "auditorium",
      "spotlight",
      "upper_body",
      "looking_at_viewer"
    ]
  }
}
```

## Status

```text
PASS: Unit 10I production direction is now a first-class runner/queue route.
```

Remaining optional work:

```text
- run a 2–3 seed robustness batch with production_character route
- add a dedicated production event CG request template in the project docs
- later consider true reference-conditioned route if prompt-only still fails production identity locks
```
