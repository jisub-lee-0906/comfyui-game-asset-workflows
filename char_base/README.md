## 문서 규격(v1)

- workflow_id: `char_base`
- modality: `image`
- input_requirement: 없음
- output: opaque character base/outfit variant PNG
- prompt_policy: `danbooru_csv+readme_wrapper`
- editable_fields: 3.inputs.text, 4.inputs.text, 5.inputs.width, 5.inputs.height, 6.inputs.seed, 6.inputs.steps, 6.inputs.cfg, 8.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🧍‍♀️ 0. 캐릭터 베이스 / 의상 베이스 제작 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, medium_breasts, cowboy_shot, standing, facing_viewer, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, {캐릭터 특징(헤어 길이, 헤어 스타일, 머리색, 눈색)}, {의상 디테일(상의, 하의, 신발, 악세서리)}, grey_background
```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, close-up, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), shadow, depth_of_field
```

#### 2. Same-seed outfit variant 규칙

1. 먼저 기준 캐릭터 후보를 제작합니다.
2. 기준 캐릭터 후보의 시드값과 캐릭터 특징을 그대로 사용합니다.
3. `{의상 디테일}` block만 CSV 검증된 의상 tag 묶음으로 교체합니다.
4. 후보별 filename_prefix는 고유하게 바꿉니다.
5. 얼굴/머리/체형/손/의상 반영을 QA합니다.

고정하는 것:
- 기준 후보와 동일한 시드값
- `masterpiece`, `best_quality`, `amazing_quality`, `4k`, `very_aesthetic`, `high_resolution`, `ultra-detailed`, `absurdres`, `newest`, `1girl`, `solo`, `medium_breasts`, `cowboy_shot`, `standing`, `facing_viewer`, `looking_at_viewer`
- `expressionless`, `closed_mouth`, `arms_at_sides`
- 기준 후보와 동일한 캐릭터 특징

바꾸는 것:
- `{의상 디테일(상의, 하의, 신발, 악세서리)}`
- `SaveImage.inputs.filename_prefix`

주의:
- 의상만 바꾸고 얼굴/머리 identity는 바꾸지 않습니다.
- 의상 slot에 표정, 카메라, 배경, 성격 단어를 섞지 않습니다.
- 손 주변에 소품/가방이 생기면 먼저 `arms_at_sides`를 유지하고 seed 후보를 봅니다. 무리하게 negative를 넓히지 않습니다.
- 어깨/다리 노출 태그(`bare_shoulders`, `bare_legs`)를 쓸 때는 의상 레이어 태그(`dress`, `shirt`, `skirt`, `gloves`)를 함께 명시합니다.

#### 3. 의상 프롬프트 리스트 (단부루 표준 규격)

Positive prompt의 `{의상 디테일}` 자리에 아래 텍스트를 그대로 넣을 수 있습니다.
모든 variable outfit tag는 루트 `danbooru_tag.csv` 기준으로 검증합니다.

**교복 / School Uniform**

하복 세일러복:
```text
school_uniform, serafuku, white_shirt, short_sleeves, sailor_collar, blue_ribbon, pleated_skirt, blue_skirt, white_socks, ankle_socks, loafers, brown_footwear, fabric
```

동복 블레이저:
```text
school_uniform, black_blazer, open_jacket, white_shirt, collared_shirt, red_necktie, cardigan, plaid_skirt, pleated_skirt, black_pantyhose, loafers, black_footwear, wool
```

검증된 기본값:
```text
school_uniform, white_shirt, necktie, pleated_skirt, cardigan
```

**일상복 / Date Outfit**

봄·가을 니트룩:
```text
casual, sweater, white_sweater, denim_shorts, black_shorts, tights, ankle_boots, brown_footwear, loose_clothes
```

여름 원피스:
```text
sundress, white_dress, floral_print, sleeveless, frills, straw_hat, sandals, belt, fabric
```

겨울 코트:
```text
winter_clothes, trench_coat, black_coat, white_sweater, turtleneck_sweater, jeans, boots, black_gloves, leather_gloves, wool
```

**판타지 / RPG**

기사/전사:
```text
armor, breastplate, white_tunic, corset, leather_belt, gauntlets, armored_boots, thigh_boots, red_cape, leather
```

마법사/마녀:
```text
witch, witch_hat, purple_cape, black_corset, long_skirt, black_boots, pendant
```

**이벤트 / 파티**

포멀 블랙 드레스:
```text
black_dress, bare_shoulders, long_dress, side_slit, frills, lace, high_heels, pearl_necklace, gloves, silk
```

주의: `evening_dress`는 README에 있던 표현이지만 현재 local CSV에서 빠져 있으므로 기본 추천 block에서는 제외합니다.

**실내복 / 잠옷**

오버사이즈 셔츠:
```text
sleepwear, oversized_shirt, white_shirt, unbuttoned, open_shirt, bare_legs, white_shorts, slippers, loose_clothes
```

파자마:
```text
pajamas, pink_pajamas, long_sleeves, pants, frills, sleep_mask, silk
```

#### 4. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 runtime placeholder 선택지로만 사용하고, 태그를 더 넣기 위해 장황하게 prompt를 늘리지 않습니다.

- 머리 길이: `short_hair`, `medium_hair`, `long_hair`, `very_long_hair`
- 헤어스타일: `straight_hair`, `wavy_hair`, `bob_cut`, `ponytail`, `side_ponytail`, `twintails`, `braid`, `blunt_bangs`, `sidelocks`
- 머리색: `black_hair`, `brown_hair`, `blonde_hair`, `pink_hair`, `blue_hair`, `white_hair`, `two-tone_hair`
- 눈색: `brown_eyes`, `blue_eyes`, `green_eyes`, `red_eyes`, `purple_eyes`
- 중립 구도: `cowboy_shot`, `standing`, `facing_viewer`, `looking_at_viewer`, `expressionless`, `closed_mouth`, `arms_at_sides`, `grey_background`
- 상의/카라: `shirt`, `white_shirt`, `blouse`, `sweater`, `cardigan`, `blazer`, `jacket`, `hoodie`, `collared_shirt`, `sailor_collar`
- 소매: `long_sleeves`, `short_sleeves`, `sleeveless`
- 하의: `skirt`, `pleated_skirt`, `plaid_skirt`, `shorts`, `pants`, `dress`
- 다리 의상/신발: `kneehighs`, `thighhighs`, `pantyhose`, `socks`, `loafers`, `boots`, `sneakers`
- 악세서리/디테일: `ribbon`, `necktie`, `bow`, `belt`, `gloves`, `hat`, `frills`, `lace`, `buttons`, `zipper`
- 재질: `fabric`, `silk`, `leather`, `denim`, `wool`

앵커 규칙: 이 workflow는 캐릭터 기준 이미지를 만드는 곳입니다. 분위기/동작/조명 태그를 늘리기보다, 같은 seed와 검증된 identity/outfit tag 조합으로 작은 후보를 뽑고 QA로 고릅니다.
