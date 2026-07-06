# Unit 10I scene_event_cg face-proximity / framing experiment — 2026-06-11

## Purpose

Follow user observation after Unit 10H:

```text
Faces appear higher quality when the character is framed closer.
If that is the best quality direction, automation should move that way.
```

Scope:

```text
workflow: scene_event_cg
mode: live ComfyUI experiment
seed: 260529202 fixed
base prompt: H6 accessory_first_minimal_scene identity/outfit policy
canonical workflow: not modified
experiment method: runtime patched workflow removes only selected framing tags from negative prompt per variant
promotion: forbidden
```

## Method

H6 best prompt policy was used as the base:

```text
character_features:
  brown_eyes, tareme, blunt_bangs, brown_hair, medium_hair, straight_hair
outfit_detail:
  red_bow, brown_cardigan, white_shirt, blue_skirt, brown_pantyhose, school_uniform
scene_context:
  auditorium, spotlight
```

Framing tags were added per variant. For each variant, the same exact framing tags were removed from the runtime negative prompt copy only. The canonical workflow file was not changed.

Validated framing tags:

```text
upper_body
cowboy_shot
portrait
headshot
close-up
solo_focus
looking_at_viewer
facing_viewer
```

`face_focus` was rejected because it is not present in the local Danbooru SQLite taxonomy.

## Variants

```text
I1 upper_body:
  upper_body, looking_at_viewer

I2 cowboy_shot:
  cowboy_shot, looking_at_viewer

I3 portrait:
  portrait, solo_focus

I4 close-up:
  close-up, solo_focus

I5 upper_body+face:
  upper_body, facing_viewer, looking_at_viewer
```

Contact sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10i_framing_experiment_contact_sheet.jpg
```

QA ranking:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10i_scene_event_cg_framing_experiment/unit10i_framing_ranked_qa.json
```

## Result

Result:

```text
PASS: closer upper-body framing improved eye/face quality.
```

Best variant:

```text
I1 upper_body
run_id: scene_event_cg_unit10i_i1_upper_body_seed260529202
```

Best prompt policy candidate:

```json
{
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
```

Why I1 ranked best:

```text
- best balance of face proximity and event-CG usability
- eyes are clearer than H6/10G baseline
- red_bow preserved
- brown_cardigan preserved
- white_shirt / blue_skirt / brown_pantyhose preserved
- auditorium/spotlight context remains visible
```

Second-best:

```text
I5 upper_body + facing_viewer + looking_at_viewer
```

I5 gives a stronger frontal character presentation, but it can feel closer to VN dialogue sprite framing than a cinematic event CG.

## Portrait / close-up result

```text
I3 portrait and I4 close-up improved face detail, but became cut-in/portrait shots rather than general event CGs.
```

Therefore:

```text
portrait / close-up are useful for special cut-in CGs, not as the default event CG framing policy.
```

## Automation implication

The user's hypothesis is supported:

```text
On the active local model, face proximity/framing matters significantly for eye and face quality.
```

Recommended automation direction:

```text
Split scene_event_cg into at least two policy modes:

1. conservative fixture/no-ref route:
   - keeps pose/camera tags mostly negative-reserved
   - useful for broad automation smoke tests

2. production character event route:
   - uses H6 identity/outfit prompt policy
   - allows upper_body + looking_at_viewer, removing those exact tokens from negative
   - optionally allows facing_viewer for frontal VN event CGs
```

Do not use generic close-up as the default. Keep it as a separate cut-in route.

## Status

```text
STRONG PARTIAL PASS / production-route direction found
```

This still does not equal reference-conditioned identity lock, but it is the best prompt-only direction found so far and is materially better than Unit 10G and H6-only.

Promotion remains blocked until owner approval.
