# Unit 5B — BGM Music-first Prompt Smoke

## Scope

Retest BGM with shorter prompts that put musical identity first. Two candidates, no promotion.

- Endpoint: `http://127.0.0.1:8000`
- Workflow: `E:\workspace\comfyui-game-asset-workflows\audio_bgm_with_sfx\audio_bgm_with_sfx_workflow_api.json`
- Candidate directory: `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit5b_bgm_music_first_smoke\candidates`

## Results

| ID | prompt | seed | prompt_id | duration | mean/max dB | silence | file |
|---|---|---:|---|---:|---:|---|---|
| `A_music_first_minor_waltz` | `Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.` | 360610511 | `01641498-4f54-4206-aa8c-65ec975ce889` | 23.962993 | -22.1 / -6.5 | [Parsed_silencedetect_0 @ 000001b68687e6c0] silence_start: 22.389524; [Parsed_silencedetect_0 @ 000001b68687e6c0] silence_end: 23.962993 | silence_duration: 1.573469 | `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit5b_bgm_music_first_smoke\candidates\A_music_first_minor_waltz_candidate_01.mp3` |
| `B_music_first_nocturne` | `Felt piano nocturne, warm cello sustain, sparse harp, melancholic noble fantasy, quiet background music.` | 360610512 | `c5ec2077-cc13-4678-9820-11482e8035a8` | 23.962993 | -22.4 / -5.3 | [Parsed_silencedetect_0 @ 000001ee2cb999c0] silence_start: 22.349116; [Parsed_silencedetect_0 @ 000001ee2cb999c0] silence_end: 23.962993 | silence_duration: 1.613878 | `E:\workspace\comfyui-game-asset-workflows\docs\validation\workflow_pack_unit_qa_20260610\unit5b_bgm_music_first_smoke\candidates\B_music_first_nocturne_candidate_01.mp3` |

## User QA request

Please compare these against Unit 5. Judge whether putting musical identity first improves the BGM direction, and which of A/B is closer.
