# Unit 9D-prime char_base Prompt Policy Refinement — 2026-06-11

## Purpose

Before title-specific heroine generation, refine `char_base` default prompt policy based on Unit 9A-9C findings:

```text
- README default `medium_breasts` increased upper-body emphasis.
- school/cardigan uniform often produced chest badge/emblem.
- necktie intent could drift into bow/ribbon.
```

## Tag oracle check

Confirmed active SQLite tags:

```text
small_breasts, medium_breasts, flat_chest,
necktie, red_necktie, blue_necktie,
ribbon, bow,
badge, emblem, crest, school_emblem
```

## Research setup

Same seed for all variants:

```text
260529202
```

Base identity:

```text
medium_hair, straight_hair, blunt_bangs, brown_hair, brown_eyes, tareme
```

Research script:

```text
E:/workspace/comfyui-game-asset-workflows/docs/validation/workflow_pack_unit_qa_20260610/unit9d_prime_char_base_prompt_policy.py
```

Research metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/unit9d_prime_char_base_prompt_policy/unit9d_prime_metadata.json
```

Contact sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9d_prime_char_base_policy_contact_sheet.jpg
```

## Variants and QA

### A — baseline medium_breasts + cardigan

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9d_prime_char_base_prompt_policy/unit9d_prime_01_A_baseline_medium_breasts_cardigan.png
```

QA:

```text
Usable char_base but confirms known issues:
- chest badge/emblem present
- neckwear becomes bow/ribbon, not necktie
- upper-body emphasis remains visible
```

### B — small_breasts + red_necktie + no badge/bow/ribbon

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9d_prime_char_base_prompt_policy/unit9d_prime_02_B_small_breasts_red_necktie_no_badge.png
```

QA:

```text
Best balanced result.
- badge/emblem removed
- red necktie appears correctly
- bow/ribbon drift removed
- upper-body emphasis reduced versus baseline
- cardigan identity preserved
- suitable char_base candidate
```

### C — no breast-size token + red_necktie + no badge/bow/ribbon

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9d_prime_char_base_prompt_policy/unit9d_prime_03_C_no_breast_size_red_necktie_no_badge.png
```

QA:

```text
Very low body emphasis and badge/necktie correction works.
However, same-seed identity shifts slightly more: hair appears longer/less like selected Unit 9B face.
Good option when neutral body shape is more important than exact face continuity.
```

### D — blazer + red_necktie + no cardigan

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9d_prime_char_base_prompt_policy/unit9d_prime_04_D_blazer_red_necktie_no_cardigan.png
```

QA:

```text
Badge/necktie correction works and blazer identity is clean.
But this is a different uniform identity from cardigan schoolgirl. Use only when blazer uniform is intended.
```

## Policy conclusion

Recommended `char_base` prompt policy:

```text
1. Do not hardcode medium_breasts in the default wrapper.
2. Add optional prompt_slots.body_shape for character-specific body intent.
3. Use color-specific necktie tags such as red_necktie / blue_necktie when necktie matters.
4. For school/cardigan uniforms, allow prompt_slots.negative_tags to suppress badge/emblem/crest/school_emblem/bow/ribbon.
```

## Automation reflection

Updated runner:

```text
E:/workspace/vn-automation-toolkit/tools/run_char_base_smoke.py
```

New optional slots:

```json
{
  "body_shape": ["small_breasts"],
  "negative_tags": ["badge", "emblem", "crest", "school_emblem", "bow", "ribbon"]
}
```

Default wrapper no longer includes forced `medium_breasts`.

Updated README:

```text
E:/workspace/comfyui-game-asset-workflows/char_base/README.md
```

Added tests:

```text
E:/workspace/vn-automation-toolkit/tests/test_char_base_routing.py
```

## Final runner smoke

Prompt slots:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/char_unit9d_prime_policy_smoke.json
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9d_prime_policy_smoke_20260611_193451/candidate_01.png
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9d_prime_policy_smoke_20260611_193451/metadata.json
```

QA:

```text
PASS.
Runner-reflected policy matches Unit 9D-prime B:
- badge/emblem removed
- red necktie preserved
- bow/ribbon absent
- body emphasis reduced vs baseline
- cardigan/skirt/pantyhose and grey-background char_base structure preserved
```

## Test results

```text
python -m pytest tests/test_char_base_routing.py -q
2 passed in 0.04s

python -m pytest tests/test_prompt_slots_fail_closed.py::test_char_base_prepare_only_requires_agent_authored_prompt_slots tests/test_prompt_slots_fail_closed.py::test_char_base_prepare_only_uses_sqlite_taxonomy_when_root_csv_removed -q
2 passed in 0.33s

python -m pytest -q
135 passed in 39.12s
```

## Next recommendation

Proceed to title-specific heroine char_base only after selecting whether the heroine should use:

```text
- body_shape omitted for neutral default,
- small_breasts for lower body emphasis,
- or a deliberate character-specific body tag.
```

For school/uniform heroine designs, use explicit `red_necktie`/`blue_necktie` and negative badge/bow/ribbon tags when appropriate.
