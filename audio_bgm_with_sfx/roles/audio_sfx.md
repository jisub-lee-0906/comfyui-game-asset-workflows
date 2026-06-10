# audio_sfx role contract

This role uses the canonical `audio_bgm_with_sfx` workflow. Do not create or maintain a separate copied workflow JSON for SFX.

## Routing

```text
asset_type: sfx
workflow_id: audio_bgm_with_sfx
audio_role: audio_sfx
```

## Prompt shape

Use short positive-only or near-positive-only natural-language cues.

```text
trigger event + one sound identity + one/two material or timbre colors
```

Good examples:

```text
A short glass chime rings when a visual novel system notification appears, with a clear crystal bell tone.
An old wooden door opens slowly with one clear metal hinge creak and a soft wooden handle click.
A dark fantasy contract seal activates with a soft arcane hum, parchment shimmer, and gentle crystal resonance.
```

Avoid by default:

```text
long negative lists
many micro-events in one prompt
many competing materials
BGM-like melody language
voice/speech/song requests unless explicitly intended
```

## Defaults

```text
negative_prompt: ""
mode: One-shot for short UI/system cues
mode: SFX for medium/long foley, sustained magic, ambience-like effects
duration: 1.5-2.5s for one-shots; 3-8s for longer SFX
use_text_generate: false
```

## QA gate

File QA is not enough. Owner/audio semantic QA must confirm that the sound matches its function, because door/foley prompts can drift into keyboard/chair sounds and magic prompts can drift into generic horror rumble.
