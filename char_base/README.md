### 🧍‍♀️ 0. 캐릭터 앵커 제작 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, nude, medium_breasts, cowboy_shot, standing, facing_viewer, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, {헤어 길이}, {헤어 스타일}, {머리색}, {눈색}, grey_background

```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, close-up, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), shadow, depth_of_field

```

#### 2. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다. 런타임 placeholder 선택지로만 사용하고, 태그를 더 넣기 위해 canonical JSON prompt를 다시 쓰지 않습니다.

- 머리 길이: `short_hair`, `medium_hair`, `long_hair`, `very_long_hair`
- 헤어스타일: `straight_hair`, `wavy_hair`, `bob_cut`, `ponytail`, `side_ponytail`, `twintails`, `braid`, `blunt_bangs`, `sidelocks`
- 머리색: `black_hair`, `brown_hair`, `blonde_hair`, `pink_hair`, `blue_hair`, `white_hair`, `two-tone_hair`
- 눈색: `brown_eyes`, `blue_eyes`, `green_eyes`, `red_eyes`, `purple_eyes`
- 중립 앵커 신체/구도: `cowboy_shot`, `standing`, `facing_viewer`, `looking_at_viewer`, `expressionless`, `closed_mouth`, `arms_at_sides`, `grey_background`
- negative crop 억제: `cropped`, `close-up`

앵커 규칙: 이 workflow는 중립적으로 유지합니다. 앵커 자체를 의도적으로 바꾸는 경우가 아니라면 분위기/동작/조명 태그를 추가하지 않습니다.

