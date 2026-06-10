# Unit 4 — audio_bgm_with_sfx SFX Situation Smoke

## Scope

This is the first actual generation unit. It tests SFX only, across three situation lengths/roles. No asset was promoted.

- Endpoint: `http://127.0.0.1:8000`
- Workflow: `E:\workspace\comfyui-game-asset-workflows\audio_bgm_with_sfx\audio_bgm_with_sfx_workflow_api.json`
- Candidate directory: `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4_audio_sfx_smoke\candidates`

## Results

| ID | role | mode | target duration | seed | prompt_id | verified files | measured duration | mean/max dB | silence note |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| `A_short_ui_system_cue` | 짧은 UI/system cue: system alert / choice appears | `One-shot` | 2.5s | 360610401 | `84df8748-46f2-42fd-8ba4-6325ea2beed3` | 1 | 2.507755 | -38.3 / -17.3 | [Parsed_silencedetect_0 @ 000001fe5cfdb0c0] silence_start: 0.710567; [Parsed_silencedetect_0 @ 000001fe5cfdb0c0] silence_end: 2.507755 | silence_duration: 1.797188 |
| `B_medium_foley_action_cue` | 짧은 행동/foley cue: old wooden door opens then settles | `SFX` | 3.5s | 360610402 | `432fb071-d5dd-4dae-8c83-e50b957ef4da` | 1 | 3.529433 | -35.8 / -0.1 | [Parsed_silencedetect_0 @ 000001d15777d940] silence_start: 2.44322; [Parsed_silencedetect_0 @ 000001d15777d940] silence_end: 3.529433 | silence_duration: 1.086213 |
| `C_longer_sustained_magic_cue` | 조금 긴 sustained SFX: magic contract forms and hums ominously | `SFX` | 7.0s | 360610403 | `b4f3e8d2-ed51-4286-9669-3ce77b40e6fa` | 1 | 6.965986 | -18.4 / 0.0 | [Parsed_silencedetect_0 @ 000002634015b580] silence_start: 4.378322; [Parsed_silencedetect_0 @ 000002634015b580] silence_end: 6.965986 | silence_duration: 2.587664 |

## Candidate files

### A_short_ui_system_cue

Intent: 짧은 UI/system cue: system alert / choice appears

Prompt: `short dark fantasy visual novel user interface sound effect, system notification appears, clear glass bell chime, tiny magical sparkle, subtle ominous low pulse, quick decay, serious tone, no voice, no speech, no music, no melody`

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4_audio_sfx_smoke\candidates\A_short_ui_system_cue_candidate_01.mp3`

### B_medium_foley_action_cue

Intent: 짧은 행동/foley cue: old wooden door opens then settles

Prompt: `realistic visual novel foley sound effect, old heavy wooden door slowly opens, soft hinge creak, subtle room tone, gentle wooden latch click at the end, close microphone, natural decay, no voice, no speech, no music, no melody`

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4_audio_sfx_smoke\candidates\B_medium_foley_action_cue_candidate_01.mp3`

### C_longer_sustained_magic_cue

Intent: 조금 긴 sustained SFX: magic contract forms and hums ominously

Prompt: `sustained dark fantasy visual novel magic sound effect, ominous contract magic forming in the air, low resonant magical hum, faint parchment rustle, slow rising tension, subtle crystal shimmer, controlled energy swell, smooth fade tail, no voice, no speech, no music, no melody`

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4_audio_sfx_smoke\candidates\C_longer_sustained_magic_cue_candidate_01.mp3`

## User QA request

Please listen to the three files and judge whether the SFX automation uses the right mode/duration for each situation: short UI cue, medium foley cue, and longer sustained magic cue.
