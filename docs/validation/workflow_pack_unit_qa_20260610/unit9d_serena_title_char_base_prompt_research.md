# Unit 9D Serena title-specific char_base prompt research — 2026-06-11

## Purpose

Continue from Unit 9D-prime after refining `char_base` policy. The initial plan was to generate title-specific heroine candidates. During prerequisite discovery, an already approved Serena base identity was found, so the task changed from "new design search" to "approved identity preservation under the updated runner policy".

## Existing approved Serena identity

Source notes:

```text
E:/workspace/obsidian-vn/sihanbu_villainess_badend/VN/Characters/serena.md
E:/workspace/obsidian-vn/sihanbu_villainess_badend/VN/Assets/serena_char_base_candidates.md
```

Approved asset:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/game/images/characters/serena/serena_char_base_c01.png
```

Approval metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_serena_char_base_20260603_212733/metadata.json
```

Approval verification:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/serena_char_base_c01_promotion_verification.json
```

Approved binding:

```text
candidate: C01
run_id: char_base_serena_char_base_20260603_212733
seed: 260603101
sha256: 97c8181ae424455f9f22cc2512172ab9a5594ce6b489c2166e094c0c6d3d2cb7
```

## Visual identity brief

Serena is:

```text
- original-story villainess and possessed-player heroine
- mature / fatal / ornate romance-fantasy villainess
- compatible with red system light and gold/red high-pressure staging
- visually commanding, controlled, and dangerous
```

Approved C01 reads as:

```text
- red very long wavy hair
- red eyes / sharp tsurime gaze
- ornate red-and-black gown
- black corset
- black gloves
- jewelry / earrings / necklace
- front-facing centered char_base composition
```

Caveat:

```text
- Opaque grey-background char_base reference, not final transparent dialogue sprite.
- Body emphasis is part of the approved visual identity; do not globally remove it from Serena without owner approval.
```

## Prompt migration finding

Unit 9D-prime removed hardcoded `medium_breasts` from the default runner wrapper and moved body-size intent to optional `prompt_slots.body_shape`.

The original approved Serena C01 metadata included `medium_breasts` because the old wrapper forced it:

```text
..., 1girl, solo, medium_breasts, cowboy_shot, ...
```

Therefore, to preserve approved Serena prompt semantics under the updated runner, `serena_char_base.json` was migrated to include:

```json
"body_shape": ["medium_breasts"]
```

Updated prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/serena_char_base.json
```

## Prepare-only verification

Command:

```bash
python tools/run_char_base_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id serena_char_base \
  --scene-id opening_visual_identity \
  --seed 260603101 \
  --prompt-slots E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/serena_char_base.json \
  --prepare-only
```

Result:

```text
TAXONOMY_SOURCE db
TAXONOMY_PLACEHOLDER_TAGS ..., medium_breasts
POSITIVE ..., arms_at_sides, medium_breasts, mature_female, very_long_hair, ...
PREPARE_ONLY
```

This confirms the updated runner now reconstructs the approved Serena prompt semantics via explicit `body_shape` rather than wrapper default.

## Regeneration smoke

Run:

```text
char_base_serena_char_base_20260611_195401
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_serena_char_base_20260611_195401/candidate_01.png
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_serena_char_base_20260611_195401/metadata.json
```

Comparison sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9d_serena_approved_vs_regen_contact_sheet.jpg
```

Hash comparison:

```text
approved sha256: 97c8181ae424455f9f22cc2512172ab9a5594ce6b489c2166e094c0c6d3d2cb7
regen sha256:    52a0e15159ebdeed3011a026c2e736eb834856c7a8c0c461272a6cade0ee0c67
same sha256:     false
```

QA comparison:

```text
PASS for identity preservation.
FAIL for pixel-identical reproduction, which is not required.
```

The regenerated candidate preserves the broad approved identity:

```text
- long red wavy hair
- red eyes / sharp expression
- ornate red/black dress
- black corset
- black gloves
- jewelry
- front-facing centered char_base composition
```

Differences:

```text
- skirt/front lace ornament differs
- corset details differ
- face/expression has small variations
- output is not byte-identical
```

## Policy decision

Do not replace the approved production asset.

```text
Approved C01 remains authoritative.
New 20260611 candidate is only a runner-policy migration verification artifact.
```

For future Serena same-identity work:

```text
- Use seed 260603101 as the approved identity seed.
- Use `serena_char_base.json` with explicit `body_shape: [medium_breasts]` to preserve approved prompt semantics.
- Bind future scene_event_cg/expression work to the approved C01 metadata, not the 20260611 verification candidate, unless owner explicitly approves a replacement.
```

## Next recommendation

Proceed to a transparent/dialogue-sprite or expression-compatible Serena route, not another opaque base search, because Serena already has an approved opaque base identity.

Recommended next:

```text
Unit 9E: Serena approved-base expression/sprite route preflight
- inspect existing expression assets
- decide whether to generate transparent dialogue sprite candidates or expression variants
- keep approval-gated promotion
```
