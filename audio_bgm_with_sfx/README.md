# audio_bgm_with_sfx

## 1. Workflow ID

```text
audio_bgm_with_sfx
```

Unified Stable Audio 3 based route for VN BGM, short SFX, one-shot UI sounds, and simple instrumental audio candidates. This workflow replaces the former split BGM/SFX audio routes.

Use this workflow for both `bgm` and `sfx` asset requests unless a future task explicitly requires video-frame-synchronized foley.

## 2. Purpose

Generate audio candidates for Ren'Py visual novels:

- loop/edit-source BGM beds;
- scene ambience-like musical underscoring;
- UI notification one-shots;
- short fantasy/system/foley SFX;
- simple instrument or texture candidates.

Raw outputs are **review candidates**, not production assets. Approved Ren'Py integration still requires audio QA, trim/loop editing, OGG conversion, explicit owner approval, manifest update, and Ren'Py playback verification.

## 3. Canonical files

```text
audio_bgm_with_sfx/audio_bgm_with_sfx_workflow_api.json
audio_bgm_with_sfx/README.md
```

The canonical API JSON must not be overwritten during normal generation. Copy it into a run directory or patch it in memory, then submit the patched payload to ComfyUI.

## 4. Core model and node route

Observed canonical route:

```text
CheckpointLoaderSimple(stable_audio_3_medium.safetensors)
CLIPLoader(t5gemma_b_b_ul2.safetensors, type=stable_audio)
CLIPTextEncode
EmptyLatentAudio
KSampler
VAEDecodeAudio
SaveAudioMP3
```

Optional prompt enhancement branch:

```text
CLIPLoader(qwen3.5_2b_bf16.safetensors)
TextGenerate
ComfySwitchNode
```

The prompt enhancement branch can expand terse prompts, but the default agent route should be **direct prompt first** for reproducibility.

## 5. Editable fields

Patch only these fields at runtime unless the user explicitly approves workflow maintenance:

```text
52:31.inputs.value              # user/agent-authored audio prompt
52:7.inputs.text                # negative prompt
52:43.inputs.choice             # Music | Instrument | SFX | One-shot
52:43.inputs.index              # 0 | 1 | 2 | 3 matching choice
52:36.inputs.value              # duration seconds
52:35.inputs.value              # TextGenerate switch; false = direct prompt
52:3.inputs.seed                # KSampler seed
52:3.inputs.steps               # KSampler steps
52:3.inputs.cfg                 # KSampler CFG
52:3.inputs.sampler_name        # usually lcm
52:3.inputs.scheduler           # usually simple
19.inputs.filename_prefix       # output prefix relative to ComfyUI output root
19.inputs.quality               # MP3 quality, default V0
```

## 6. Mode selection

| Asset need | `52:43.inputs.choice` | Suggested duration | Notes |
|---|---|---:|---|
| BGM / background music | `Music` | 16–60s source | Treat as edit source; trim tail and loop edit. |
| Single instrument/texture | `Instrument` | 4–20s | Useful for motif or tonal layer probes. |
| Longer effect texture | `SFX` | 3–8s | Use for magic whoosh, atmosphere sting, impact beds. |
| UI/notification/short foley | `One-shot` | 1.0–3.0s | Preferred for Ren'Py click/system notification sounds. |

For ordinary VN route requests:

```text
asset_type bgm -> mode Music
asset_type sfx -> mode One-shot by default
```

Use `SFX` instead of `One-shot` when the sound should have a sustained tail or multi-part texture.

## 7. Prompt policy

Audio prompts are natural-language production briefs, not Danbooru tags.

Keep prompts concrete:

1. source/instrument/material;
2. action or musical role;
3. timing/duration feel;
4. spatial/mix character;
5. explicit exclusions.

### BGM prompt template

```text
instrumental visual novel background music, <genre/mood>, <lead instrument>, <supporting instruments>, <rhythmic or harmonic behavior>, <density>, <scene function>, no vocals, no singing, no lyrics, dialogue friendly, loopable
```

Example:

