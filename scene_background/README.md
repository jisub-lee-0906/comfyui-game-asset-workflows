## 문서 규격(v1)

- workflow_id: `scene_background`
- modality: `image`
- input_requirement: 없음
- output: 16:9 background PNG
- prompt_policy: `danbooru_sqlite+readme_wrapper`
- editable_fields: 3.inputs.text, 4.inputs.text, 5.inputs.width, 5.inputs.height, 6.inputs.seed, 6.inputs.steps, 6.inputs.cfg, 8.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🖼️ 0. 배경 제작 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, scenery, no_humans, wide_shot, landscape, {배경 테마 및 장소}, {시간대 및 분위기 태그}, BREAK, depth_of_field, volumetric_lighting, BREAK, {짧은 자연어 semantic_prompt/style_prompt if needed}

```

자동화 주의: `hallway`, `window`, `night`처럼 일반 tag만 넣으면 학교/병원 같은 범용 복도로 drift할 수 있습니다. 귀족 저택, 성, 고딕 실내, 특정 재질/건축 양식처럼 tag만으로 부족한 장소 의도는 `semantic_prompt`/`style_prompt`에 짧은 자연어로 넣어 live prompt에 반영합니다.

프롬프트 주의: background live prompt에는 `visual novel setting`, `dialogue overlay`, `text box`, `caption`처럼 VN UI/자막을 연상시키는 표현을 넣지 않습니다. Unit 6D 현대 침실 smoke에서 이런 표현이 하단 black subtitle bar와 fake text를 유도했습니다. VN에서 쓸 배경이라는 의도는 `visual_brief`/metadata에 남기고, live prompt는 `empty modern bedroom background`, `clean full-frame interior`, `open central wall and floor space`처럼 순수 배경 묘사로 유지합니다. fake caption/letterbox가 생기면 `negative_tags`에 `caption`, `letterboxed`, `black_border`, `text_focus`를 추가합니다.

**Negative prompt:**

```text
1girl, 1boy, crowd, people, silhouette, monster, animal, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, ugly, lowres, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, simple_background, (worst_quality, bad_quality:1.2)

```

#### 2. 배경 리스트 (태그 조합용)

**[ 배경 테마 및 장소 ]**

**1) 학교 (School)**

* **교실:** `school, classroom, desk, chair, chalkboard, window`
* **복도:** `school, hallway, locker, window, wooden_floor`
* **학교 옥상:** `school, rooftop, fence, blue_sky`
* **교문/등굣길:** `school, cherry_blossoms, road, street`

**2) 일상 / 집 (Home / Daily)**

* **주인공/히로인 방:** `indoors, bedroom, bed, desk, computer, bookshelf`
* **거실:** `indoors, living_room, television, coffee_table, window`
* **동네 길거리:** `outdoors, street, utility_pole, houses, sidewalk`
* **공원:** `outdoors, park, bench, tree, grass, path`

**3) 판타지 / 이세계 (Fantasy)**

* **판타지 마을:** `outdoors, town, street, house`
* **신비로운 숲:** `outdoors, forest, mushroom, tree`
* **마왕성 / 서재:** `indoors, castle, gothic_architecture, library, bookshelf, candelabra`

**[ 시간대 및 분위기 태그 ]**

* **낮 (Day):** `day, sunlight, clear_sky`
* **노을/저녁 (Sunset):** `sunset, golden_hour, orange_sky, shadow`
* **밤 (Night):** `night, starry_sky, moonlight, dark`
* **새벽/비 (Atmosphere):** `morning, fog` 또는 `rain, overcast`

#### 3. 검증된 Danbooru SQLite 태그 메모

출처: 로컬 Danbooru taxonomy SQLite tag oracle. 아래 태그들은 README에 적기 전에 DB에서 active/non-deprecated로 확인했습니다. `{배경 테마 및 장소}`와 `{시간대 및 분위기 태그}`를 런타임에서 패치할 때 사용합니다.

- 장면 기본 태그: `scenery`, `no_humans`, `indoors`, `outdoors`
- 장소: `classroom`, `school`, `hallway`, `rooftop`, `bedroom`, `living_room`, `street`, `park`, `forest`, `library`
- 장면 오브젝트: `window`, `bookshelf`, `bench`, `utility_pole`
- 구도/시간/날씨: `wide_shot`, `depth_of_field`, `day`, `sunset`, `night`, `rain`, `overcast`, `fog`, `snow`
- 조명/분위기: `sunlight`, `moonlight`

배경 규칙: 사람이 있는 배경을 의도적으로 테스트하는 경우가 아니라면 `no_humans`와 사람/캐릭터 관련 negative를 유지합니다.

