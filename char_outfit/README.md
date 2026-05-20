### 👗 0. 의상 변경 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, medium_breasts, cowboy_shot, standing, facing_viewer, looking_at_viewer, expressionless, closed_mouth, arms_at_sides, open_hands, {헤어 길이}, {헤어 스타일}, {머리색}, {눈색}, {의상 디테일(상의, 하의, 신발, 악세서리)}, grey_background

```

**Negative prompt:**

```text
nude, nipples, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), shadow, depth_of_field

```

#### 2. 의상 프롬프트 리스트 (단부루 표준 규격)

*(※ Positive prompt의 `{의상 디테일}` 자리에 아래 텍스트를 그대로 복사해서 넣으세요.)*

**1) 교복 (School Uniform)**

* **하복 (세일러복 스타일):**
`school_uniform, serafuku, white_shirt, short_sleeves, sailor_collar, blue_ribbon, pleated_skirt, blue_skirt, white_socks, ankle_socks, loafers, brown_footwear, fabric`
* **동복 (블레이저 스타일):**
`school_uniform, black_blazer, open_jacket, white_shirt, collared_shirt, red_necktie, cardigan, plaid_skirt, pleated_skirt, black_pantyhose, loafers, black_footwear, wool`

**2) 일상복 / 데이트룩 (Casual / Date Outfit)**

* **봄/가을 (포근한 니트룩):**
`casual, sweater, off_shoulder, denim_shorts, black_shorts, tights, ankle_boots, brown_footwear, scarf, loose_clothes`
* **여름 (시원한 원피스룩):**
`sundress, white_dress, floral_print, sleeveless, frills, straw_hat, sandals, belt, fabric`
* **겨울 (코트룩):**
`winter_clothes, trench_coat, black_coat, white_sweater, turtleneck_sweater, jeans, boots, black_gloves, leather_gloves, wool`

**3) 판타지 / 이세계 (Fantasy / RPG)**

* **기사/전사 (Knight/Fighter):**
`armor, breastplate, white_tunic, corset, leather_belt, gauntlets, armored_boots, thigh_boots, red_cape, leather`
* **마법사/마녀 (Mage/Witch):**
`witch, witch_hat, purple_cape, black_corset, long_skirt, black_boots, pendant`

**4) 특별 이벤트 / 파티 (Formal / Party)**

* **우아한 이브닝 드레스:**
`evening_dress, black_dress, bare_shoulders, long_dress, side_slit, frills, lace, high_heels, pearl_necklace, gloves, silk`

**5) 실내복 / 잠옷 (Sleepwear / Loungewear)**

* **오버사이즈 셔츠 (루즈핏/하의실종):**
`sleepwear, oversized_shirt, white_shirt, unbuttoned, open_shirt, bare_legs, white_shorts, slippers, loose_clothes`
* **귀여운 파자마:**
`pajamas, pink_pajamas, long_sleeves, pants, frills, sleep_mask, silk`

#### 3. 의상 프롬프팅 추가 팁 (단부루 태그)

* **재질 태그:** `fabric` (기본 옷감), `silk` (실크), `leather` (가죽), `denim` (청재질), `wool` (겨울/울 소재)
* **형태와 핏 태그:** `loose_clothes` (헐렁한 옷), `oversized_clothes` (오버사이즈), `pleated_skirt` (주름치마)
* **포인트 디테일:** `frills` (프릴/주름장식), `lace` (레이스), `ribbon` (리본), `zipper` (지퍼), `buttons` (단추)
* **손/소품 억제:** 교복/일상복에서 손 주변에 가방·소품이 생기면 negative의 `holding`/`carrying` 단독 추가보다 Positive prompt의 `open_hands`가 더 안정적이었습니다. 기본 자세 태그 `arms_at_sides`와 함께 유지합니다.
* **특수 노출 (주의점):** 어깨나 다리 노출 태그(`bare_shoulders`, `bare_legs` 등)를 넣을 때는 negative의 `nude`, `nipples`를 유지하고, 의상 레이어 태그(`dress`, `shirt`, `skirt`, `gloves` 등)를 함께 명시합니다.

#### 4. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다. `{의상 디테일}`은 모호한 분위기 단어보다 안정적인 의상 레이어 태그로 구성합니다.

- 상의/카라: `shirt`, `white_shirt`, `blouse`, `sweater`, `cardigan`, `blazer`, `jacket`, `hoodie`, `collared_shirt`, `sailor_collar`
- 소매: `long_sleeves`, `short_sleeves`, `sleeveless`
- 하의: `skirt`, `pleated_skirt`, `plaid_skirt`, `shorts`, `pants`, `dress`
- 다리 의상/신발: `kneehighs`, `thighhighs`, `pantyhose`, `socks`, `loafers`, `boots`, `sneakers`
- 악세서리/디테일: `ribbon`, `necktie`, `bow`, `belt`, `gloves`, `hat`, `frills`, `lace`, `buttons`, `zipper`
- 자세/손: `arms_at_sides`, `open_hands`
- 유용한 색상/재질 기준 태그: `denim`, `leather`, `fabric`, `silk`, `wool`, `white_shirt`, `red_ribbon`

의상 규칙: source 보존이 중요하면 `white_shirt`, `red_ribbon`, `blue_skirt`처럼 의상 색을 명시합니다. 얼굴/머리 identity 태그는 승인된 source prompt에서 이어받습니다.

