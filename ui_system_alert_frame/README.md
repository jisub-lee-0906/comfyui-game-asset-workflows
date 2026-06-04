## 문서 규격(v1)

- workflow_id: `ui_system_alert_frame`
- modality: `image`
- input_requirement: 없음
- output: 16:9 textless VN system alert backdrop/frame PNG
- prompt_policy: `pure_t2i_creator_wrapper+danbooru_csv_backdrop_slots+runtime_patch+overlay_readability_qa`
- editable_fields: 3.inputs.text, 4.inputs.text, 5.inputs.width, 5.inputs.height, 6.inputs.seed, 6.inputs.steps, 6.inputs.cfg, 8.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.
- 생성 후보는 owner가 exact candidate metadata/run id를 승인하기 전까지 `game/images/ui/`에 promotion하지 않습니다.
- Korean text overlay preview는 QA 진단용입니다. 최종 목적은 baked text 없는 UI frame asset입니다.

### 🔴 0. 붉은 시한부 시스템 알림창 backdrop/frame 워크플로우

이 workflow는 VN/Ren'Py에서 재사용할 **textless system alert backdrop/frame** 후보를 만듭니다. `scene_prop_cg`와 분리된 전용 workflow입니다. UI 프레임은 소품 CG가 아니며, prop workflow를 쓰면 중앙 소품, 가짜 텍스트, 기호, 이름표, 로고가 생기기 쉽습니다.

목표 산출물:
- 16:9 PNG 후보, 기본 source generation `1024x576`.
- red/crimson + dark + corner ornament 계열의 로판/VN 시스템 알림 배경/패널.
- Ren'Py에서 한국어를 overlay할 수 있는 어둡고 읽기 좋은 중앙 영역.
- literal picture frame에 고정하지 않고, corner/border/backdrop identity와 overlay readability를 우선할 것.
- baked text, logo, icon, symbol, emblem, nameplate, character, prop, scenery 없음.
- review-only metadata를 유지하고 approval 전 promotion 금지.

#### 1. 프롬프팅 방법

이미지 workflow prompt는 **pure T2I textless system alert backdrop/frame generation**을 기본 route로 사용합니다. 제작자 권장 quality/style wrapper와 Danbooru CSV 검증 backdrop/color/corner slot을 분리합니다. 구조/장식/색/억제 slot은 루트 `danbooru_tag.csv`의 `tag` 또는 `aliases`에 존재하는 tag를 우선 사용하고, `masterpiece`, `best quality`, `amazing quality`, `very aesthetic`, `absurdres`, `highres`, `newest` 같은 제작자 권장 wrapper는 CSV 밖이어도 보존합니다. 단, 임의 자연어 chunk/pseudo-tag/문장형 UI 설명은 넣지 않습니다. 2026-06-04 실사용 probe 기준으로 `window_(computing)`, `dialogue_box`, positive `scenery`, `user_interface`, `empty_picture_frame`, `picture_frame`, `gradient_background`, `gradient_border`는 기본 positive에서 제외하고 필요 시 별도 실험으로만 사용합니다.

**Positive prompt 기본형 — corner alert backdrop base:**

```text
masterpiece, best quality, amazing quality, very aesthetic, absurdres, highres, newest, game_cg, visual_novel, border, outside_border, red_border, black_border, gold_border, corner, red_theme, black_theme, dark_background, black_background, no_humans
```

이 기본형은 owner가 `83f9997b-0490-468d-b68f-45f1187ee3ef` / `J3_no_gradient_S3_seed260604912` 수준이면 충분하다고 확인한 route입니다. `empty_picture_frame`, `picture_frame`, `gradient_border`, `gradient_background` positive를 제거하고, literal/nested picture-frame purity보다 **dark/red/gold corner ornament backdrop + Ren'Py overlay readability**를 우선합니다.

**색상/무드 변형 slot:**

```text
red_border, black_border, gold_border, red_theme, black_theme, dark_background, black_background
blue_border, black_border, gold_border, blue_theme, black_theme, dark_background, black_background
purple_border, black_border, gold_border, purple_theme, black_theme, dark_background, black_background
green_border, black_border, gold_border, green_theme, black_theme, dark_background, black_background
orange_border, black_border, gold_border, orange_theme, black_theme, dark_background, black_background
```

