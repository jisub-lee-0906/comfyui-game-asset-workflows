# Unit 5 — BGM Single Smoke

## Scope

First BGM generation unit after SFX validation. One candidate only. No promotion.

- Endpoint: `http://127.0.0.1:8000`
- Workflow: `E:\workspace\comfyui-game-asset-workflows\audio_bgm_with_sfx\audio_bgm_with_sfx_workflow_api.json`
- Candidate directory: `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit5_bgm_smoke\candidates`

## Intent

continuous dialogue-friendly BGM bed; B2/B2-anchor style direction, but not prompt/seed clone

## Prompt

Positive-only prompt:

```text
A quiet dark romantic fantasy background music bed for visual novel dialogue, with soft felt piano, low strings, and gentle harp texture.
```

Negative prompt: intentionally blank.

## Settings

```text
mode: Music
duration: 24.0s
seed: 360610501
steps: 8
cfg: 1.0
sampler: lcm
scheduler: simple
prompt_id: fe3d76de-50ab-437c-b1e6-ee0e6123adc5
```

## Candidate

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit5_bgm_smoke\candidates\A_dialogue_dark_romantic_bed_candidate_01.mp3`

## Objective QA

```text
verified files: 1
measured duration: 23.962993
sample_rate: 44100
channels: 2
mean/max dB: -23.2 / -4.3
silence: [Parsed_silencedetect_0 @ 000001dab6a0efc0] silence_start: 22.590317; [Parsed_silencedetect_0 @ 000001dab6a0efc0] silence_end: 23.962993 | silence_duration: 1.372676
```

## User QA request

Please listen and judge whether this works as a BGM/music bed rather than SFX/stinger: continuous, dialogue-friendly, dark romantic fantasy mood, not too busy or too empty.
