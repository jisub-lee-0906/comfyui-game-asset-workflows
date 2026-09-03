## 문서 규격(v2)

- workflow_id: `ui_system_alert_frame`
- modality: `image`
- input_requirement: 없음
- output: 1024x576 textless VN alert frame source PNG
- prompt_policy: `pure_t2i+danbooru_slots+rendered_korean_overlay_qa`
- editable_fields: `3.inputs.text`, `4.inputs.text`, `5.inputs.width`, `5.inputs.height`, `6.inputs.seed`, `6.inputs.steps`, `6.inputs.cfg`, `8.inputs.filename_prefix`

운영 원칙:

- canonical JSON은 직접 덮어쓰지 않고 runtime copy만 patch합니다.
- candidate != approved != production-ready입니다.
- 생성 모델은 프레임만 만들고 실제 문자와 상태 값은 Ren'Py가 그립니다.
- static CI는 prompt, seed, 경로, 배치 수, 화면 수치만 검사합니다. 가짜 문자·중앙 기호·가독성·장면 가림은 rendered visual QA가 필수입니다.

### 1. 기본 경로

- checkpoint: `novaAnimeXL_ilV190.safetensors`
- source size: 1024x576
- sampler: `euler_ancestral`, normal
- steps/CFG: 30 / 3.6
- default seed: `260604912`
- Ren'Py display: 1920x1080
- presentation: 720x240 top-left non-modal panel
- margin: 48x48
- preview opacity: 245/255

canonical positive:

```text
masterpiece, best quality, amazing quality, very aesthetic, absurdres, highres, newest, game_cg, visual_novel, border, outside_border, red_border, black_border, gold_border, corner, red_theme, black_theme, dark_background, black_background, no_humans
```

canonical negative:

```text
worst quality, low quality, bad quality, lowres, jpeg artifacts, blurry, bad anatomy, bad hands, missing fingers, extra fingers, extra digits, fewer digits, cropped, very displeasing, artist name, signature, watermark, text, fake_text, text_focus, english_text, korean_text, logo, label, caption, speech_bubble, dialogue_options, 1girl, 1boy, people, portrait, glowing_eye, animal, cat, scenery, indoors, outdoors, city, building, window_(computing), dialogue_box, icon_(computing), emblem, crest, magic_circle, runes, glyph, circle, red_circle, heart, halo, lens_flare, spotlight, gem, jewel, crystal, cross, medallion, box, paper, book, empty_picture_frame, picture_frame, photo_frame, painting, painting_(object)
```

wrapper의 `masterpiece`, `best quality` 같은 표현은 제작자 권장 품질 구문입니다. 구조·색상·억제 slot은 로컬 Danbooru taxonomy DB에서 검증된 태그를 우선합니다.

### 2. 동일 seed prompt A/B 결과

세 개의 서로 다른 seed `9065001`, `9065002`, `9065003`을 A와 B에 동일하게 재사용하여 총 3쌍/6회 렌더했습니다.

A — canonical corner/backdrop prompt:

- 3/3에서 baked text, 인물, 소품 없이 사용할 수 있는 중앙 영역이 나왔습니다.
- seed에 따라 얇은 테두리, 붉은 gradient, 코너 장식 강도가 달랐습니다.

B — minimal prompt:

```text
masterpiece, best quality, highres, black_background, no_humans, border, red_border, gold_border, dark_background
```

- 2/3은 깨끗했지만 seed `9065002`에서 중앙 금색 기호가 생겨 hard reject였습니다.
- prompt가 짧다고 중앙 semantics가 항상 줄어드는 것은 아니었습니다.

따라서 현재 canonical prompt를 유지합니다. 프롬프트를 바꿀 때는 최소 3개의 서로 다른 seed를 양쪽 variant에 재사용하여 3쌍/6회 렌더합니다.

### 3. canonical source 검증

기본 seed `260604912`를 canonical에서 edits 없이 재생성했을 때 다음을 확인했습니다.

- baked text/logo/icon/character/prop 없음
- 중앙 medallion 또는 세로 bar 없음
- 검정 중앙 영역과 붉은 코너/테두리 유지
- 짧은·긴 한국어 모두 직접 overlay 가능

중앙이 이미 깨끗한 source는 그대로 사용합니다. cleanplate는 모든 결과에 자동 적용하는 production 단계가 아니라, 중앙에 기호·ghosting이 있는 후보를 살리는 선택적 fallback입니다.

### 4. Ren'Py top-left non-modal 계약

기본 배치:

```text
display: 1920x1080
panel: 720x240
position: x=48, y=48
mode: top_left_nonmodal
text width: 620
font size: 34
```

