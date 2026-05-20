### 🔍 0. 소품 클로즈업 CG 워크플로우

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, digital_illustration, no_humans, still_life, object_focus, {아이템 이름 및 형태}, {재질 및 질감 디테일}, {놓여있는 장소/배경}, centered composition, entire object visible, single object, BREAK, depth_of_field, studio_lighting, highly_detailed_texture

```

**Negative prompt:**

```text
1girl, 1boy, human, person, character, face, hands, body, multiple objects, duplicate object, cropped, out_of_frame, cut off, extreme close-up, macro shot, modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, lowres, bad_anatomy, sketch, jpeg_artifacts, signature, watermark, username, bad_ai-generated, (worst_quality, bad_quality:1.2), readable_text, fake_letters, fake_writing, printed_text, paragraphs, symbols, glyphs, logo, label, ui, interface, screenshot, dialogue_box, subtitle, caption

```

#### 2. 단서 리스트 적용 예시 (단부루 표준 규격)

*(※ Positive prompt의 `{아이템 이름 및 형태}`, `{재질 및 질감 디테일}` 자리에 복사해서 넣으세요.)*

**1) 낡은 문서나 편지, 책 (종이 질감)**

* **아이템 및 형태:** `old_diary, torn_letter, crumpled_paper, open_book, strange_text, bloodstained_envelope, closed_diary, leather_cover, blank_page, sealed_letter`
* **재질 및 질감:** `yellowed_paper, torn_edges, ink_stains, aged_texture, blank_paper, no_writing`
* **적용 예시:** `... object_focus, old_diary, leather_cover, gold_lock, yellowed_paper, aged_texture, blank_cover, no_writing, lying_on_wooden_desk, BREAK, strong_depth_of_field ...`

**2) 열쇠, 반지, 펜던트 (금속/보석 질감)**

* **아이템 및 형태:** `antique_key, brass_key, flat_key, key_teeth, key_bow, small_key, silver_pocket_watch, glowing, ruby_ring, broken_glass, vial`
* **재질 및 질감:** `metallic_luster, scratched_surface, glowing, reflective, dust_motes`
* **적용 예시:** `... object_focus, antique_key, brass_key, flat_key, key_teeth, key_bow, scratched_surface, metallic_luster, dark_velvet_cloth_background, BREAK, strong_depth_of_field ...`

**3) 현대 기기 (스마트폰, USB 등)**

* **아이템 및 형태:** `cracked_screen, smartphone, blank_screen, black_screen, screen_turned_off, no_text, bloody, usb_drive, modern_tablet`
* **재질 및 질감:** `glass_reflection, fingerprint_smudges, glowing_screen, dark_display`
* **적용 예시:** `... object_focus, cracked_screen, smartphone, blank_screen, black_screen, screen_turned_off, no_text, fingerprint_smudges, glass_reflection, dark_floor, BREAK, strong_depth_of_field ...`

**4) 무기류 (칼, 총기 등)**

* **아이템 및 형태:** `bloody_knife, kitchen_knife, vintage_revolver, broken_sword, sword_hilt`
* **재질 및 질감:** `dried_blood, cold_steel, sharp_edge, heavy_texture`
* **적용 예시:** `... object_focus, bloody_knife, kitchen_knife, sharp_edge, cold_steel, dried_blood, heavy_texture, dimly_lit_table, BREAK, strong_depth_of_field ...`

#### 3. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다. 오브젝트/재질/카메라 태그를 사용하고, 스토리상 텍스트 artifact 테스트가 꼭 필요한 경우가 아니라면 읽을 수 있는 글자는 피합니다.

- 카메라/오브젝트 초점: `still_life`, `object_focus`, `close-up`
- 자주 쓰는 소품 오브젝트: `key`, `ring`, `pendant`, `smartphone`, `letter`, `open_book`, `knife`, `pocket_watch`
- 디테일/상태 태그: `cracked_screen`, `hilt`, `rust`, `blood`, `scratches`
- 표면/조명: `wooden_table`, `desk`, `shadow`, `depth_of_field`, `blurry_background`
- CSV에서 확인된 텍스트/UI negative: `signature`, `watermark`, `logo`, `label`, `caption`, `speech_bubble`

소품 규칙: 편지/책/화면은 최종 텍스트를 ComfyUI 밖에서 합성할 계획이 아니라면 빈 디자인이나 읽을 수 없는 디자인을 우선합니다. `single_object`처럼 "단일 소품만"을 직접 뜻하는 Danbooru 태그는 현재 로컬 CSV에 없으므로, 단일 소품 구도는 `no_humans`, `still_life`, `object_focus`와 `entire object visible`, `single object` 같은 자연어 구도 보정으로 유도합니다. 소품이 잘리면 `close-up`, `macro shot`, `key_teeth`, `key_bow`처럼 부분 디테일이나 과한 근접을 유도하는 태그를 줄입니다.

