# Unit 10L scene_event_cg best-seed micro prompt refinement — 2026-06-12

## Purpose

Push the Unit 10K best production route a little further instead of stopping at a merely robust default.

Question:

```text
At best seed 260529217, can small prompt-slot changes improve eye/face quality and composition without breaking outfit/context preservation?
```

## Scope

```text
workflow: scene_event_cg
seed: 260529217
base route: production_character
baseline: Unit 10K best candidate
promotion: none
```

## Variants

### L1 neutral_face_lock

```text
route: production_character
added character tags: expressionless, closed_mouth
```

Purpose:

```text
Stabilize neutral eyes/mouth/face while preserving event CG framing.
```

Run:

```text
scene_event_cg_event_unit10l_l1_neutral_face_lock_20260612_080828
```

### L2 focus_bokeh

```text
route: production_character
added scene tags: blurry_background, bokeh
```

Purpose:

```text
Increase perceived face/eye focus without changing route mode.
```

Run:

```text
scene_event_cg_event_unit10l_l2_focus_bokeh_20260612_080839
```

### L3 front_straight

```text
route: production_character_front
added scene tags: facing_viewer, straight-on
```

Purpose:

```text
Test whether frontal route improves face/eye quality enough to justify a separate route.
```

Run:

```text
scene_event_cg_event_unit10l_l3_front_straight_20260612_080844
```

### L4 pose_neutral

```text
route: production_character
added scene tag: arms_at_sides
```

Purpose:

```text
Try a simple body/pose stabilizer without changing camera route.
```

Run:

```text
scene_event_cg_event_unit10l_l4_pose_neutral_20260612_080850
```

## Contact sheet

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10l_micro_refinement_contact_sheet.jpg
```

Panels:

```text
SOURCE char_base
10K best seed260529217
L1 neutral_face
L2 focus_bokeh
L3 front_straight
L4 arms_sides
```

## Visual QA ranking

### 1. L1 neutral_face_lock — best overall refinement

Status:

```text
best_overall_refinement
```

Why:

```text
- improves over 10K baseline for neutral event CG
- more orderly upper-body composition
- eye/face stable
- red bow preserved
- brown cardigan preserved
- event background/context preserved
```

Policy implication:

```text
For neutral production event CGs, add expressionless + closed_mouth to the production_character prompt policy.
```

### 2. L3 front_straight — best face detail, separate frontal route

Status:

```text
best_face_detail_frontal_route
```

Why:

```text
- best eye/face detail in the batch
- strong frontal composition
- outfit/context preserved
```

Caveat:

```text
Feels more like a frontal emphasis/dialogue-like event CG than the default general event CG.
```

Policy implication:

```text
Keep production_character_front as a separate intentional route, not the default.
```

### 3. L2 focus_bokeh — strong but more cut-in-like

Status:

```text
strong_but_more_cut_in
```

Why:

```text
- good eye detail
- stronger face focus
```

Caveat:

```text
Face becomes larger and more cut-in-like; less balanced than L1 for default event CG.
```

### 4. L4 arms_sides — no clear improvement

Status:

```text
no_clear_improvement
```

Why:

```text
- outfit/context preserved
- but not clearly better than Unit 10K baseline
```

Policy implication:

```text
Do not default arms_at_sides.
```

## Final result

```text
IMPROVED PROMPT POLICY FOUND
```

Default neutral production event CG policy now becomes:

```text
scene_event_route_mode: production_character
character_features: brown_eyes, tareme, blunt_bangs, brown_hair, medium_hair, straight_hair, expressionless, closed_mouth
outfit_detail: red_bow, brown_cardigan, white_shirt, blue_skirt, brown_pantyhose, school_uniform
scene_context: auditorium, spotlight, upper_body, looking_at_viewer
```

Keep this caveat:

```text
expressionless/closed_mouth is a neutral-scene stabilizer, not a universal emotional-event default.
```

## QA report

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10l_scene_event_cg_micro_refinement/unit10l_micro_refinement_ranked_qa.json
```

## Promotion status

```text
not_promoted_pending_owner_approval
```
