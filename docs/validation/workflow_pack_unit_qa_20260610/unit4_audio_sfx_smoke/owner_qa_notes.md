# Unit 4 Owner QA Notes — SFX Situation Smoke

Owner listened to the three generated SFX candidates and provided semantic QA.

## A_short_ui_system_cue

File:

```text
E:/workspace/comfyui-game-asset-workflows/docs/validation/workflow_pack_unit_qa_20260610/unit4_audio_sfx_smoke/candidates/A_short_ui_system_cue_candidate_01.mp3
```

Intended by agent:

```text
short UI/system cue; system notification / choice appears; glass/chime/magical cue
```

Owner heard:

```text
유리 부딪히는 소리 + 차임벨 느낌
```

QA interpretation:

```text
Mostly matches intended direction. It reads as glass/chime UI cue. The direction is valid for magical/system notification style SFX, though future automation may need level/trim adjustment because objective QA showed low loudness and long tail silence.
```

Decision:

```text
semantic_direction_pass_for_short_ui_cue
```

## B_medium_foley_action_cue

File:

```text
E:/workspace/comfyui-game-asset-workflows/docs/validation/workflow_pack_unit_qa_20260610/unit4_audio_sfx_smoke/candidates/B_medium_foley_action_cue_candidate_01.mp3
```

Intended by agent:

```text
old wooden door opens then settles; hinge creak + latch click
```

Owner heard:

```text
키보드 타자음 이후 의자 삐걱이는 소리 느낌
```

QA interpretation:

```text
Semantic miss for the intended door/hinge foley. It may still be usable as another office/room interaction SFX, but it does not validate the prompt as a reliable old-door generation recipe.
```

Decision:

```text
semantic_fail_for_door_foley; possible_relabel_candidate_keyboard_or_chair_creak
```

Automation lesson:

```text
For door/foley SFX, prompt needs stronger physical event anchoring and probably fewer ambiguous mechanical/click descriptors. Future tests should separate keyboard/typing/chair/door classes and require owner QA before treating foley prompt patterns as validated.
```

## C_longer_sustained_magic_cue

File:

```text
E:/workspace/comfyui-game-asset-workflows/docs/validation/workflow_pack_unit_qa_20260610/unit4_audio_sfx_smoke/candidates/C_longer_sustained_magic_cue_candidate_01.mp3
```

Intended by agent:

```text
longer sustained magic contract forming; ominous low resonance and tension
```

Owner heard:

```text
살짝 공포감 느껴지는 저음 울림
```

QA interpretation:

```text
Partial semantic match. It did produce sustained low ominous resonance, so the long SFX mode/duration direction works mechanically. However, it leans horror/low-rumble rather than clearly magical contract formation. Future prompts should control horror intensity depending on scene role.
```

Decision:

```text
partial_pass_for_long_sustained_sfx; mood_too_horror_for_general_contract_magic
```

Automation lesson:

```text
Long SFX should be split by dramatic function: ominous horror rumble vs magical contract resonance vs ambience bed. If the target is contract magic but not horror, include clearer magical material cues and reduce horror/ominous wording.
```

## Overall Unit 4 conclusion

The workflow generated real audio with correct rough duration/mode categories. Owner QA shows:

```text
A: direction pass for short UI glass/chime cue.
B: semantic fail for door foley; output reads as keyboard/chair instead.
C: partial pass for sustained low ominous SFX; too horror-leaning for neutral contract magic.
```

This validates that situation-based SFX testing is necessary. The automation must not assume SFX quality from file/duration checks alone; semantic listening QA is required per SFX class.
