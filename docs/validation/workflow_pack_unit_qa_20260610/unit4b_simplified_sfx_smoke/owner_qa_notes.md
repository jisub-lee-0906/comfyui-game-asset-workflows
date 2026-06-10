# Unit 4B Owner QA Notes — Simplified SFX Prompt Smoke

Owner QA after listening to Unit 4B simplified positive-only SFX candidates:

```text
훨씬 의도와 맞게 수정된거같아 bgm으로 넘어가도돼
```

## Interpretation

The simplified positive-only prompting style improved SFX semantic alignment compared with Unit 4's over-described positive + long negative prompts.

## Automation decision

For future SFX generation with `audio_bgm_with_sfx`:

```text
Use short positive-only or near-positive-only natural-language prompts.
Describe one triggering event clearly.
Add only one or two material/instrument/timbre colors.
Avoid long negative lists and excessive micro-event sequencing by default.
Use mode/duration according to situation: One-shot for short UI cues, SFX for medium/long functional effects.
```

## Status

```text
Unit 4B SFX prompting direction: owner_accepted_as_better_direction
Proceed to BGM validation.
```
