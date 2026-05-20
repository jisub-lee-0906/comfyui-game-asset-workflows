### 🎭 0. 감정 표현 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, nude, medium_breasts, cowboy_shot, standing, front_view, looking_at_viewer, straight_posture, arms_at_sides, {헤어 길이}, {헤어 스타일}, {머리색}, {눈색}, {감정표현}, BREAK, depth_of_field, volumetric_lighting

```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, lowres, bad_anatomy, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, changed_clothes, different_clothes, different_hair, (worst_quality, bad_quality:1.2), {상극 감정표현}

```

#### 2. 감정표현 리스트 (Positive / Negative 세트)

*(※ 긍정 프롬프트의 `{감정표현}` 자리와 부정 프롬프트의 `{상극 감정표현}` 자리에 아래의 세트를 각각 복사해서 넣으세요.)*

**1) 기쁨 (Happy)**

* **Positive:** `happy, smile, open_mouth, sparkling_eyes, light_blush`
* **Negative:** `sad, angry, crying, tears, disgusted, expressionless`

**2) 슬픔 (Sad)**

* **Positive:** `sad, watery_eyes, tears, quivering_lips, slanted_eyebrows`
* **Negative:** `happy, smile, laugh, angry, smug, sparkling_eyes`

**3) 놀람 (Surprised)**

* **Positive:** `surprised, wide_eyed, open_mouth, gasped`
* **Negative:** `calm, sleepy, expressionless, angry, happy, closed_eyes`

**4) 공포 (Scared)**

* **Positive:** `scared, constricted_pupils, pale_skin, trembling, sweat_drop`
* **Negative:** `calm, happy, smile, relaxed, confident, smug`

**5) 혐오 (Disgusted)**

* **Positive:** `disgusted, scowl, turned_away, frown`
* **Negative:** `happy, smile, blush, excited, heart-shaped_pupils, sparkling_eyes`

**6) 무표정 (Expressionless)**

* **Positive:** `expressionless, closed_mouth, blank_stare`
* **Negative:** `smile, sad, angry, surprised, open_mouth, blush, tears`

**7) 과부하 (Flustered)**

* **Positive:** `heavy_blush, flustered, trembling, teardrop, nervous_smile`
* **Negative:** `calm, expressionless, confident, angry, pale_skin`

**8) 황홀 (Dazed)**

* **Positive:** `heart-shaped_pupils, heavy_blush, open_mouth, dazed, tongue_out`
* **Negative:** `sad, angry, disgusted, scared, pale_skin, expressionless`

**9) 울먹임 (Crying)**

* **Positive:** `tears, crying, upset, quivering_lips, watery_eyes`
* **Negative:** `happy, smile, laugh, smug, confident, sparkling_eyes`

**10) 분노/굴욕 (Angry)**

* **Positive:** `angry, glare, furrowed_brow, tight_lips, indignant`
* **Negative:** `happy, smile, laugh, sad, calm, expressionless, blush`

**11) 멘탈붕괴 (Mental Breakdown)**

* **Positive:** `expressionless, empty_eyes, hollow_eyes, pale_skin, agape`
* **Negative:** `happy, smile, angry, sparkling_eyes, light_blush, confident`

**12) 우쭐함 (Smug)**

* **Positive:** `smug, smirk, raised_eyebrows`
* **Negative:** `sad, crying, scared, flustered, pale_skin, wide_eyed`

#### 3. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다. `{감정표현}` / `{상극 감정표현}`에는 얼굴에 영향을 주는 태그만 넣고, 의상/배경/카메라 태그는 expression patch에 넣지 않습니다.

- 감정 기준 태그: `happy`, `sad`, `angry`, `surprised`, `scared`, `embarrassed`, `flustered`, `smug`, `crying`, `expressionless`
- 눈/동공: `sparkling_eyes`, `empty_eyes`, `hollow_eyes`, `constricted_pupils`, `closed_eyes`
- 입: `closed_mouth`, `open_mouth`, `smile`, `frown`, `smirk`, `wavy_mouth`, `clenched_teeth`, `parted_lips`
- 얼굴 효과: `blush`, `light_blush`, `tears`, `sweatdrop`, `pale_skin`

표정 규칙: 태그가 포즈/의상/배경/카메라 구도를 바꿀 가능성이 있으면 이 workflow에 넣지 말고 `scene_event_cg`를 사용합니다.

