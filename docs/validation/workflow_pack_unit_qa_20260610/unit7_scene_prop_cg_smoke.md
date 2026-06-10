# Unit 7 Scene Prop CG Smoke — 2026-06-11

## Intent

```text
Single red magical contract document / envelope on dark wooden table; no humans/hands/faces; no readable text; usable as VN item/evidence cut-in.
```

## Live prompt

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, letter, envelope, blank_page, paper, glowing, wooden_table, shadow, BREAK, depth_of_field
```

## Negative

```text
1girl, 1boy, cropped, out_of_frame, duplicate, close-up, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, lowres, bad_anatomy, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, (worst_quality, bad_quality:1.2), fake_text, logo, label, screenshot, dialogue_box, caption
```

## Candidate

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7_red_contract_document_smoke_20260611_005105/candidate_01.png
```

## Run

```text
workflow: scene_prop_cg
endpoint: http://127.0.0.1:8000
prompt_id: 633693e4-bdb9-4f4f-ad01-351ecd5387d8
seed: 360610701
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
- Single prop/object focus is strong.
- No humans/hands/faces visible.
- No readable text/logo/watermark visible.
- Dark wooden table placement is clear.
- Usable as a VN item/envelope cut-in candidate.
- Semantic mismatch: reads as a white envelope with a red heart/wax seal, not a red magical contract document.
- The prop workflow appears to share the same issue as early scene_background: visual_brief/tag_rationale are metadata only, while the live prompt is mostly generic tags. For stronger story props, scene_prop_cg likely also needs short semantic_prompt/style_prompt support.
```

## QA question

```text
Accept as generic sealed envelope prop? Or reject for red magical contract semantic mismatch and run Unit 7B with semantic/style prompt support?
```
