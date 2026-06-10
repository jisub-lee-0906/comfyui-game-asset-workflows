# Unit 7F novaAnimeXL_ilV190 Prop Prompt Shape Research — 2026-06-11

## Purpose

User raised that the QA may need model-specific prompt research rather than only automation constraints.

Test target:

```text
one old brass key alone on wooden table
```

Shared negative:

```text
1girl, 1boy, cropped, out_of_frame, duplicate, close-up, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, lowres, bad_anatomy, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, (worst_quality, bad_quality:1.2), fake_text, logo, label, screenshot, dialogue_box, caption, lock, box, book, stack, extra objects, multiple objects, jewelry, pendant
```

Shared seed:

```text
360610708
```

## A — current README wrapper, quality first + semantic prose at end

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7f_prop_prompt_shape_research/unit7f_01_A_current_wrapper_long.png
```

Prompt:

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, key, scratches, wooden_table, shadow, BREAK, depth_of_field, BREAK, one old brass key alone on wooden table, single object item cut-in, plain warm desk light, worn metal key, no other props
```

Agent QA:

```text
- Clean single key on table.
- No extra objects/text/people.
- Key is somewhat small and composition leaves a lot of empty table.
- Good single-object adherence, but less item-cut-in impact.
```

## B — object-first compact

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7f_prop_prompt_shape_research/unit7f_02_B_object_first_compact.png
```

Prompt:

```text
old brass key, single key, key, worn metal, scratches, wooden_table, shadow, still_life, object_focus, no_humans, one object only, warm desk light, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Agent QA:

```text
- Strongest object emphasis.
- Key is large, clear, and centered as item cut-in.
- No extra objects/text/people.
- Slightly close-up / large crop feeling, but still usable.
- Best evidence that novaAnimeXL follows early subject tokens strongly for prop CG.
```

## C — compact tag-first, minimal prose

File:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/unit7f_prop_prompt_shape_research/unit7f_03_C_tag_compact_minimal_prose.png
```

Prompt:

```text
masterpiece, best_quality, very_aesthetic, high_resolution, no_humans, still_life, object_focus, key, scratches, wooden_table, shadow, depth_of_field, single old key, no other props
```

Agent QA:

```text
- Clean single key, no extra objects/text/people.
- Good composition and table placement.
- Key is less visually dominant than B but more prominent than A.
- Balanced candidate; compact prompt performs well.
```

## Early model-specific finding

For `novaAnimeXL_ilV190.safetensors` / Illustrious-style SDXL workflow:

```text
- Prop CG benefits from putting the target object very early.
- Long quality wrapper first can still work, but may reduce subject dominance.
- Compact prompts with the object near the front are better for single-object item cut-ins.
- Negative prompt helps, but positive order/shape appears more important than simply adding more negative terms.
```

## Provisional prop prompt recommendation

Prefer this structure for `scene_prop_cg` prompt research:

```text
{target object}, {single-object restatement}, {key material/detail}, {placement}, still_life, object_focus, no_humans, {short style}, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Example:

```text
old brass key, single key, key, worn metal, scratches, wooden_table, shadow, still_life, object_focus, no_humans, one object only, warm desk light, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Next research should repeat this with a text-prone object such as smartphone and a document/blank parchment object to see whether object-first compact also reduces fake UI/text drift.
