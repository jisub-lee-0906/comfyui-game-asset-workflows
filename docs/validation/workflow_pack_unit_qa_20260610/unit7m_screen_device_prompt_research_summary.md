# Unit 7H-I-K-L-M Screen Device Prompt Research — Summary

## User instruction

```text
의도에 맞는 산출물이 나올때까지 계속 연구해줘 의도에 맞는 산출물이 나온다면 같은 방향성으로 다른 산출물도 뽑아보고 해당 산출물도 의도에 맞게 뽑힌다면 그때 자동화 반영 진행해줘
```

## Research sequence

### Unit 7H — strategy sweep

Tested:

```text
A. face-down/back-side phone
B. side/edge view phone
C. featureless black glass front
D. strict front blank screen
```

Result:

```text
B side/edge view was the first success candidate; others failed due visible screen/UI/symbol/extra monitor drift.
```

### Unit 7I — side/edge reproduction

Generated:

```text
smartphone side/edge view
tablet_pc side/edge view
```

Result:

```text
Both had no UI/text/logo, but side/edge/screen-not-visible did not reliably reproduce; hardware/front screen remained visible. Do not automate side/edge as a strict rule.
```

### Unit 7K — rear panel strategy

Generated:

```text
rear smartphone / back panel / rear tablet
```

Result:

```text
Failed. Rear/back prompts confused the model into camera-like devices or still visible-screen artifacts.
```

### Unit 7L — realistic black/off screen policy

Reframed intent:

```text
Black/off screen is allowed to be visible.
Hardware bezel/button/notch is allowed.
No UI/text/logo/icon/status bar.
```

Result:

```text
tablet_pc candidate passed.
smartphone candidate failed due monitor/large display drift.
```

### Unit 7M — smartphone black-glass repeat

Prompt direction:

```text
small plain smartphone on wooden tabletop, black glass front, phone display off, dark reflective glass, single smartphone only, wooden_table, shadow, still_life, object_focus, no_humans, tabletop fills background, no logo, no icons, no app UI, no text, no monitor, no large display, simple modern item cut-in, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

Generated 3 seeds:

```text
360610719
360610720
360610721
```

Result:

```text
All 3 passed the realistic screen_device intent.
```

## Accepted screen_device policy

```text
screen_device_black_screen_safe
```

Definition:

```text
- The device front/black screen may be visible.
- Hardware bezel/button/notch/speaker marks are acceptable.
- No readable text, logo, app icon, UI, status bar, notification, or active app screen.
- Avoid extra monitor/large display/cup/keyboard/mouse/cable by prompt and negative.
- Prefer tabletop-only background.
```

## Automation reflection criteria

Criteria were satisfied:

```text
1. Found an intended-output direction: Unit 7M smartphone black-glass repeat.
2. Repeated same direction across multiple seeds: 3/3 smartphone seeds passed.
3. Same direction produced another screen-device output: Unit 7L tablet_pc passed under black/off screen policy.
```

Proceed to automate only this verified direction, not the failed rear/side strict policies.