이 위치는 중앙 캐릭터의 얼굴·손·스토리 소품을 가리지 않고 배경의 좌상단 공간만 사용하도록 정한 기본값입니다. 다른 장면에서는 protected box를 직접 지정하고 패널과 교차하면 실패시킵니다.

QA 문구:

```text
미확인 에너지 감지
제3교실에서 미확인 데이터 코어가 감지되었습니다
```

실제 preview:

```bash
python ui_system_alert_frame/scripts/make_renpy_alert_preview.py \
  /path/to/textless_frame.png \
  /path/to/event_cg.png \
  /path/to/preview.png \
  --message "제3교실에서 미확인 데이터 코어가 감지되었습니다" \
  --font /path/to/korean-font.ttf \
  --protected-box 800,40,1250,760
```

스크립트는 다음을 검증합니다.

- display와 panel 크기가 양수인지, source/display가 20,000,000 pixel 제한 안인지
- panel이 화면 안에 들어오는지
- message가 비어 있지 않고 최대 줄 수를 넘지 않는지
- panel이 protected box와 교차하지 않는지
- 결과가 1920x1080 RGB preview인지

preview의 한국어는 QA용으로만 합성되며 textless source 파일을 수정하지 않습니다.
기존 출력 경로는 기본적으로 거부합니다. 의도적으로 같은 preview를 다시 만들 때만
`--overwrite`를 추가합니다. 덮어쓰기는 같은 디렉터리의 임시 파일을 거쳐 원자적으로
교체되며, frame/background 입력과 같은 경로·심볼릭 링크·하드링크는 거부합니다.
한글 등 비 ASCII 문구에는 해당 글리프를 포함한 `--font`를 반드시 지정해야 합니다.

### 5. Ren'Py screen

`templates/renpy_screen_snippet.rpy`는 같은 기본 계약을 사용합니다.

- `modal False`
- `xpos 48`, `ypos 48`
- `xysize (720, 240)`
- frame `alpha 0.96` (`245/255` preview opacity와 대응)
- `xmaximum 620`
- 실제 문구는 `message` 인자로 전달

이 알림은 전체 장면을 대체하는 full-screen backdrop이 아니라 기본적으로 좌상단 non-modal notification입니다. script beat가 전체 화면 경고를 요구한다면 별도 screen으로 구현하고 동일 자산을 무조건 확대하지 않습니다.

### 6. Cleanplate fallback

중앙이 더러운 source에만 실행합니다.

```bash
python ui_system_alert_frame/scripts/make_cleanplate_variants.py \
  --source /path/to/source.png \
  --outdir /path/to/review_run \
  --font /path/to/korean-font.ttf
```

- V08: 중앙 plate와 장식 균형
- V09: 가장 넓어 긴 문구 fallback에 적합
- V10: 더 강한 red tone

cleanplate 결과도 review-only입니다. source에 baked text, 캐릭터, 큰 소품이 있으면 cleanplate로 억지 복구하지 말고 seed를 버립니다.

### 7. Hard reject와 QA

즉시 탈락:

- baked text, fake text, logo, label, nameplate, watermark
- character, face, animal, prop, book, paper, scenery focus
- 중앙 gem, crystal, medallion, cross, halo, rune, icon, emblem
- 한국어를 가리는 중앙 세로 bar/glow
- 패널과 protected character/action box 교차

Rendered QA:

- 짧은 문구가 한 줄로 읽힘
- 긴 문구가 2~3줄 안에서 자연스럽게 줄바꿈됨
- 테두리와 글자가 충돌하지 않음
- 실제 이벤트 CG의 얼굴·손·스토리 소품을 가리지 않음
- 어두운 장면과 밝은 장면 모두에서 대비가 충분함
- textless source와 overlay preview를 구분하여 보관함

### 8. Promotion gate

owner가 정확한 candidate/run을 승인하기 전에는 `game/images/ui/`로 복사하지 않습니다. 승인 후에는 다음을 다시 확인합니다.

1. source hash와 metadata
2. Ren'Py screen asset reference
3. Ren'Py lint
4. 실제 screenshot smoke
5. 짧은·긴 한국어와 대상 해상도

### 9. Files

- `ui_system_alert_frame_workflow_api.json`: canonical ComfyUI API workflow
- `scripts/make_renpy_alert_preview.py`: 실제 장면 위 short/long 한국어 overlay QA
- `scripts/make_cleanplate_variants.py`: 선택적 중앙 cleanplate fallback
- `templates/renpy_screen_snippet.rpy`: top-left non-modal Ren'Py screen 예시
- `references/qa_policy.md`: hard reject와 approval gate
