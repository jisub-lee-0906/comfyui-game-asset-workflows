# Unit 7Q scene_prop_cg prop-class coverage smoke — 2026-06-11

## Purpose

Continue broad VN automation-level audit without focusing on named characters/scenes/assets.

Scope:

```text
workflow: scene_prop_cg
mode: automation audit fixture coverage
production intent: none
promotion: forbidden
```

Unit 7Q extends prop-class coverage beyond the already-tested classes:

```text
previously strong/covered:
- document/parchment/contract after semantic prompt corrections
- key
- smartphone/screen_device after dedicated prompt_shape policy

tested here:
- jewelry/small ring
- glass vial/container
- knife/tool
```

## Guardrail

This run followed the automation audit drift guard:

```text
Automation audit measures the machine, not a specific heroine/scene/asset.
```

All assets are generic fixtures:

```text
prop_unit7q_fixture_gold_ring_gem_smoke
prop_unit7q_fixture_glass_vial_smoke
prop_unit7q_fixture_kitchen_knife_smoke
prop_unit7q_fixture_ring_band_corrective_smoke
prop_unit7q_fixture_upright_corked_vial_corrective_smoke
```

No production promotion.

## Prompt validation

All fixture tags were checked against the local workflow-pack Danbooru SQLite taxonomy.

Rejected/missing tags:

```text
ruby: missing
metal: missing
silver: missing as generic material
reflective: missing as exact tag
```

Accepted tags:

```text
ring, gem, jewelry, gold, scratches, vial, glass, liquid, cork, knife, kitchen_knife, wooden_table, shadow
```

All smoke runs reported:

```text
PROMPT_POLICY README wrapper + agent-authored SQLite-verified prompt slots
PROMPT_SHAPE object_first_compact
TAXONOMY_SOURCE db
GENERATION_OUTPUT_VERIFIED
```

## Contact sheet

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7q_prop_class_coverage_contact_sheet.jpg
```

## Runs and QA

### A. Jewelry / ring initial

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/prop_unit7q_fixture_gold_ring_gem_smoke.json
```

Run:

```text
scene_prop_cg_prop_unit7q_fixture_gold_ring_gem_smoke_20260611_202635
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7q_fixture_gold_ring_gem_smoke_20260611_202635/candidate_01.png
```

QA:

```text
FAIL / partial
- single gold/gem object exists
- but reads more like domed ornament/box/helmet than a ring
- band/hole geometry not visible
```

### B. Glass vial initial

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/prop_unit7q_fixture_glass_vial_smoke.json
```

Run:

```text
scene_prop_cg_prop_unit7q_fixture_glass_vial_smoke_20260611_202645
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7q_fixture_glass_vial_smoke_20260611_202645/candidate_01.png
```

QA:

```text
FAIL
- split into open glass/cup plus separate vial/dropper
- violates single-object prop requirement
```

### C. Knife/tool

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/prop_unit7q_fixture_kitchen_knife_smoke.json
```

Run:

```text
scene_prop_cg_prop_unit7q_fixture_kitchen_knife_smoke_20260611_202655
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7q_fixture_kitchen_knife_smoke_20260611_202655/candidate_01.png
```

QA:

```text
PASS
- single kitchen knife clearly visible
- no hands/fingers
- no blood/food/plate
- no readable text/logo
- object class and count stable
```

### D. Ring corrective

Reason:

```text
Initial ring fixture drifted into domed ornament/box-like geometry.
```

Corrective live semantic:

```text
single thin circular gold ring band with one small gem, hole visible through the center, lying flat on plain wooden tabletop
```

Run:

```text
scene_prop_cg_prop_unit7q_fixture_ring_band_corrective_smoke_20260611_202816
```

QA:

```text
PARTIAL / FAIL
- ring/hole cue improved
- but result still reads like a large circular ornament/plate with a small secondary ring-like object
- object count and class remain ambiguous
```

### E. Vial corrective

Reason:

```text
Initial vial split into open glass/cup plus separate vial/dropper.
```

Corrective live semantic:

```text
one closed upright corked glass vial only, small potion bottle with colored liquid inside, centered on plain wooden tabletop
```

Run:

```text
scene_prop_cg_prop_unit7q_fixture_upright_corked_vial_corrective_smoke_20260611_202827
```

QA:

```text
FAIL
- closed corked bottle shape improved
- but still generated two bottles
- single-object constraint remains unreliable
```

## Automation finding

`object_first_compact` is useful but not universally sufficient.

Current prop-class maturity:

```text
high confidence:
- kitchen_knife / knife-like tool
- key-like simple metal prop
- screen_device with dedicated screen_device_black_screen_safe shape

medium confidence:
- document/parchment/contract, when semantic_prompt and fake-text suppression are used

low confidence / needs stronger policy:
- ring / small jewelry: drifts into ornament/box/plate, poor band geometry
- vial / glass container: tends to split into multiple containers or cup+dropper
```

## Recommended policy update

README should explicitly mark ring/vial as caution classes:

```text
ring/jewelry:
- needs visible band geometry, not just ring/gem/jewelry tags
- QA must reject domes, plates, jewelry boxes, extra rings
- may require seed batch or workflow change for reliable single-ring output

vial/container:
- needs one closed upright corked vial only
- QA must reject cup/tumbler/dropper/spill/multiple bottles
- prompt-only single-object control is weak; consider mask/control or batch-selection before production use
```

## Do not over-iterate during audit

Further rerolls could optimize these specific fixture assets, but that would violate the broad automation audit goal. The correct next action is to record the class limitation and move to the next workflow coverage area.
