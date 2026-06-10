# audio_bgm role contract

This role uses the canonical `audio_bgm_with_sfx` workflow. Do not create or maintain a separate copied workflow JSON for BGM.

## Routing

```text
asset_type: bgm
workflow_id: audio_bgm_with_sfx
audio_role: audio_bgm
```

## Prompt shape

Lead with the musical identity, not a long usage explanation.

```text
instrumentation + musical form/rhythm + mood + short role
```

Current owner-preferred anchor direction:

```text
Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.
```

Use this as a style contract, not as a seed/prompt clone. Adapt the instrumentation, form/rhythm, mood, and role to the scene.

Avoid starting with long functional prose such as:

```text
A quiet background music bed for visual novel dialogue...
```

Avoid SFX/stinger language:

```text
notification, chime, alert, sparkle, one-shot, sudden hit, impact
```

## Defaults

```text
negative_prompt: ""
mode: Music
duration: 20-30s for QA source candidates; longer only after direction approval
use_text_generate: false
```

## QA gate

A valid file is not enough. Owner/audio semantic QA must confirm that the output reads as continuous BGM/music bed rather than a stinger/SFX, and that it is dialogue-friendly.