```text
instrumental visual novel background music, dark romantic fantasy, warm felt piano lead, low sustained cello and viola, soft harp arpeggios, slow pulse, sparse arrangement, no vocals, no singing, no lyrics, dialogue friendly, loopable ambience
```

### SFX / one-shot prompt template

```text
short <source/event> sound effect, <material/action>, <transient>, <tail/decay>, <mix character>, no voice, no speech, no music, no melody
```

Example:

```text
short fantasy user interface notification, clear glass bell chime, single magical sparkle, tiny parchment rustle, one clean transient, quick decay, no voice, no music, no melody
```

### Negative prompt baseline

```text
speech, human voice, talking, singing, lyrics, low quality, distorted, clipping, harsh noise, watermark
```

For SFX, add:

```text
background music, melody, song, choir, crowd, ambience bed
```

For BGM, add only if needed:

```text
lead vocal, rap, spoken words, announcer, sound effect impacts
```

## 8. Recommended runtime defaults

### BGM smoke/default

```json
{
  "mode": "Music",
  "duration": 16.0,
  "use_text_generate": false,
  "steps": 8,
  "cfg": 1.0,
  "sampler_name": "lcm",
  "scheduler": "simple"
}
```

For final candidate batches, longer durations such as 30–60s may produce better edit material, but do not skip tail/loop QA.

### SFX / one-shot smoke/default

```json
{
  "mode": "One-shot",
  "duration": 2.5,
  "use_text_generate": false,
  "steps": 8,
  "cfg": 1.0,
  "sampler_name": "lcm",
  "scheduler": "simple"
}
```

Use shorter durations first. If the output has too much dead tail, shorten duration or trim in post.

## 9. Prompt slots JSON contract

Toolkit runners expect agent-authored prompt slots under:

```text
<project>/docs/production/prompt_slots/*.json
```

Minimal BGM example:

```json
{
  "workflow_id": "audio_bgm_with_sfx",
  "asset_id": "bgm_opening_red_contract",
  "author": "agent",
  "prompt_slots": {
    "positive_prompt": "instrumental visual novel background music, dark romantic fantasy, warm felt piano lead, low sustained cello and viola, soft harp arpeggios, slow pulse, sparse arrangement, no vocals, no singing, no lyrics, dialogue friendly, loopable ambience",
    "negative_prompt": "speech, human voice, talking, singing, lyrics, distorted, clipping",
    "mode": "Music",
    "duration": 16.0,
    "use_text_generate": false,
    "steps": 8,
    "cfg": 1.0
  }
}
```

Minimal SFX example:

```json
{
  "workflow_id": "audio_bgm_with_sfx",
  "asset_id": "sfx_red_system_notice",
  "author": "agent",
  "prompt_slots": {
    "positive_prompt": "short fantasy user interface notification, clear glass bell chime, single magical sparkle, tiny parchment rustle, one clean transient, quick decay, no voice, no music, no melody",
    "negative_prompt": "speech, human voice, talking, singing, background music, melody, distorted, clipping",
    "mode": "One-shot",
    "duration": 2.5,
    "use_text_generate": false,
    "steps": 8,
    "cfg": 1.0
  }
}
```

Supported prompt slot keys:

```text
positive_prompt          required
audio_prompt             alias for positive_prompt
bgm_prompt               alias for positive_prompt
sfx_prompt               alias for positive_prompt
negative_prompt          optional
mode / audio_mode        Music | Instrument | SFX | One-shot
duration / seconds       output length in seconds
use_text_generate        false recommended for direct prompt
steps                    KSampler steps
cfg                      KSampler cfg
sampler_name             default lcm
scheduler                default simple
```

## 10. Output and QA

`SaveAudioMP3.inputs.filename_prefix` is relative to the active ComfyUI output root:

```text
$COMFYUI_OUTPUT_DIR
```

After generation, agents must verify exact output files through `/history/{prompt_id}` and filesystem existence. Do not report guessed paths.

Run objective QA before review/promotion:

```bash
ffprobe -v error -show_entries format=duration,bit_rate,size:stream=codec_name,sample_rate,channels,bit_rate -of json <file>
ffmpeg -hide_banner -nostats -i <file> -af volumedetect -f null -
ffmpeg -hide_banner -nostats -i <file> -af silencedetect=noise=-45dB:d=0.5 -f null -
```

