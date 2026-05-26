## 문서 규격(v1)

- workflow_id: `char_expression`
- modality: `image`
- input_requirement: source character image 필요
- output: expression variant PNG
- prompt_policy: `danbooru_csv+readme_wrapper`
- editable_fields: 1.inputs.image, 6.inputs.text, 7.inputs.text, 13.inputs.seed, 13.inputs.denoise, 19.inputs.filename_prefix, 5.inputs.mask_blur, 5.inputs.mask_offset, 1000.inputs.model_name, 1002.inputs.threshold, 1002.inputs.crop_factor, 1003.inputs.detection_hint, 1003.inputs.threshold

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🎭 0. 감정 표현 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, nude, medium_breasts, cowboy_shot, standing, facing_viewer, looking_at_viewer, arms_at_sides, {캐릭터 원본 특징(헤어 길이, 헤어 스타일, 머리색, 눈색)}, {감정표현}, BREAK, depth_of_field, volumetric_lighting

```

캐릭터 원본 특징 guard:
- `헤어 길이, 헤어 스타일, 머리색, 눈색`은 반드시 입력 source/승인된 캐릭터 metadata에서 가져옵니다.
- 임의로 다른 특징을 넣지 않습니다. 이전 이미지와 다른 특징을 넣으면 같은 캐릭터 표정 variant가 아니라 새 캐릭터처럼 drift할 수 있습니다.
- 위 code block은 ComfyUI에 들어가는 실제 prompt contract이므로 `{캐릭터 원본 특징(...)}` 같은 한국어 라벨은 넣지 않습니다. 라벨은 이 guard 문단에서만 읽고, 실제 prompt에는 검증된 Danbooru tag만 넣습니다.

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, lowres, bad_anatomy, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), {상극 감정표현}

```

#### 2. 감정표현 리스트 (Positive / Negative 세트)

*(※ 긍정 프롬프트의 `{감정표현}` 자리와 부정 프롬프트의 `{상극 감정표현}` 자리에 아래의 세트를 각각 복사해서 넣으세요.)*

**1) 기쁨 (Happy)**

* **Positive:** `happy, smile, open_mouth, sparkling_eyes, light_blush`
* **Negative:** `sad, angry, crying, tears, disgusted, expressionless`

**2) 슬픔 (Sad)**

* **Positive:** `sad, tears, frown`
* **Negative:** `happy, smile, laugh, angry, smug, sparkling_eyes`

**3) 놀람 (Surprised)**

* **Positive:** `surprised, wide_eyed, open_mouth`
* **Negative:** `sleepy, expressionless, angry, happy, closed_eyes`

**4) 공포 (Scared)**

* **Positive:** `scared, wide_eyed, constricted_pupils, pale_skin, sweatdrop`
* **Negative:** `happy, smile, relaxed, confident, smug`

**5) 혐오 (Disgusted)**

* **Positive:** `disgusted, scowl, frown`
* **Negative:** `happy, smile, blush, excited, heart-shaped_pupils, sparkling_eyes`

**6) 무표정 (Expressionless)**

* **Positive:** `expressionless, closed_mouth, blank_stare`
* **Negative:** `smile, sad, angry, surprised, open_mouth, blush, tears`

**7) 과부하 (Flustered)**

* **Positive:** `blush, flustered, sweatdrop, nervous_smile`
* **Negative:** `expressionless, confident, angry, pale_skin`

**8) 황홀 (Dazed)**

* **Positive:** `heart-shaped_pupils, blush, open_mouth, dazed, tongue_out`
* **Negative:** `sad, angry, disgusted, scared, pale_skin, expressionless`

**9) 울먹임 (Crying)**

* **Positive:** `tears, crying, frown`
* **Negative:** `happy, smile, laugh, smug, confident, sparkling_eyes`

**10) 분노/굴욕 (Angry)**

* **Positive:** `angry, glare, furrowed_brow, clenched_teeth`
* **Negative:** `happy, smile, laugh, sad, expressionless, blush`

**11) 멘탈붕괴 (Mental Breakdown)**

* **Positive:** `expressionless, empty_eyes, hollow_eyes, pale_skin, open_mouth`
* **Negative:** `happy, smile, angry, sparkling_eyes, light_blush, confident`

**12) 우쭐함 (Smug)**

* **Positive:** `smug, smirk, raised_eyebrows`
* **Negative:** `sad, crying, scared, flustered, pale_skin, wide_eyed`

#### 3. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다. 제작자 추천 wrapper prompt는 CSV 예외로 보존하고, `{감정표현}` / `{상극 감정표현}`에 들어가는 variable 태그만 CSV에 실제 존재하는 태그로 제한합니다. `{감정표현}` / `{상극 감정표현}`에는 얼굴에 영향을 주는 태그만 넣고, 의상/배경/카메라 태그는 expression patch에 넣지 않습니다.

- 감정 기준 태그: `happy`, `sad`, `angry`, `surprised`, `scared`, `embarrassed`, `flustered`, `smug`, `crying`, `expressionless`
- 눈/동공: `sparkling_eyes`, `empty_eyes`, `hollow_eyes`, `constricted_pupils`, `closed_eyes`
- 입: `closed_mouth`, `open_mouth`, `smile`, `frown`, `smirk`, `wavy_mouth`, `clenched_teeth`, `parted_lips`
- 얼굴 효과: `blush`, `light_blush`, `tears`, `sweatdrop`, `pale_skin`

표정 규칙: 이 workflow는 YOLO+SAM 얼굴 마스크 영역만 inpaint/composite하므로 `{감정표현}` / `{상극 감정표현}`에는 눈, 눈썹, 입, 홍조, 눈물처럼 얼굴 마스크 안에서 해결되는 태그만 넣습니다. 고개 방향, 몸동작, 손동작, 의상, 배경, 카메라 구도 변화가 필요한 감정 연기는 `scene_event_cg`에서 처리합니다.

