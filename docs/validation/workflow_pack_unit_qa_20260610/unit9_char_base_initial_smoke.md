# Unit 9 char_base Initial Smoke / Repro / Outfit Variant — 2026-06-11

## Purpose

Start validating `char_base` after non-character workflows were stabilized.

Scope:

```text
- Use current README wrapper and SQLite-validated prompt slots.
- Test neutral female character base, not title-specific heroine yet.
- Confirm one successful direction, seed reproducibility, and same-seed outfit variant behavior.
```

## Prompt slots

Base prompt slots:

```text
character_features:
medium_hair, straight_hair, blunt_bangs, brown_hair, brown_eyes, tareme

outfit_detail:
school_uniform, white_shirt, brown_cardigan, blue_skirt, brown_pantyhose
```

Prompt slots file:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/char_unit9a_neutral_schoolgirl_base_smoke.json
```

## Unit 9A — first smoke

Seed:

```text
260529200
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190055/candidate_01.png
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190055/metadata.json
```

QA:

```text
PASS candidate.
Solo 1girl, grey background, front-facing standing/cowboy-shot base.
School uniform/cardigan/skirt/pantyhose reflected.
No extra character/text. Hands/arms acceptable for char_base smoke.
```

Caveats:

```text
Cardigan badge/emblem appears automatically.
Slight upper-body emphasis from README default medium_breasts.
Not a transparent dialogue sprite; opaque reference/base candidate only.
```

## Unit 9B — same prompt, 3-seed reproducibility

Seeds:

```text
260529201
260529202
260529203
```

Candidates:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190232/candidate_01.png
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/candidate_01.png
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190303/candidate_01.png
```

Contact sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/unit9_char_base_repro_contact_sheet.jpg
```

QA:

```text
All three pass as neutral char_base candidates.
The workflow reliably produces solo female front-facing opaque character bases with grey background.
Hair/eye direction, cardigan, blue skirt, pantyhose, closed mouth, and simple pose are stable.
```

Recurring caveats:

```text
- School uniform can create an automatic chest badge/emblem.
- `necktie`-like intent may become a bow/ribbon because school_uniform priors dominate.
- Body emphasis remains influenced by README default `medium_breasts` and outfit material.
```

Best current base seed for follow-up:

```text
260529202
```

Reason:

```text
Balanced headroom/crop, clean face, stable pose, strong uniform readability.
```

## Unit 9C — same-seed outfit variant

Variant prompt slots:

```text
character_features:
medium_hair, straight_hair, blunt_bangs, brown_hair, brown_eyes, tareme

outfit_detail:
winter_clothes, black_coat, white_sweater, jeans, boots
```

Same seed:

```text
260529202
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/characters/char_base_char_unit9c_neutral_schoolgirl_winter_coat_variant_smoke_20260611_190528/candidate_01.png
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9c_neutral_schoolgirl_winter_coat_variant_smoke_20260611_190528/metadata.json
```

QA:

```text
PARTIAL PASS.
Same brown-haired/brown-eyed identity is reasonably preserved.
Outfit changes clearly to black coat + white sweater + jeans.
Solo/grey background/no text/no extra characters pass.
```

Caveat:

```text
Same seed helps preserve face/hair identity, but outfit changes can still alter perceived body shape, maturity, and silhouette. `white_sweater` plus README default `medium_breasts` increases upper-body emphasis.
```

## Automation lesson

`char_base` is functional for neutral female opaque reference candidates.

Current policy:

```text
same seed = useful identity-consistency aid
same seed != complete identity/body/silhouette lock
```

For production character anchors, select one base candidate and treat its metadata/seed as a reference handoff for `scene_event_cg`, but do not assume outfit variants are approval-equivalent without visual QA.

## Next recommended work

Before title-specific heroine generation, refine one of these depending on priority:

```text
A. char_base prompt policy: reduce default body emphasis / badge drift.
B. title-specific heroine base: generate Serena/active title heroine candidates using the now-verified char_base route.
C. char_base transparent/dialogue sprite route: separate from opaque base candidate generation.
```