QA expectations:

- sample rate/channels readable;
- no decode errors;
- no unexpected speech/vocals;
- no harsh clipping/distortion;
- BGM has enough active span for loop/edit;
- SFX has a clear transient and not excessive tail;
- approved candidates are converted to OGG before Ren'Py promotion.

## 11. Known behavior from replacement smoke

A 2026-06-10 replacement smoke showed:

- ComfyUI execution succeeded for `Music`, `SFX`, and `One-shot` modes.
- Direct prompt mode was viable and more reproducible than TextGenerate for agent-authored prompts.
- BGM outputs may include tail silence and hot peaks; trim/loop/loudness QA remains mandatory.
- One-shot SFX outputs may be quiet and tail-heavy; trim and normalize before integration.

Therefore this workflow is the canonical generation route, but postprocess QA is still part of the production gate.

## 12. Automation style contract from owner QA

Owner QA on 2026-06-10 established a role split for future automated audio generation. Do **not** clone the exact QA prompts/seeds; use these as style/role contracts and adapt to each scene.

Role contracts live next to this README:

```text
roles/audio_sfx.md
roles/audio_bgm.md
roles/audio_role_contracts.json
```

The workflow folder remains a single canonical engine. Automation should route to logical roles (`audio_sfx`, `audio_bgm`) while executing this same `audio_bgm_with_sfx_workflow_api.json`; do not duplicate the workflow JSON into separate BGM/SFX folders.

### SFX role

SFX should be generated as short, functional cues with a clear gameplay/scene purpose.

- Default mode: `One-shot`.
- Default duration: about 1.5–2.5s.
- Good direction from QA: red system alert style — clear transient, short magical/glass/parchment cue, serious tone, quick decay.
- Prompting lesson from owner QA: keep SFX prompts short and positive-first. Prefer one natural-language sentence plus one or two material/instrument colors. Do not over-describe many micro-events or pile up negatives by default.
- Avoid in the prompt itself: long lists of prohibitions, excessive event sequencing, and many competing sound materials. These can cause semantic drift such as door prompts becoming keyboard/chair sounds or magic prompts becoming generic horror rumble.
- Prompt should name the triggering event plainly: e.g. alert appears, wooden door opens, contract seal activates, paper slides.

### BGM role

BGM should be generated as continuous dialogue-friendly music beds, not alert cues.

- Default mode: `Music`.
- Default source duration: about 20–30s for QA batches, longer only after the direction is approved.
- Good direction from QA: B2 / B2-anchor style — continuous dark romantic fantasy bed, felt piano, low strings, understated emotional tension, restrained density.
- Later BGM QA refined this: put musical identity first. `Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.` was closer to the desired BGM direction than a longer functional prompt starting with `background music bed for visual novel dialogue`.
- Preferred BGM prompt shape: `instrumentation + musical form/rhythm + mood + short role`.
- Avoid: one-shot/stinger language, notification chime, sparkle SFX, long mid-track silence gaps, battle drums, intrusive lead melody, vocals/speech.
- Do not start BGM prompts with a long usage explanation; lead with the sound and musical form.

### Generation batch policy

For new audio automation, generate small candidate batches rather than a single file:

- SFX: 3 seed candidates unless the user asks for one exact reroll.
- BGM: 3 seed candidates around a style direction; after owner feedback, generate a second anchor batch if needed.
- Always report exact files, seed, prompt_id, duration, loudness, and silence/tail notes.
- Promotion remains approval-gated; raw MP3 candidates are not final Ren'Py assets.

## 13. Promotion gate

Do not promote raw MP3 candidates directly into game audio.

Required sequence:

```text
generate candidate
-> ffprobe/volumedetect/silencedetect QA
-> listening QA
-> trim/loop edit or one-shot trim
-> normalize if needed
-> convert to OGG
-> explicit owner approval
-> promote to game/audio/...
-> manifest update
-> Ren'Py audio declaration/playback verification
```

Generated candidates remain `not_promoted_pending_owner_approval` until this gate is complete.
