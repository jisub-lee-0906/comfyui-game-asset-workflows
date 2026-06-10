# Unit 7G novaAnimeXL_ilV190 Prop Prompt Shape Retest — Smartphone / Document — 2026-06-11

## Purpose

Retest the Unit 7F provisional `object-first compact` prompt shape on prior failure-prone prop classes:

```text
1. smartphone / blank screen — fake UI/logo risk
2. blank parchment/document — fake text/envelope/multiple-paper risk
```

Each target compares:

```text
A. current quality-first README wrapper
B. object-first compact
```

## Smartphone A — current wrapper

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7g_prop_prompt_shape_retest/unit7g_01_phone_A_current_wrapper.png
```

Prompt:

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, smartphone, screen, glass, desk, shadow, BREAK, depth_of_field, BREAK, plain modern smartphone lying on desk, completely blank black screen, screen turned off, dark reflection only, no logo, no icons, no app UI, no text
```

Agent QA:

```text
- Smartphone is clear and dominant.
- No people/hands/faces.
- No cup/glass/drink extra object.
- Problem: small UI/logo-like marks remain at top-left/top edge and a home-button-like symbol appears.
- Not a strict blank/off screen pass.
```

## Smartphone B — object-first compact

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7g_prop_prompt_shape_retest/unit7g_02_phone_B_object_first_compact.png
```

Prompt:

```text
plain smartphone, blank black screen, screen turned off, smartphone, screen, glass, desk, shadow, still_life, object_focus, no_humans, no logo, no icons, no app UI, no text, dark reflection only, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Agent QA:

```text
- Smartphone is large/dominant and no cup/glass/drink extra object.
- No people/hands/faces.
- Problem: small icon-like/UI-like white marks still appear near the top-left, and a home-button-like symbol appears.
- Object-first improves subject dominance but does not solve fake phone UI/symbol risk.
```

## Document A — current wrapper

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7g_prop_prompt_shape_retest/unit7g_03_doc_A_current_wrapper.png
```

Prompt:

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, blank_page, paper, wooden_table, shadow, BREAK, depth_of_field, BREAK, blank parchment sheet on wooden table, empty paper prop, no writing visible, no handwriting, not an envelope, simple item cut-in
```

Agent QA:

```text
- Clean single blank sheet on wooden table.
- No writing/handwriting/text/envelope/book/stamp/logo.
- No people/hands/faces.
- Strong pass as a blank document/overlay base.
- Best document candidate so far.
```

## Document B — object-first compact

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7g_prop_prompt_shape_retest/unit7g_04_doc_B_object_first_compact.png
```

Prompt:

```text
blank parchment sheet, empty paper, blank_page, paper, wooden_table, shadow, still_life, object_focus, no_humans, no writing visible, no handwriting, not an envelope, simple item cut-in, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Agent QA:

```text
- No visible writing/text.
- No people/hands/faces.
- Problem: multiple sheets/paper fragments appear, so single-object adherence fails.
- Object-first made the paper concept stronger but also multiplied it.
- Not acceptable for single blank document base.
```

## Model-specific finding update

Unit 7F suggested object-first compact is good for `key`, but Unit 7G shows this is not universal.

```text
- Key / simple physical objects: object-first compact is likely beneficial.
- Smartphone / screen objects: object-first increases subject dominance but does not remove baked UI/logo/symbol artifacts.
- Blank document / paper objects: quality-first wrapper with explicit blank/no-writing semantics works better; object-first can multiply sheets.
```

## Prompt-shape recommendation v0.2

Use prop-class-specific prompt policies instead of one global wrapper:

```text
simple_object_key_ring_vial:
  object-first compact

screen_device_smartphone:
  object-first or compact wrapper for dominance, but prefer post-edit / mask cleanup / alternate non-screen angle if strict logo-free blank is required

blank_document_paper:
  quality-first wrapper + blank_page/paper + explicit no writing semantics; avoid over-repeating paper object terms at the front
```

## Next suggested research

For smartphone specifically, try reducing `screen`/phone UI triggers rather than only changing order:

```text
- phone lying face down / back side only
- side view smartphone with dark reflective glass and no visible display details
- generate phone shell/base, then overlay screen separately
```

For document:

```text
Document A can be treated as pass candidate for blank overlay base.
```
