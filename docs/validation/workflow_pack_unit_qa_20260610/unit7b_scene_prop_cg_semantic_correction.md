# Unit 7B Scene Prop CG Semantic Correction Smoke — 2026-06-11

## Unit 7 issue

Unit 7 generated a clean single prop, but it read as a generic white envelope with a red heart/wax seal rather than a red magical contract document.

## Correction applied

`run_scene_prop_cg_smoke.py` now supports `semantic_prompt` / `style_prompt` live prompt segments, similar to `scene_background`.

Unit 7B removed the `envelope` tag and added:

```text
red magical contract document, unfolded parchment sheet, sealed noble pact evidence, dark red wax seal, ominous fantasy clue, subtle arcane glow, not a love letter, not an envelope
```

## Candidate

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7b_red_magic_contract_semantic_smoke_20260611_005704/candidate_01.png
```

## Run

```text
workflow: scene_prop_cg
endpoint: http://127.0.0.1:8000
prompt_id: 8b5dbcae-69df-4899-a83d-e528e737beb1
seed: 360610702
size: 1024x576
```

## File QA

```text
format: PNG
mode: RGB
size: 1024x576
aspect: 1.7778
status: file_qa_pass_pending_owner_visual_review
```

## Agent visual QA notes

```text
- Contract/document feeling improved compared to Unit 7.
- Wooden table and red wax seal are clear.
- No humans/hands/faces visible.
- Problem: fake handwritten text appears on the parchment, violating no-readable/fake-text prop rule.
- Problem: envelope remains visually central despite removing the envelope tag and adding "not an envelope".
- It is closer to sealed letter on top of contract parchment than a clean red magical contract document.
```

## Automation conclusion

`semantic_prompt/style_prompt` support is useful but not sufficient for text-prone document props. For document/letter/book props, automation should prefer blank/empty parchment candidates and plan to add readable story text outside ComfyUI via overlay/Ren'Py/post-edit. If the prop needs to avoid fake text, prompt should emphasize blank parchment/symbolic seal and may need multiple candidates or a different safer prop type.

## Suggested next corrective direction

```text
Unit 7C: blank red wax-sealed parchment / magical seal prop
- avoid envelope wording entirely
- avoid contract/document wording if it triggers fake writing
- use "blank parchment sheet", "red wax seal", "arcane glowing seal", "no writing visible" in semantic/style
- consider adding extra negative tags/semantic no-writing controls
```
