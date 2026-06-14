# Unit 10M scene_event_cg emotion/framing generalization matrix — 2026-06-12

## Purpose

Expand `scene_event_cg` beyond neutral upper-body generation by testing direct emotion tags and varied framing/camera routes.

User goal:

```text
감정 그대로 프롬프트로 넣어서도 테스트하고, 다양한 자세/근접/카메라 구도를 싹 테스트해서 event CG pipeline의 범용성을 늘리고 자동화에 반영한다.
```

## Scope

```text
workflow: scene_event_cg
seed: 260529217
source: Unit 9A char_base metadata
reference conditioning: none
promotion: none
```

## Route expansion

TDD route additions in `run_scene_event_cg_smoke.py`:

```text
production_character_cowboy:
  allows cowboy_shot + looking_at_viewer

cut_in:
  now allows portrait + close-up + headshot + solo_focus
```

Existing routes retained:

```text
conservative
production_character
production_character_front
cut_in
```

Tests added:

```text
test_scene_event_cg_cowboy_route_allows_cowboy_shot_only_with_look
test_scene_event_cg_cut_in_route_allows_headshot_token
```

## Matrix

Emotions:

```text
happy: smile, open_mouth
serious: serious, closed_mouth
surprised: surprised, open_mouth
sad: sad, tears, frown, closed_mouth
```

Framing routes:

```text
upper: production_character + upper_body, looking_at_viewer
front: production_character_front + upper_body, looking_at_viewer, facing_viewer, straight-on
cutin: cut_in + portrait, close-up, headshot, solo_focus
cowboy probe: production_character_cowboy + cowboy_shot, looking_at_viewer
```

Generated candidates:

```text
happy_upper
happy_front
happy_cutin
serious_upper
serious_front
serious_cutin
surprised_upper
surprised_front
surprised_cutin
sad_upper
sad_front
sad_cutin
cowboy_serious
```

All candidates completed with:

```text
GENERATION_OUTPUT_VERIFIED
```

## Contact sheets

Full image matrix:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10m_emotion_framing_matrix_full_contact_sheet.jpg
```

Face crop matrix:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/unit10m_emotion_framing_matrix_face_contact_sheet.jpg
```

## Visual QA result

### Happy

Best default:

```text
happy_front
route: production_character_front
emotion tags: smile, open_mouth
```

Result:

```text
PASS — best happy general route; direct cheerful event CG with outfit/context preserved.
```

Alternative:

```text
happy_upper
```

Use when a less direct/frontal CG is desired.

Cut-in:

```text
happy_cutin
```

Works well as emotional close-up, not as default general event CG.

### Serious

Best default:

```text
serious_front
route: production_character_front
emotion tags: serious, closed_mouth
```

Result:

```text
PASS — better serious route than upper; stable face/outfit/context.
```

Caveat:

```text
serious is visually subtle. Use cut_in if the scene needs stronger intensity.
```

### Surprised

Best default:

```text
surprised_front
route: production_character_front
emotion tags: surprised, open_mouth
```

Result:

```text
BEST surprised default — strong emotion, stable outfit/context.
```

Cut-in:

```text
surprised_cutin
```

Works for dramatic close-up, but crop/too-close risk makes it non-default.

### Sad

Best default:

```text
sad_front
route: production_character_front
emotion tags: sad, tears, frown, closed_mouth
```

Result:

```text
BEST sad default — clear tears/expression with event composition.
```

Cut-in:

```text
sad_cutin
```

Strong close-up sad cut-in; useful for high-emotion moments but not default event CG.

### Cowboy shot

Probe:

```text
cowboy_serious
route: production_character_cowboy
```

Result:

```text
PARTIAL — useful medium/full shot but face/emotion weaker.
```

Policy:

```text
Keep as optional medium-shot route, not default production route.
```

## Automation policy after Unit 10M

Default route recommendations:

```text
neutral:
  production_character
  expressionless, closed_mouth
  upper_body, looking_at_viewer

happy:
  production_character_front
  smile, open_mouth
  upper_body, looking_at_viewer, facing_viewer, straight-on

serious:
  production_character_front
  serious, closed_mouth
  upper_body, looking_at_viewer, facing_viewer, straight-on

surprised:
  production_character_front
  surprised, open_mouth
  upper_body, looking_at_viewer, facing_viewer, straight-on

sad:
  production_character_front
  sad, tears, frown, closed_mouth
  upper_body, looking_at_viewer, facing_viewer, straight-on

cut-in:
  cut_in
  portrait, close-up, headshot, solo_focus
  use only when the beat intentionally calls for emotional close-up

medium/cowboy:
  production_character_cowboy
  cowboy_shot, looking_at_viewer
  optional, not default
```

## QA report

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10m_scene_event_cg_emotion_framing_matrix/unit10m_emotion_framing_matrix_qa.json
```

## Status

```text
PASS: event CG pipeline range expanded to neutral, happy, serious, surprised, sad, frontal, cut-in, and optional cowboy/medium framing.
```

Promotion remains:

```text
not_promoted_pending_owner_approval
```
