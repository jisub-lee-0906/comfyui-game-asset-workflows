# Unit 7C Scene Prop CG Blank Parchment / Red Seal Smoke — 2026-06-11

## Unit 7B issue

Unit 7B improved story intent but still had:

```text
- envelope remains too central
- fake handwritten text appears
```

## Corrective direction

Avoid readable/contract-like document generation. Generate a safe blank prop base:

```text
blank parchment sheet
red wax / arcane seal
wooden table
no writing visible
not an envelope
```

## Live prompt

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, blank_page, paper, glowing, wooden_table, shadow, BREAK, depth_of_field, BREAK, blank parchment sheet with a dark red wax seal, arcane sealed clue prop, no writing visible, no handwriting, not an envelope, subtle magical red glow, dark fantasy evidence
```

## Candidate

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7c_blank_parchment_red_seal_smoke_20260611_010057/candidate_01.png
```

## Run

```text
workflow: scene_prop_cg
endpoint: http://127.0.0.1:8000
prompt_id: 0edd9789-ae61-4738-ab7c-05590d4b68db
seed: 360610703
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
- Fake text issue appears solved: no visible writing/handwriting.
- No humans/hands/faces visible.
- Strong single prop focus on wooden table.
- Reads as blank folded/parchment paper with a dramatic dark red seal/glow.
- It is less like a written contract and more like a sealed cursed/magical parchment base, which is safer for later overlay.
- Possible semantic concern: the red seal may read as blood/ink spill rather than wax seal, but it does support ominous magical clue mood.
- Still has some folded-paper geometry, but no explicit envelope flap/heart-letter feeling like Unit 7.
```

## Automation conclusion

For document-like props, the safer automated base is:

```text
blank parchment / paper base + symbolic seal/glow
```

Readable or exact contract text should be added outside ComfyUI through overlay/post-edit/Ren'Py. This avoids fake-text artifacts while preserving the item/evidence cut-in role.
