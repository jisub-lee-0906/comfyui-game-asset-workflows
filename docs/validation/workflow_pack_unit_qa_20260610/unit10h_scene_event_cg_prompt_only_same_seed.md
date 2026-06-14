# Unit 10H scene_event_cg prompt-only same-seed identity/outfit experiments — 2026-06-11

## Purpose

Respond to the Unit 10G visual caveat: the live `scene_event_cg` no-ref route worked mechanically but the baseline prompt produced identity/outfit drift and eye damage.

User direction:

```text
Before moving to reference conditioning, try many prompt-only variants with the same seed.
The local model is newer than the assistant's training knowledge and can respond well to correct tags.
```

Scope:

```text
workflow: scene_event_cg
mode: live ComfyUI prompt-only experiments
seed: 260529202 fixed across variants
source: Unit 9A neutral schoolgirl char_base metadata
promotion: forbidden
```

## Baseline problem

Unit 10G baseline:

```text
run_id: scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316
prompt omitted full source outfit detail and red_bow
```

Observed baseline drift:

```text
- red bow drifted to blue bow
- brown cardigan disappeared
- short-sleeve white shirt replaced source cardigan outfit
- eye/face impression drifted
```

## Prompt-only strategy

The second pass followed the source metadata more faithfully and kept the same seed:

```text
seed: 260529202
character: brown_eyes, tareme, blunt_bangs, brown_hair, medium_hair, straight_hair
outfit: red_bow, brown_cardigan, white_shirt, blue_skirt, brown_pantyhose, school_uniform
scene: auditorium, spotlight, optionally indoors/bokeh
```

All tags were validated through the local Danbooru SQLite taxonomy by the runner.

## Variants generated

First pass:

```text
H1 source_full_exact
H2 accessory_lock
H3 eye_face_lock
H4 compact_identity_first
```

Second pass:

```text
H5 neutral_eye_outfit_lock
H6 accessory_first_minimal_scene
H7 source_prompt_face_neutral
H8 cardigan_color_detail
```

Contact sheets:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10h_prompt_only_same_seed_contact_sheet.jpg
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10h_prompt_only_same_seed_contact_sheet_pass2.jpg
```

QA ranking report:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10h_scene_event_cg_prompt_only_same_seed/unit10h_prompt_only_same_seed_ranked_qa.json
```

## Best result

Best prompt-policy candidate:

```text
H6 accessory_first_minimal_scene
run_id: scene_event_cg_event_unit10h_h6_accessory_first_minimal_scene_20260611_234633
```

Prompt slots:

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
    "spotlight"
  ]
}
```

Observed:

```text
- red bow preserved
- brown cardigan preserved
- blue skirt/brown pantyhose preserved
- eyes readable and not obviously damaged
- 16:9 event composition usable
- auditorium/spotlight context still present
```

Status:

```text
STRONG PARTIAL PASS / best prompt-only candidate so far
```

It is a major improvement over the Unit 10G baseline, but still not promoted.

## Other strong candidates

```text
H7 source_prompt_face_neutral
H5 neutral_eye_outfit_lock
```

Findings:

```text
- Adding expressionless + closed_mouth can help neutral face/eye stability.
- Reintroducing full source outfit tags is more important than extra scene tags.
- Minimal scene context reduces outfit drift.
- Accessory/color tags such as red_bow and brown_cardigan should be explicit, not assumed from school_uniform.
```

## Prompt policy findings

For current novaAnimeXL_ilV190 + scene_event_cg route:

```text
1. Do not rely on school_uniform alone for outfit continuity.
2. Carry forward full source char_base outfit tags: brown_cardigan, red_bow, blue_skirt, brown_pantyhose, white_shirt.
3. Put fragile identity tags early: brown_eyes, tareme, blunt_bangs.
4. For neutral CGs, expressionless + closed_mouth may reduce eye/face drift.
5. Keep scene_context compact; auditorium + spotlight worked better than heavier scene pressure.
6. Use the same source seed for continuity, but treat prompt slots as the real driver of visual preservation.
7. Prompt-only can substantially improve the result on this model, though it remains weaker than true reference conditioning for exact identity.
```

## Outcome

```text
Unit 10H improved event_cg from Unit 10G's identity/outfit partial failure to a strong prompt-only partial pass.
```

This validates the user's hypothesis: with this newer model, correct Danbooru tag selection/order materially improves event CG quality even without reference conditioning.

## Next recommendation

Before building a reference-conditioned route, run one more controlled prompt-only batch around H6/H7 if needed:

```text
- H6 same prompt with 2-3 nearby seeds for robustness, or
- H6 same seed with only one variable changed at a time: scene_context, expression tags, outfit order.
```

Promotion remains blocked until owner visual approval.
