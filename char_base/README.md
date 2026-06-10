## 문서 규격(v1)

- workflow_id: `char_base`
- modality: `image`
- input_requirement: 없음
- output: opaque character base/outfit variant PNG
- prompt_policy: `danbooru_sqlite+readme_wrapper`
- editable_fields: 3.inputs.text, 4.inputs.text, 5.inputs.width, 5.inputs.height, 6.inputs.seed, 6.inputs.steps, 6.inputs.cfg, 8.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🧍‍♀️ 0. 캐릭터 베이스 / 의상 베이스 제작 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, medium_breasts, cowboy_shot, standing, facing_viewer, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, {캐릭터 특징(연령대, 헤어스타일, 머리길이, 머리색, 눈매, 눈색)}, {의상 디테일(의상 이름, 색상_의상종류)}, grey_background
```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, close-up, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), shadow, depth_of_field
```

#### 2. Same-seed outfit variant 규칙

1. 먼저 기준 캐릭터 후보를 제작합니다.
2. 기준 캐릭터 후보의 시드값과 캐릭터 특징을 그대로 사용합니다.
3. `{의상 디테일}` block만 DB 검증된 의상 tag 묶음으로 교체합니다.
4. 후보별 filename_prefix는 고유하게 바꿉니다.
5. 얼굴/머리/체형/손/의상 반영을 QA합니다.

고정하는 것:
- 기준 후보와 동일한 시드값
- `masterpiece`, `best_quality`, `amazing_quality`, `4k`, `very_aesthetic`, `high_resolution`, `ultra-detailed`, `absurdres`, `newest`, `1girl`, `solo`, `medium_breasts`, `cowboy_shot`, `standing`, `facing_viewer`, `looking_at_viewer`
- `expressionless`, `closed_mouth`, `arms_at_sides`
- 기준 후보와 동일한 캐릭터 특징

바꾸는 것:
- `{의상 디테일(의상 이름, 색상_의상종류)}`
- `SaveImage.inputs.filename_prefix`

주의:
- 의상만 바꾸고 얼굴/머리 identity는 바꾸지 않습니다.
- 의상 slot에 표정, 카메라, 배경, 성격 단어를 섞지 않습니다.
- 손 주변에 소품/가방이 생기면 먼저 `arms_at_sides`를 유지하고 seed 후보를 봅니다. 무리하게 negative를 넓히지 않습니다.
- 어깨/다리 노출 태그(`bare_shoulders`, `bare_legs`)를 쓸 때는 의상 레이어 태그(`dress`, `shirt`, `skirt`, `gloves`)를 함께 명시합니다.

#### 3. 의상 프롬프트 리스트 (canonical 예시)

Positive prompt의 `{의상 디테일}` 자리에 아래 텍스트를 넣습니다.
원칙: `{의상 이름, 색상_의상종류}` 중심으로 짧고 고정된 block을 우선 사용합니다.
모든 variable outfit tag는 로컬 Danbooru taxonomy SQLite tag oracle 기준으로 검증합니다.

아래 5세트는 현재 char_base same-seed 비교에 자주 쓰는 canonical 예시입니다.

**1) school_uniform**
```text
school_uniform, white_shirt, brown_cardigan, blue_skirt, brown_pantyhose
```

**2) summer_sundress**
```text
sundress, white_dress, floral_print, sleeveless, sandals
```

**3) winter_coat**
```text
winter_clothes, black_coat, white_sweater, jeans, boots
```

**4) armor_knight**
```text
armor, breastplate, white_tunic, gauntlets, armored_boots
```

**5) witch_mage**
```text
witch, purple_cape, black_corset, long_skirt, pendant
```

확장 후보(선택):
- 위 5세트 QA가 안정적일 때만 tag를 1~2개씩 추가합니다.
- 한 번에 다층 태그를 늘리지 않습니다.
- 예: `frills`, `belt`, `gloves`, `leather`, `wool` 같은 재질/디테일 tag는 A/B로만 추가합니다.

주의:
- `black_kneehighs`, `black_boots`는 local DB 미검증이므로 기본 세트에서 사용하지 않습니다.
- 의상 block에는 표정/카메라/배경 tag를 넣지 않습니다.
- 예시 목록 확장/수정은 소규모 QA(최소 same-seed 3~5장) 후 반영합니다.

#### 4. 검증된 Danbooru SQLite 태그 메모

출처: 로컬 Danbooru taxonomy SQLite tag oracle. 아래 태그들은 runtime placeholder 선택지로만 사용하고, 태그를 더 넣기 위해 장황하게 prompt를 늘리지 않습니다.

현재 char_base 기본 템플릿은 `1girl, solo` 기준이므로 여성 캐릭터 생성만 지원합니다.

- 연령대(여): `loli`, `mature_female`, `old_woman`
- 머리 길이: `short_hair`, `medium_hair`, `long_hair`, `very_long_hair`
- 헤어스타일: `straight_hair`, `wavy_hair`, `bob_cut`, `ponytail`, `side_ponytail`, `twintails`, `braid`, `blunt_bangs`, `sidelocks`
- 머리색: `black_hair`, `brown_hair`, `blonde_hair`, `pink_hair`, `blue_hair`, `white_hair`, `two-tone_hair`
- 눈매: `tsurime`, `tareme`, `upturned_eyes`, `downturned_eyes`
- 눈색: `brown_eyes`, `blue_eyes`, `green_eyes`, `red_eyes`, `purple_eyes`
- 중립 구도: `cowboy_shot`, `standing`, `facing_viewer`, `looking_at_viewer`, `expressionless`, `closed_mouth`, `arms_at_sides`, `grey_background`
- 상의/카라: `shirt`, `white_shirt`, `blouse`, `sweater`, `cardigan`, `blazer`, `jacket`, `hoodie`, `collared_shirt`, `sailor_collar`
- 소매: `long_sleeves`, `short_sleeves`, `sleeveless`
- 하의: `skirt`, `pleated_skirt`, `plaid_skirt`, `shorts`, `pants`, `dress`
- 다리 의상/신발: `kneehighs`, `thighhighs`, `pantyhose`, `socks`, `loafers`, `boots`, `sneakers`
- 악세서리/디테일: `ribbon`, `necktie`, `bow`, `belt`, `gloves`, `hat`, `frills`, `lace`, `buttons`, `zipper`
- 재질: `fabric`, `silk`, `leather`, `denim`, `wool`

앵커 규칙: 이 workflow는 캐릭터 기준 이미지를 만드는 곳입니다. 분위기/동작/조명 태그를 늘리기보다, 같은 seed와 검증된 identity/outfit tag 조합으로 작은 후보를 뽑고 QA로 고릅니다.
