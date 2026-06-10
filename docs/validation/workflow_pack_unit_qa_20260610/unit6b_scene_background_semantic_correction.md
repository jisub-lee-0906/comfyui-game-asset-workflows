# Unit 6B Scene Background Semantic Correction Smoke — 2026-06-11

## Owner issue from Unit 6

```text
자동화에 프롬프트를 그대로 넣어버리는 문제가있나봐 학교 복도 느낌이야
```

## Automation correction

`run_scene_background_smoke.py` now supports live `semantic_prompt` / `style_prompt` segments in addition to strict taxonomy-validated tag slots.

Reason: generic tags like `indoors, hallway, window, night, moonlight` are insufficient to express noble mansion / dark romantic fantasy architecture and can drift into school/hospital corridors.

## Unit 6B live prompt segment

```text
semantic_prompt: empty noble mansion corridor, dark romantic fantasy interior, ornate gothic architecture
style_prompt: polished dark wood, candlelit atmosphere, elegant aristocratic hallway, no school corridor
```

## Candidate

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6b_noble_mansion_hallway_semantic_smoke_20260611_003736/candidate_01.png
```

## Run

```text
run_id: scene_background_bg_unit6b_noble_mansion_hallway_semantic_smoke_20260611_003736
endpoint: http://127.0.0.1:8000
prompt_id: 9a3653d0-fdc6-4172-83b3-d9771317b247
seed: 360610602
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
- School/hospital corridor drift appears fixed.
- Reads much more like a noble/dark fantasy mansion hallway: arched windows, chandeliers, dark wood, candlelit wall lamps.
- No obvious people/faces/characters.
- No readable text/logo/watermark visible.
- Lower third is mostly floor and should be dialogue-box-safe.
```

## Automation QA conclusion

Unit 6 discovered a real prompt-routing issue. Unit 6B confirms the correction direction: `scene_background` should preserve strict tag validation while also allowing short semantic/style live prompt segments for architecture/material/location identity.
