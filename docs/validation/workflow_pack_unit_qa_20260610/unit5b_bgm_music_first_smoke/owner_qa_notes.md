# Unit 5B Owner QA Notes — BGM Music-first Prompt Smoke

Owner QA after listening to Unit 5B candidates:

```text
A쪽이 더 bgm의 방향성에 맞아
```

## Candidates

### A_music_first_minor_waltz

Prompt:

```text
Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.
```

Owner decision:

```text
closer_to_bgm_direction
```

Interpretation:

```text
The music-first prompt with a clear musical form/rhythm cue (`slow minor waltz`) gave a stronger BGM direction than the broader dialogue-bed prose prompt and the nocturne variant.
```

### B_music_first_nocturne

Prompt:

```text
Felt piano nocturne, warm cello sustain, sparse harp, melancholic noble fantasy, quiet background music.
```

Owner decision:

```text
less_preferred_than_A
```

## Automation lesson

For BGM generation with `audio_bgm_with_sfx`, prefer prompts that put musical identity first and include a concise form/rhythm cue:

```text
instrumentation + musical form/rhythm + mood + short role
```

Current preferred direction:

```text
soft felt piano + low strings + slow minor waltz + dark romantic fantasy + quiet dialogue underscore
```

Do not clone this exact prompt/seed blindly. Use it as the BGM prompt style anchor, adapting instrumentation, rhythm, and mood to the scene role.

## Recommended next test

Run Unit 5C around the A direction with 2–3 nearby variants, for example:

```text
1. same direction, softer and less prominent rhythm
2. same direction, darker low strings
3. same direction, more romantic piano lead but still dialogue-safe
```
