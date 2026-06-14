# Unit 10K scene_event_cg production_character seed robustness — 2026-06-12

## Purpose

Verify whether the Unit 10J formalized `production_character` route is robust beyond the single Unit 10I I1 seed.

Question:

```text
Is H6/I1 prompt policy + scene_event_route_mode=production_character reliable enough to become the default production prompt-only event CG route?
```

## Scope

```text
workflow: scene_event_cg
route_mode: production_character
prompt policy: event_unit10j_production_upper_body_route
reference conditioning: none
seed strategy: fixed prompt, additional seeds
promotion: none
```

## Prompt slots

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10j_production_upper_body_route.json
```

Core prompt slots:

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

## Generated seeds

Additional live generations:

```text
seed 260529203 -> scene_event_cg_event_unit10j_production_upper_body_route_20260612_003540
seed 260529217 -> scene_event_cg_event_unit10j_production_upper_body_route_20260612_003551
seed 260530001 -> scene_event_cg_event_unit10j_production_upper_body_route_20260612_003557
```

All three runs completed with:

```text
GENERATION_OUTPUT_VERIFIED
route_mode: production_character
negative_policy: route_policy_runtime_copy
```

The effective negative prompt removed only:

```text
upper_body
looking_at_viewer
```

and continued to block unrelated pose/camera tokens such as:

```text
standing
facing_viewer
close-up
cowboy_shot
from_above
from_below
dutch_angle
```

## Contact sheet

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10k_production_character_seed_robustness_contact_sheet.jpg
```

Compared panels:

```text
SOURCE char_base
I1 seed260529202 previous best
10K seed260529203
10K seed260529217
10K seed260530001
```

## Visual QA ranking

### 1. seed 260529217 — best candidate

Run:

```text
scene_event_cg_event_unit10j_production_upper_body_route_20260612_003551
```

Assessment:

```text
best overall production candidate in the batch
centered upper-body framing
good eye/face quality
red bow preserved
brown cardigan preserved
auditorium/spotlight context preserved
```

### 2. seed 260530001 — strong candidate

Run:

```text
scene_event_cg_event_unit10j_production_upper_body_route_20260612_003557
```

Assessment:

```text
good eye/face quality
red bow/cardigan preserved
slightly more front/cut-in-like than rank 1
usable 16:9 event CG
```

### 3. seed 260529202 — previous best still valid

Run:

```text
scene_event_cg_unit10i_i1_upper_body_seed260529202
```

Assessment:

```text
balanced composition
good proof of upper-body route
slightly less preferred than seed 260529217 in this batch
```

### 4. seed 260529203 — partial candidate

Run:

```text
scene_event_cg_event_unit10j_production_upper_body_route_20260612_003540
```

Assessment:

```text
full image has usable event context and outfit
tilted/offset composition makes face QA weaker
not preferred as production default
```

## Overall status

```text
PASS WITH SEED SELECTION REQUIRED
```

The `production_character` route is robust enough to keep as the default production prompt-only event CG route.

However, it should not generate a single seed and auto-promote. Small seed batches remain necessary because composition/framing can drift by seed.

## Policy result

Recommended default for prompt-only production event CGs:

```text
scene_event_route_mode: production_character
scene_context includes: upper_body, looking_at_viewer
full source outfit/accessory carry-forward required
batch size: at least 3 seeds
promotion: owner approval only
```

Reject criteria:

```text
face off-frame or too tilted
eye damage / muddy iris detail
missing red_bow
missing brown_cardigan
wrong outfit color
loss of auditorium/spotlight context when required
```

## QA report

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10k_scene_event_cg_production_character_seed_robustness/unit10k_production_character_seed_robustness_ranked_qa.json
```

## Promotion status

```text
not_promoted_pending_owner_approval
```

No generated candidate was promoted to production assets.