운영 메모:
- `corner`, `border`, `outside_border`가 silhouette/장식 정체성에 가장 중요합니다.
- `gradient_background`와 `gradient_border`는 색 변화/쏠림과 literal frame 느낌을 키울 수 있어 기본형에서 제외합니다.
- `user_interface`는 baked HUD/text 위험이 있어 기본형에서 제외하고, UI 감각은 Ren'Py overlay와 border/corner로 처리합니다.
- `empty_picture_frame`/`picture_frame` route는 중앙 plate를 잘 만들 수 있지만 nested/literal picture-frame artifact가 반복되어 fallback/historical route로만 기록합니다.

**Negative prompt 기본형:**

```text
worst quality, low quality, bad quality, lowres, jpeg artifacts, blurry, bad anatomy, bad hands, missing fingers, extra fingers, extra digits, fewer digits, cropped, very displeasing, artist name, signature, watermark, username, text, fake_text, text_focus, english_text, korean_text, logo, label, caption, speech_bubble, dialogue_options, 1girl, 1boy, people, portrait, face, eye, glowing_eye, animal, cat, scenery, indoors, outdoors, city, building, window_(computing), dialogue_box, icon_(computing), emblem, crest, magic_circle, runes, glyph, circle, red_circle, heart, halo, lens_flare, spotlight, gem, jewel, crystal, cross, medallion, box, paper, book, empty_picture_frame, picture_frame, photo_frame, painting, painting_(object)
```

프롬프트 원칙:
- subject/구조/억제 slot의 Danbooru tag는 README 작성 시점에 루트 `danbooru_tag.csv` 존재를 확인한 것만 적습니다.
- 제작자 권장 wrapper는 CSV 검증 대상에서 분리하여 보존할 수 있습니다. 이 workflow의 현재 positive wrapper는 `masterpiece, best quality, amazing quality, very aesthetic, absurdres, highres, newest`입니다. `scenery`는 wrapper가 아니라 drift-prone subject tag로 취급하여 negative에 둡니다.
- `alert`, `warning`, `prohibition`, `system message frame`, `frame overlay asset`, `large blank central panel` 같은 임의 자연어/pseudo-tag는 사용하지 않습니다.
- 중앙 영역의 “읽기 좋음”은 Danbooru tag만으로 완전히 보장하기 어렵습니다. pure T2I source 생성에서는 `border`, `outside_border`, `corner`, color border/theme 계열로 시스템 backdrop 성격을 유도하고, `window_(computing)`, `dialogue_box`, positive `scenery`, `user_interface`는 기본 positive에서 제외합니다. 중앙 gem/cross/vertical flare/medallion/character/HUD는 QA reject 또는 다음 prompt-change 대상으로 처리합니다.
- 중앙 내용은 ComfyUI가 아니라 Ren'Py/후편집 overlay로 처리합니다.
- raw source가 좋지만 중앙이 깨끗하지 않으면 `V08`~`V10` 같은 deterministic cleanplate review candidate로 정리합니다.

#### 1-1. 검증된 Danbooru CSV 태그 메모와 wrapper 예외

출처: 루트 `danbooru_tag.csv`. 아래 subject/억제 태그들은 README 작성 시점에 CSV의 `tag` 또는 `aliases` 존재를 확인했습니다. 제작자 권장 quality/style wrapper는 별도 예외로 취급합니다.

- UI/게임 맥락: `game_cg`, `visual_novel`, `user_interface`, `window_(computing)`, `dialogue_box`
- 프레임/장식: `border`, `outside_border`, `corner`, `gold_border`, `red_border`, `black_border`, `blue_border`, `purple_border`, `green_border`, `orange_border`, `empty_picture_frame`, `picture_frame`, `inset_border`, `gradient_border`, `ornate_border`, `ornate`, `filigree`, `gold_trim`
- 색/배경 보조: `red_theme`, `blue_theme`, `purple_theme`, `green_theme`, `orange_theme`, `black_theme`, `dark_background`, `simple_background`, `black_background`, `red_background`, `blue_background`, `purple_background`, `green_background`, `orange_background`, `flat_color`, `gradient_background`
- 사람/장면 억제: `no_humans`, `1girl`, `1boy`, `people`, `portrait`, `scenery`, `indoors`, `outdoors`
- 텍스트/UI artifact 억제: `fake_text`, `text_focus`, `english_text`, `korean_text`, `logo`, `label`, `caption`, `speech_bubble`, `dialogue_options`
- 중앙 기호/소품 drift 억제: `icon_(computing)`, `emblem`, `crest`, `magic_circle`, `runes`, `glyph`, `circle`, `red_circle`, `heart`, `halo`, `lens_flare`, `spotlight`, `gem`, `jewel`, `crystal`, `cross`, `medallion`, `box`, `paper`, `book`
- 품질/워터마크 억제: `watermark`, `signature`, `lowres`, `jpeg_artifacts`, `bad_anatomy`

