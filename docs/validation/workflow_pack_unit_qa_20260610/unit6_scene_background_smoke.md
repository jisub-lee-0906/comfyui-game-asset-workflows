# Unit 6 Scene Background Smoke — 2026-06-11

## Intent

Generate one independent `scene_background` candidate for workflow-pack QA.

```text
Empty 16:9 VN background; intended semantic direction: empty noble mansion hallway / dark romantic fantasy corridor; no humans, no readable text, dialogue-box-safe composition.
```

## Prompt slots

```text
background_theme: indoors, hallway, window
time_mood: night, moonlight
negative_tags: []
```

## Live prompt

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, scenery, no_humans, wide_shot, landscape, indoors, hallway, window, night, moonlight, BREAK, depth_of_field, volumetric_lighting
```

## Negative

```text
1girl, 1boy, crowd, people, silhouette, monster, animal, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, ugly, lowres, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, simple_background, (worst_quality, bad_quality:1.2)
```

## Run

```text
run_id: scene_background_bg_unit6_empty_noble_hallway_smoke_20260611_003109
endpoint: http://127.0.0.1:8000
prompt_id: 2606d52a-0ab6-4065-9eba-ee61df92ae7c
seed: 360610601
```

## Candidate

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6_empty_noble_hallway_smoke_20260611_003109/candidate_01.png
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
- No obvious humans/faces/characters.
- No readable text/logo/watermark visible.
- 16:9 VN background-like corridor composition.
- Lower third is mostly floor/shadow and likely dialogue-box-safe.
- Semantic drift: it reads more like a modern/school/hospital corridor than a noble mansion hallway. The basic background workflow works, but the prompt/tag set is not sufficient for "noble mansion" direction.
```

## Owner QA needed

```text
1. Usable as generic empty hallway background?
2. Reject for noble/dark romantic fantasy mismatch?
3. If rerolling, should we expand tags/README contract to support mansion/castle/gothic interiors more explicitly?
```
