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
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, scenery, no_humans, wide_shot, landscape, {배경 테마 및 장소}, {시간대 및 분위기 태그}, BREAK, depth_of_field, BREAK, {짧은 자연어 semantic_prompt/style_prompt if needed}

```

자동화 주의: `hallway`, `window`, `night`처럼 일반 tag만 넣으면 학교/병원 같은 범용 복도로 drift할 수 있습니다. 귀족 저택, 성, 고딕 실내, 특정 재질/건축 양식처럼 tag만으로 부족한 장소 의도는 `semantic_prompt`/`style_prompt`에 짧은 자연어로 넣어 live prompt에 반영합니다.

**Negative prompt:**

```text
1girl, 1boy, crowd, people, silhouette, monster, animal, modern, recent, old, oldest, cartoon, graphic, text, logo, sign, school_emblem, painting, crayon, graphite, abstract, glitch, deformed, ugly, lowres, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, simple_background, (worst_quality, bad_quality:1.2)

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

#### 3. Ren'Py staging / safe-area 계약

- source generation: `1024x576` PNG (16:9)
- review display: `1920x1080` (정확한 1.875배 확대; 종횡비 crop 없음)
- 기본 대사창 영역: 화면 하단 `28%` (`y >= 0.72 * height`)
- 캐릭터 staging: 중앙 배치가 기본이며, 캐릭터 머리/몸 뒤의 창틀·조명·가구가 얼굴 실루엣을 과도하게 가르지 않는 후보를 우선합니다.
- 배경의 핵심 단서, 출입구, 중요한 소품은 하단 28%에만 두지 않습니다. 대사창에 가려져도 장면 이해가 유지되어야 합니다.
- `1024x576`은 생성 원본이지 최종 UI 검수 크기가 아닙니다. Ren'Py target display에서 확대 합성한 preview를 반드시 확인합니다.

실제 배경과 선택적 투명 캐릭터를 합성한 QA preview:

```bash
python scripts/make_renpy_background_preview.py \
  path/to/background.png path/to/renpy_preview.png \
  --character path/to/character_alpha.png \
  --display-width 1920 --display-height 1080 \
  --textbox-fraction 0.28
```

이 preview는 승인본이 아니라 staging 진단물입니다. 실제 프로젝트의 screen/style에 넣은 screenshot smoke와 Ren'Py lint가 최종 gate입니다.

#### 4. 모델 한계와 프롬프트 운영

- Nova Anime XL은 교실·침실·거리처럼 학습 빈도가 높은 장소는 안정적이지만, 특정 도시/랜드마크/건축 양식은 일반적인 배경으로 drift할 수 있습니다.
- `Seoul`, 특정 학교명, 간판 문구처럼 정확한 지리·문자 재현을 생성 모델에 맡기지 않습니다. 지역성은 skyline 후보 선택, 후편집, 별도 prop, Ren'Py overlay로 보강합니다.
- 책상·의자·창틀의 반복 구조는 원근이 깨질 수 있으므로 1장 성공으로 승인하지 않고 최소 3개 seed를 비교합니다.
- `volumetric_lighting`은 로컬 Danbooru taxonomy에서 미확인된 pseudo-tag라 canonical prompt에서 제외합니다. 빛줄기가 필요한 장면만 검증된 `light_rays` 또는 짧은 자연어 style block을 사용합니다.
- 사람 없음과 가짜 문자 억제를 위해 `no_humans` 및 negative의 `text, logo, sign, school_emblem`을 유지합니다.

#### 5. 검증된 Danbooru SQLite 태그 메모

출처: 로컬 Danbooru taxonomy SQLite tag oracle. 아래 태그들은 README에 적기 전에 DB에서 active/non-deprecated로 확인했습니다. `{배경 테마 및 장소}`와 `{시간대 및 분위기 태그}`를 런타임에서 패치할 때 사용합니다.

- 장면 기본 태그: `scenery`, `no_humans`, `indoors`, `outdoors`
- 장소: `classroom`, `school`, `hallway`, `rooftop`, `bedroom`, `living_room`, `street`, `park`, `forest`, `library`
- 장면 오브젝트: `window`, `bookshelf`, `bench`, `utility_pole`
- 구도/시간/날씨: `wide_shot`, `depth_of_field`, `day`, `sunset`, `night`, `rain`, `overcast`, `fog`, `snow`
- 조명/분위기: `sunlight`, `moonlight`

배경 규칙: 사람이 있는 배경을 의도적으로 테스트하는 경우가 아니라면 `no_humans`와 사람/캐릭터 관련 negative를 유지합니다.

