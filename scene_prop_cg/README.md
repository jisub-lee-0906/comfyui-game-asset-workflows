## 문서 규격(v1)

- workflow_id: `scene_prop_cg`
- modality: `image`
- input_requirement: 없음
- output: 16:9 prop CG PNG
- prompt_policy: `danbooru_sqlite+readme_wrapper`
- editable_fields: 3.inputs.text, 4.inputs.text, 5.inputs.width, 5.inputs.height, 6.inputs.seed, 6.inputs.steps, 6.inputs.cfg, 8.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🔍 0. 소품 클로즈업 CG 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt 기본형:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, {아이템 이름 및 형태}, {재질 및 질감 디테일}, {놓여있는 장소/배경}, BREAK, depth_of_field, BREAK, {짧은 자연어 semantic_prompt/style_prompt if needed}

```

**검증된 prompt shape 정책:**

`novaAnimeXL_ilV190` 실험(Unit 7F~7M) 기준으로 `scene_prop_cg`는 단일 wrapper보다 소품 class별 shape가 안정적입니다.

```text
quality_first_wrapper:
  기본값. 문서/종이처럼 반복하면 여러 장으로 분열되는 소품에 사용.

object_first_compact:
  열쇠/반지/병/칼처럼 단순 물리 소품에 사용. target object를 맨 앞에 둠.

screen_device_black_screen_safe:
  스마트폰/태블릿 화면 소품에 사용. black/off reflective screen은 허용하고, UI/text/logo/status bar를 금지. hardware bezel/button/notch/speaker mark는 허용.
```

검증된 screen-device 예시:

```text
small plain smartphone on wooden tabletop, featureless empty black glass front, display powered off, completely blank dark reflective glass surface, single smartphone only, wooden_table, shadow, still_life, object_focus, no_humans, tabletop fills background, no logo, no icons, no app UI, no text, no corner marks, no colored marks, no monitor, no large display, simple modern item cut-in, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution
```

자동화 주의: `letter`, `envelope`, `blank_page`처럼 generic object tag만 넣으면 일반 봉투/편지로 drift할 수 있습니다. 붉은 마법 계약서, 단서, 저주받은 반지처럼 story identity가 중요한 소품은 `semantic_prompt`/`style_prompt`를 짧게 넣어 live prompt에 반영합니다. 소품별로 피해야 할 것이 명확하면 `extra_negative_prompt`를 추가합니다. 예: 열쇠 후보는 `lock, box, book, extra objects`; 스마트폰 후보는 `logo, icon, app ui, text, monitor, large display`.

**Negative prompt:**

```text
1girl, 1boy, cropped, out_of_frame, duplicate, close-up, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, lowres, bad_anatomy, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, (worst_quality, bad_quality:1.2), fake_text, logo, label, screenshot, dialogue_box, caption

```

#### 2. 단서 리스트 적용 예시 (단부루 표준 규격)

*(※ Positive prompt의 `{아이템 이름 및 형태}`, `{재질 및 질감 디테일}` 자리에 복사해서 넣으세요.)*

**1) 낡은 문서나 편지, 책 (종이 질감)**

* **아이템 및 형태:** `diary, letter, crumpled_paper, open_book, envelope, leather, blank_page`
* **재질 및 질감:** `paper, blank_page`
* **적용 예시:** `... object_focus, diary, leather, paper, blank_page, wooden_table, BREAK, depth_of_field ...`

**2) 열쇠, 반지, 펜던트 (금속/보석 질감)**

* **아이템 및 형태:** `key, pocket_watch, glowing, ring, broken_glass, vial`
* **재질 및 질감:** `scratches`, `rust`, `glowing`, `reflective`
* **적용 예시:** `... object_focus, key, scratches, wooden_table, shadow, BREAK, depth_of_field, BREAK, old brass key prop, worn metal surface ...`

**3) 현대 기기 (스마트폰, USB 등)**

* **아이템 및 형태:** `cracked_screen`, `smartphone`, `screen`
* **재질 및 질감:** `glass`, `fingerprint`, `glowing`
* **적용 예시:** `... object_focus, smartphone, screen, glass, desk, shadow, BREAK, depth_of_field, BREAK, blank black screen, screen turned off, no logo, no icons ...`

**4) 무기류 (칼, 총기 등)**

* **아이템 및 형태:** `knife, kitchen_knife, revolver, broken_sword, sword_hilt`
* **재질 및 질감:** `dried_blood, blood`
* **적용 예시:** `... object_focus, knife, kitchen_knife, blood, dried_blood, table, BREAK, depth_of_field ...`

#### 3. 검증된 Danbooru SQLite 태그 메모

출처: 로컬 Danbooru taxonomy SQLite tag oracle. 아래 태그들은 README에 적기 전에 DB에서 active/non-deprecated로 확인했습니다. 오브젝트/재질/카메라 태그를 사용하고, 스토리상 텍스트 artifact 테스트가 꼭 필요한 경우가 아니라면 읽을 수 있는 글자는 피합니다.

- 카메라/오브젝트 초점: `still_life`, `object_focus`, `close-up`
- 자주 쓰는 소품 오브젝트: `key`, `ring`, `pendant`, `smartphone`, `letter`, `open_book`, `knife`, `pocket_watch`
- 디테일/상태 태그: `cracked_screen`, `hilt`, `rust`, `blood`, `scratches`
- 표면/조명: `wooden_table`, `desk`, `shadow`, `depth_of_field`, `blurry_background`
- DB에서 확인된 텍스트/UI negative: `signature`, `watermark`, `logo`, `label`, `caption`, `speech_bubble`

소품 규칙: 편지/책/화면은 최종 텍스트를 ComfyUI 밖에서 합성할 계획이 아니라면 빈 디자인이나 읽을 수 없는 디자인을 우선합니다. `single_object`처럼 "단일 소품만"을 직접 뜻하는 Danbooru 태그는 현재 로컬 Danbooru taxonomy SQLite에서 정확 태그로 검증되지 않으므로, 단일 소품 구도는 `no_humans`, `still_life`, `object_focus`와 seed/settings/후보 선택으로 유도합니다. 소품이 잘리면 `close-up`처럼 과한 근접을 유도하는 태그를 줄입니다.

#### 4. 운영 가이드

- `key`는 단일 단서 소품 후보로 안정적인 편입니다.
- `ring`은 단일 소품으로는 가능하지만 보석 장식이 커져 bracelet/ornamental object처럼 보일 수 있으므로 seed 후보를 여러 장 뽑습니다.
- `pocket_watch`는 단서 분위기는 좋지만 문자판/뚜껑/체인 때문에 화면상 여러 물체처럼 분리될 수 있습니다. 단일 소품 기준에서는 QA 후보로만 봅니다.
- 문서, 책, 편지, 스마트폰 화면, 시계 문자판처럼 텍스트/기호가 들어가기 쉬운 소품은 fake text 여부를 반드시 확인합니다.
- 단순 금속/보석/병/칼/크리스탈류는 상대적으로 안전한 첫 후보입니다.
- 읽을 수 있는 정보가 필요한 단서는 ComfyUI에서 직접 생성하지 말고 빈 소품을 만든 뒤 Ren'Py/후편집으로 텍스트를 합성합니다.

