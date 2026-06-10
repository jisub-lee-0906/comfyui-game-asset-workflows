# Unit 5 Owner QA Notes — First BGM Smoke

Owner QA after Unit 5 BGM single smoke:

```text
음 별로야 다른 방향으로 진행해줘 맨앞에 프롬프트가 너무 길지않아?
```

## Interpretation

The first BGM prompt was too long and functional at the front:

```text
A quiet dark romantic fantasy background music bed for visual novel dialogue, with soft felt piano, low strings, and gentle harp texture.
```

Problem:

```text
The prompt begins with broad functional explanation rather than musical identity. The model may receive "background music bed for visual novel dialogue" before concrete style/instrument cues, resulting in weak or generic music direction.
```

## Revised BGM prompting rule

For BGM automation, put musical identity first:

```text
instrumentation + rhythm/tempo + mood + short scene role
```

Prefer concise prompts such as:

```text
Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.
```

Avoid starting BGM prompts with long functional prose such as:

```text
A quiet background music bed for visual novel dialogue...
```

## Unit 5B plan

Generate a new BGM smoke with a shorter, music-first prompt.