#### 1-2. 현재 안정화된 pure T2I 방향

2026-06-04 owner-reviewed direction is **flexible non-frame corner alert backdrop** rather than literal frame purity. Earlier `empty_picture_frame`/`picture_frame` routes kept a central plate but repeatedly produced nested/literal picture-frame artifacts. The accepted base run is `ui_system_alert_J3_no_gradient_probe_20260604_195922`, prompt id `83f9997b-0490-468d-b68f-45f1187ee3ef`, candidate `J3_no_gradient_S3_seed260604912.png`.

Accepted design principle:
- Treat the asset as a dark/red limited-life system alert **backdrop/frame**, not a prop CG and not a literal painting frame.
- Preserve `border`, `outside_border`, `corner`, color border/theme tags, `dark_background`, `black_background`, and `no_humans`.
- Keep `empty_picture_frame`, `picture_frame`, `gradient_background`, `gradient_border`, and `user_interface` out of the default positive prompt.
- Judge success by Korean overlay readability, fatal fantasy system vibe, no baked text/logo/characters/central symbols, and enough corner/border identity.

Historical note: F1 empty-picture-frame canonical smoke reached 2/3 pass but remained too attached to nested picture-frame artifacts. The new corner-backdrop base is now preferred for this workflow; the old route remains useful only as a fallback probe when a literal central plate is specifically requested.

#### 1-3. 색상/무드 변형 가이드

색상 변형은 canonical base에서 아래 공통 구조를 유지하고 color slot만 교체합니다.

공통 구조:

```text
masterpiece, best quality, amazing quality, very aesthetic, absurdres, highres, newest, game_cg, visual_novel, border, outside_border, corner, no_humans
```

권장 color slots:

| Mood | Color slot | QA note |
| --- | --- | --- |
| fatal red / limited life | `red_border, black_border, gold_border, red_theme, black_theme, dark_background, black_background` | canonical base. 붉은 fatal system vibe가 강하지만 same-seed에서는 세로 red glow가 남을 수 있음. |
| cold blue / status scan | `blue_border, black_border, gold_border, blue_theme, black_theme, dark_background, black_background` | `ui_system_alert_color_mood_variants_20260604_200550`에서 실사용 가능. 얇은 중앙 blue line은 있으나 가독성 양호. |
| cursed royal purple | `purple_border, black_border, gold_border, purple_theme, black_theme, dark_background, black_background` | 가장 안정적인 alternate mood. 로판/저주/귀족 시스템 알림에 적합. |
| contract green magic | `green_border, black_border, gold_border, green_theme, black_theme, dark_background, black_background` | 계약/마법/상태 UI에 사용 가능. 중앙 세로선이 생길 수 있어 overlay 위치 확인 필요. |
| urgent orange warning | `orange_border, black_border, gold_border, orange_theme, black_theme, dark_background, black_background` | same-seed probe에서 중앙 orange bar가 강해 기본 추천은 아님. seed reroll 또는 `orange_border` 약화 필요. |
| white/gold divine notice | `white_border, black_border, gold_border, white_theme, black_theme, dark_background, black_background` | same-seed probe에서 흰 vertical bar가 중앙을 막아 기본 추천은 아님. divine UI가 필요하면 별도 prompt/seed 연구 필요. |

색상 변형 QA 원칙:
- 같은 seed/color slot swap만으로도 중앙 세로 bar/glow가 생길 수 있습니다. 색상별로 최소 2~3 seed smoke를 권장합니다.
- `gradient_background`/`gradient_border`는 색상 richness를 만들 수 있지만, 이번 base에서는 색상 쏠림과 literal frame 느낌을 키워 기본형에서 제외합니다.
- strict uniformity가 필요하면 `dark_background`를 줄이고 `simple_background`, `flat_color`, `black_background` 중심으로 재실험합니다. 단, 너무 평면화하면 VN system identity가 약해질 수 있습니다.
- Korean overlay preview를 항상 같이 만듭니다. 이 workflow의 성공 기준은 “멋진 빈 이미지”가 아니라 실제 Ren'Py 화면에서 읽히는 시스템 backdrop입니다.

