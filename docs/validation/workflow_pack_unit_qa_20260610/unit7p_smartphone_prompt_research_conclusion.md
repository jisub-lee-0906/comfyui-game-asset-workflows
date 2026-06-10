# Unit 7N-7P Smartphone Prompt Research — Featureless vs Practical Black Screen

## Unit 7N result

Prompt direction:

```text
small plain smartphone on wooden tabletop, featureless empty black glass front, display powered off, completely blank dark reflective glass surface, single smartphone only, wooden_table, shadow, still_life, object_focus, no_humans, tabletop fills background, no logo, no icons, no app UI, no text, no corner marks, no colored marks, no monitor, no large display, simple modern item cut-in, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Generated seeds:

```text
360610723
360610724
360610725
```

Agent QA:

```text
All 3 produced a usable single smartphone on wooden tabletop with black/off screen and no obvious UI/text/logo/monitor/extra object. Hardware details such as bezel/speaker/notch/buttons remain.
```

## Unit 7O automation smoke

Runner path with `prompt_shape=screen_device_black_screen_safe` worked technically:

```text
PROMPT_SHAPE screen_device_black_screen_safe
TAXONOMY_PLACEHOLDER_TAGS smartphone, phone, shadow, wooden_table
GENERATION_OUTPUT_VERIFIED
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/props/scene_prop_cg_prop_unit7o_smartphone_featureless_black_glass_automation_smoke_20260611_020012/candidate_01.png
```

Agent QA:

```text
Single smartphone on wooden tabletop, no large monitor/extra objects, no readable text/app UI/logo.
However, hardware/small corner marks and a home-button-like ring remain.
```

## Unit 7P strict buttonless experiment

Prompt direction tried to remove hardware details entirely:

```text
buttonless black glass slab shaped like a smartphone
no home button, no notch, no speaker slot, no camera hole
```

Result:

```text
Failed for strict buttonless intent. The model continues to synthesize plausible phone hardware features such as speaker slots, button rings, ports, and bezels.
```

## Final research conclusion for smartphone props

For `novaAnimeXL_ilV190`, prompt-only generation can reliably get:

```text
- single smartphone on wooden tabletop
- black/off screen
- no app UI
- no readable text
- no obvious logo
- no large monitor/cup/keyboard extra objects
```

Prompt-only generation is not reliable for:

```text
- completely buttonless / notchless / speakerless phone
- perfectly featureless black glass rectangle
```

Recommended practical policy:

```text
screen_device_black_screen_safe:
  accept hardware bezel/button/notch/speaker/camera marks
  reject readable text, app UI, status bar, logo, obvious icon, monitor/large display extras
```

If a perfectly featureless display is required, use post-edit/masking rather than prompt-only generation.
