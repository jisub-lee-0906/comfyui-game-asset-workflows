# Unit 4B — Simplified Positive-only SFX Prompt Smoke

## Scope

Retests all three SFX situations using the owner-requested prompting style: short positive-only natural language prompts, no negative prompt. No asset was promoted.

- Endpoint: `http://127.0.0.1:8000`
- Workflow: `E:\workspace\comfyui-game-asset-workflows\audio_bgm_with_sfx\audio_bgm_with_sfx_workflow_api.json`
- Candidate directory: `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4b_simplified_sfx_smoke\candidates`

## Results

| ID | mode | target duration | seed | prompt_id | verified files | measured duration | mean/max dB | silence note |
|---|---|---:|---:|---|---:|---:|---:|---|
| `A_simple_ui_system_chime` | `One-shot` | 2.5s | 360610411 | `8d407f7b-24c1-4398-bd11-3eb0f406a90a` | 1 | 2.507755 | -24.7 / -2.4 | [Parsed_silencedetect_0 @ 000001ee50bdce00] silence_start: 1.185533; [Parsed_silencedetect_0 @ 000001ee50bdce00] silence_end: 2.507755 | silence_duration: 1.322222 |
| `B_simple_old_wooden_door` | `SFX` | 3.5s | 360610412 | `3b2cf8db-02f7-4374-89fd-23ac2e973a64` | 1 | 3.529433 | -37.9 / -4.3 | [Parsed_silencedetect_0 @ 000001c5c392c200] silence_start: 1.852336; [Parsed_silencedetect_0 @ 000001c5c392c200] silence_end: 3.529433 | silence_duration: 1.677098 |
| `C_simple_contract_magic_seal` | `SFX` | 7.0s | 360610413 | `abfa34ec-0f58-413c-b82a-80045f87b2c4` | 1 | 6.965986 | -24.0 / -3.5 | [Parsed_silencedetect_0 @ 000001db061dbbc0] silence_start: 4.592562; [Parsed_silencedetect_0 @ 000001db061dbbc0] silence_end: 6.965986 | silence_duration: 2.373424 |

## Prompts and files

### A_simple_ui_system_chime

Intent: short UI/system cue using simple positive-only prompt

Positive-only prompt: `A short glass chime rings when a visual novel system notification appears, with a clear crystal bell tone.`

Negative prompt: intentionally blank.

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4b_simplified_sfx_smoke\candidates\A_simple_ui_system_chime_candidate_01.mp3`

### B_simple_old_wooden_door

Intent: medium foley/action cue using simple positive-only prompt

Positive-only prompt: `An old wooden door opens slowly with one clear metal hinge creak and a soft wooden handle click.`

Negative prompt: intentionally blank.

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4b_simplified_sfx_smoke\candidates\B_simple_old_wooden_door_candidate_01.mp3`

### C_simple_contract_magic_seal

Intent: longer sustained contract magic cue using simple positive-only prompt

Positive-only prompt: `A dark fantasy contract seal activates with a soft arcane hum, parchment shimmer, and gentle crystal resonance.`

Negative prompt: intentionally blank.

- `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit4b_simplified_sfx_smoke\candidates\C_simple_contract_magic_seal_candidate_01.mp3`

## User QA request

Please compare against Unit 4 and judge whether simplified positive-only prompting improves semantic accuracy for UI cue, door foley, and sustained contract magic SFX.