#### 1-4. Minimal ablation prompt lesson

2026-06-04 `ui_system_alert_minimal_single_token_probe_20260604_201237` and follow-up ladders showed that broad/contextual tags can cause most artifacts. When the output feels overworked, reset to a very small base and add one tag at a time.

Minimal fixed base used for ablation:

```text
masterpiece, best quality, highres, black_background, no_humans
```

Observed token effects from same-seed single-token probe:

| Token | Observed effect | Default stance |
| --- | --- | --- |
| `border` | clean simple frame/border; little artifact | keep |
| `red_border` | clean red edge; good warning identity | keep |
| `gold_border` | clean gold edge; useful accent | keep |
| `dark_background` | subtle dark field; readable | keep/cautious |
| `visual_novel` | fake vertical text appeared | avoid default |
| `game_cg` | central blue star/line appeared | avoid default |
| `corner` | central pole/round object appeared in same-seed probe | avoid until needed |
| `red_theme` | central red burst/symbol appeared | avoid default |
| `black_theme` | mecha/character drift appeared | avoid default |
| `red_background` | mecha/character drift appeared | avoid default |
| `outside_border` | fake vertical text appeared alone; cleaner only in cumulative case | cautious |

Cleaner cumulative candidates came from:

```text
masterpiece, best quality, highres, black_background, no_humans, border, red_border, gold_border
masterpiece, best quality, highres, black_background, no_humans, border, red_border, gold_border, dark_background
```

Theme-free color swaps were cleaner than earlier `*_theme` variants:

```text
masterpiece, best quality, highres, black_background, no_humans, border, red_border, gold_border
masterpiece, best quality, highres, black_background, no_humans, border, purple_border, gold_border
masterpiece, best quality, highres, black_background, no_humans, border, orange_border, gold_border
```

Operational rule: start from the minimal base, add only one structure/color token, run overlay QA, then decide whether the next token is necessary. Do not add `visual_novel`, `game_cg`, `*_theme`, `corner`, or `outside_border` by habit.

#### 2. Canonical API workflow

- canonical 파일: `ui_system_alert_frame_workflow_api.json`
- ComfyUI API JSON이며 UI graph export가 아닙니다.
- source workflow는 그대로 보존합니다.
- 실행 시 project run directory로 복사한 뒤 runtime copy만 patch합니다.
- generated candidate는 workflow pack 밖의 프로젝트 automation 영역에 저장합니다.

주요 노드:

| Node | Class | Purpose |
| --- | --- | --- |
| `1` | `CheckpointLoaderSimple` | SDXL/anime checkpoint. 기본 `novaAnimeXL_ilV190.safetensors` |
| `2` | `CLIPSetLastLayer` | CLIP skip `-2` |
| `3` | `CLIPTextEncode` | Positive prompt |
| `4` | `CLIPTextEncode` | Negative prompt |
| `5` | `EmptyLatentImage` | 기본 `1024x576`, batch `1` |
| `6` | `KSampler` | 기본 smoke settings: 30 steps, CFG 3.6, euler ancestral, normal scheduler |
| `7` | `VAEDecode` | Decode latent |
| `8` | `SaveImage` | Output prefix; run마다 patch |

#### 3. 운영 가이드

1. `ui_system_alert_frame_workflow_api.json`을 target project의 runtime/run directory로 복사합니다.
2. runtime copy에서만 seed/prompt/output prefix를 patch합니다.
3. smoke batch는 보통 3~5장부터 시작합니다.
4. baked text/logos/symbols/icons/nameplates/central objects가 있으면 reject합니다.
5. source의 corner/border identity는 좋지만 중앙이 바쁘면 `scripts/make_cleanplate_variants.py`로 cleanplate review variant를 만들 수 있습니다.
6. 최종 후보는 backdrop-first로 평가합니다: text overlay readability, red/dark/gold system-alert vibe, corner/border identity, no baked semantics.
7. Korean overlay preview와 contrast matrix는 core QA로 사용하되, overlay text를 이미지에 굽지 않습니다.
8. exact metadata/run id에 owner approval이 붙기 전까지 promotion하지 않습니다.

#### 4. Cleanplate/helper 사용

`make_cleanplate_variants.py`는 pure T2I 후보가 중앙 장식/세로 glow 때문에惜しい 경우에만 사용하는 optional fallback입니다. source backdrop/frame 하나를 review-only variant와 QA preview로 변환하며, 이 스크립트는 `game/images/ui/`에 쓰지 않습니다.

