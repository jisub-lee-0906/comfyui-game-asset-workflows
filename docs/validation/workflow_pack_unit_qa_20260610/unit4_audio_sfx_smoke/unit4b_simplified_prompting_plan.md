# Unit 4B Prompting Revision Plan — Simplified SFX Prompts

Owner feedback after Unit 4:

```text
프롬프트가 과한거같아 positive만 넣고 짧은 자연어 문장과 어울리는 악기 느낌 정도면 될거같거든?
```

## Interpretation

The Unit 4 SFX prompts were over-specified. Long negative lists and too many micro-events likely caused semantic drift:

- door/foley prompt drifted toward keyboard typing + chair creak;
- sustained magic prompt leaned into horror low rumble;
- UI cue worked better because glass/chime material was simple and direct.

## Revised SFX prompting rule

For SFX automation, prefer:

```text
positive-only or near-positive-only
one short natural-language sentence
one triggering event
one or two material/instrument/timbre colors
minimal/no negative prompt unless a recurrent failure must be suppressed
```

Avoid:

```text
long prohibition lists
many micro-actions in one prompt
many competing materials
heavy mood words like ominous/horror/dread unless explicitly wanted
```

## Proposed simplified retest prompts

### Door foley simplified

```text
An old wooden door opens slowly with one clear metal hinge creak and a soft wooden handle click.
```

Optional color only if needed:

```text
close quiet room foley, dry wood and metal hinge texture
```

### Contract magic simplified

```text
A dark fantasy contract seal activates with a soft arcane hum, parchment shimmer, and gentle crystal resonance.
```

Optional color only if needed:

```text
restrained magical glass and parchment texture
```

### UI cue simplified

```text
A short glass chime rings when a visual novel system notification appears.
```

Optional color only if needed:

```text
clear crystal bell, serious fantasy UI tone
```

## Next test recommendation

Run Unit 4B with only two generated files first:

1. simplified door foley;
2. simplified contract magic sustained cue.

Keep UI cue unchanged as the Unit 4 direction already matched owner hearing.
