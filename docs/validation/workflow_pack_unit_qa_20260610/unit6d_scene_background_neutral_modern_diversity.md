# Unit 6D/6E Scene Background Neutral Modern Diversity Smoke — 2026-06-11

## Purpose

Reduce title-specific dark-fantasy bias by validating `scene_background` on neutral/modern VN backgrounds.

Targets:

```text
A. modern classroom
B. modern bedroom / small apartment room
C. evening urban residential street
```

## Unit 6D candidates

### A — Modern classroom

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6d_modern_classroom_smoke_20260611_185050/candidate_01.png
```

Prompt summary:

```text
indoors, classroom, school, desk, chair, window, day, sunlight
+ empty modern school classroom background, clean daily-life visual novel setting, no students, no teacher
```

QA:

```text
PASS.
Empty modern classroom. No characters/students/teacher. No readable text/logo. Bright daylight and strong dialogue-background usability.
```

### B — Modern bedroom first attempt

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6d_modern_bedroom_smoke_20260611_185055/candidate_01.png
```

QA:

```text
FAIL.
Good modern bedroom composition, but a black bottom subtitle/caption bar with fake text appeared.
```

Likely cause:

```text
The live semantic/style segment used phrases such as "visual novel setting" / "dialogue overlay".
For novaAnimeXL_ilV190, these can cue a VN screenshot-like composition and produce subtitle/fake text artifacts.
```

### C — Evening urban street

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6d_evening_urban_street_smoke_20260611_185100/candidate_01.png
```

QA:

```text
PASS.
Empty evening residential/urban road. No pedestrians/cars/sign text/logos. Strong VN background readability.
```

## Unit 6E corrective bedroom

Corrective strategy:

```text
- Remove "visual novel" / "dialogue overlay" from live semantic/style text.
- Keep VN usability only in metadata/visual_brief.
- Add validated negative_tags: caption, letterboxed, black_border, text_focus.
- Use natural-language no subtitle bar only as concise style guidance.
```

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/scene_background_bg_unit6e_modern_bedroom_no_subtitle_smoke_20260611_185242/candidate_01.png
```

QA:

```text
PASS.
Empty modern bedroom/small apartment room. No characters. No fake/readable text. No subtitle/caption/black bottom bar. Usable as a full-frame VN background.
```

## Contact sheet

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/backgrounds/unit6d_modern_background_contact_sheet.jpg
```

## Automation lesson

For `scene_background`, keep live prompt language background-only.

Prefer:

```text
empty modern bedroom background, small apartment room, clean full-frame interior
soft daylight, tidy lived-in room, open central wall and floor space
```

Avoid in live positive prompt:

```text
visual novel setting
visual novel background
dialogue overlay
text box
caption
```

Reason:

```text
These phrases can trigger screenshot/UI/caption priors, including fake subtitles or black bottom bars.
```

Keep such intent in metadata/visual_brief instead.

## Current conclusion

`scene_background` is now validated beyond the title-specific dark-fantasy samples:

```text
modern classroom: pass
modern bedroom: pass after prompt correction
urban evening street: pass
```

This supports treating the workflow as broadly usable for fantasy and modern/daily-life VN backgrounds, with the caveat that live semantic text must not cue VN UI/caption artifacts.
