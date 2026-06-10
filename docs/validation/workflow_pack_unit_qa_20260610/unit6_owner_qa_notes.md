# Unit 6 Owner QA Notes — Scene Background Semantic Failure

Owner QA after reviewing Unit 6 `scene_background` candidate:

```text
자동화에 프롬프트를 그대로 넣어버리는 문제가있나봐 학교 복도 느낌이야
```

## Interpretation

The generated image passed basic file/background checks, but failed semantic intent.

Intended direction:

```text
empty noble mansion hallway / dark romantic fantasy corridor
```

Live placeholder tags:

```text
indoors, hallway, window, night, moonlight
```

Observed result:

```text
school-like / institutional hallway
```

## Root cause

The automation currently patches README placeholders too literally with a small generic tag set. `hallway + window + night` is not enough to express a noble mansion or dark romantic fantasy location, and it can collapse into common school/hospital corridor imagery.

This is not simply a bad seed. It is a prompt-routing / prompt-slot expressiveness issue.

## Required automation correction

For `scene_background`, prompt slots must separate:

```text
1. verified core Danbooru tags
2. short natural-language semantic intent
3. style/material/location qualifiers
```

The runner/README should not reduce a rich scene brief to only generic tags when the desired location depends on architecture/material/style.

## Next corrective test

Run Unit 6B with a richer but still controlled background prompt shape, e.g.:

```text
scenery, no_humans, wide_shot, landscape, indoors, castle, hallway, gothic_architecture, candelabra, window, night, moonlight, dark romantic fantasy noble mansion corridor
```

If unsupported tags are missing from taxonomy, either:

- validate and add them to the allowed set if active/non-deprecated; or
- keep them in a natural-language semantic segment separate from the strict tag segment.

## Status

Unit 6 basic workflow smoke: pass.
Unit 6 semantic automation QA: fail; prompt-slot policy needs correction before accepting `scene_background` automation as robust.