```bash
python E:/workspace/comfyui-game-asset-workflows/ui_system_alert_frame/scripts/make_cleanplate_variants.py \
  --source E:/workspace/renpy-project/<game_slug>/docs/automation/generated_candidates/ui/<run>/<candidate>.png \
  --outdir E:/workspace/renpy-project/<game_slug>/docs/automation/generated_candidates/ui/<new_cleanplate_run> \
  --font E:/workspace/renpy-project/<game_slug>/game/fonts/source_han_sans_lite.ttf \
  --background E:/workspace/renpy-project/<game_slug>/game/images/backgrounds/bg_example.png
```

주요 출력:
- `candidates/V01_reference_source.png`
- `candidates/V02_large_dark_readable_plate.png`
- `candidates/V03_wide_low_contrast_plate.png`
- `candidates/V04_thin_gold_red_inner_trim.png`
- `candidates/V05_bottom_oval_suppressed.png`
- `candidates/V06_strict_wide_textsafe_plate.png` — readability stress-test/fallback
- `candidates/V07_strict_minimal_modal_plate.png` — readability stress-test/fallback
- `candidates/V08_production_solid_cleanplate_balanced.png` — 현재 권장 production review 후보
- `candidates/V09_production_solid_cleanplate_wide.png` — 긴 텍스트 안전성 우선 후보
- `candidates/V10_production_deep_red_cleanplate.png` — 더 강한 red alert tone 후보
- per-candidate metadata: `review_candidate_not_promoted`, `promotion_allowed: false`
- `validation/variant_contact_sheet_with_korean_overlay.png`
- `validation/contrast_matrix.png`
- Korean overlay diagnostic previews
- `qa_metadata.json`

2026-06-04 production note:
- V08은 central plate/ornament/가독성 균형이 가장 좋아 현재 기본 추천입니다.
- V09는 plate가 넓어 긴 텍스트에 유리하지만 ornament 보존이 V08보다 약합니다.
- V10은 경고색이 강하지만 중앙이 더 무겁고 어둡습니다.
- V02~V07은 비교/diagnostic/stress-test 용도로 남겨두고, production review에는 V08~V10을 우선합니다.

#### 5. QA 체크리스트

후보 batch마다 다음을 남깁니다.

- candidate metadata: seed, workflow hash, endpoint, prompt, source output, candidate copy, promotion status.
- runtime patched workflow copy.
- contact sheet.
- Korean Ren'Py-style sample text overlay preview. 텍스트는 이미지에 굽지 않지만, overlay readability는 core QA입니다.
- contrast matrix 또는 busy/dark/bright background 확인.
- visual QA notes:
  - backdrop/frame identity와 red/dark/gold system-alert silhouette.
  - corner/border ornament quality.
  - central text overlay readability와 busy-area 여부.
  - baked text/logos/symbols/nameplates/characters/props 없음.
  - 실제 Ren'Py screen placement에서 대사창/character와 충돌하지 않는지.
  - `game/images/ui/` promotion 여부와 approval gate 상태.

#### 6. Promotion gate

Generated images are review candidates only.

금지:
- owner approval 없이 `game/images/ui/`로 복사.
- approval 없이 manifest를 production-ready로 변경.
- Korean overlay QA 샘플을 baked text로 오해하고 이미지 자체에 굽기.

승인 후 절차:
1. owner가 exact candidate id/run id를 명시합니다.
2. 후보 hash/metadata를 재확인합니다.
3. `game/images/ui/`에 promotion합니다.
4. target Ren'Py project에서 `templates/renpy_screen_snippet.rpy` 또는 project-specific screen을 적용합니다.
5. asset-ref check, Ren'Py lint, 실제 screenshot smoke를 통과시킵니다.
6. manifest와 Obsidian에 promotion 완료 상태를 기록합니다.

#### 7. Files

| Path | Purpose |
| --- | --- |
| `ui_system_alert_frame_workflow_api.json` | Canonical ComfyUI API workflow |
| `scripts/make_cleanplate_variants.py` | Optional fallback cleanplate variants + Korean overlay QA diagnostics; pure T2I route is preferred |
| `templates/renpy_screen_snippet.rpy` | Review-only Ren'Py screen snippet |
| `references/qa_policy.md` | Hard rejects, review outputs, lessons |
