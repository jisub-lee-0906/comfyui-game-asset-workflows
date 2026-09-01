## 문서 규격(v1)

- workflow_id: `scene_event_cg`
- modality: `image`
- input_requirement: 없음 (no-ref)
- output: 16:9 event CG PNG
- prompt_policy: `danbooru_sqlite+readme_wrapper`
- editable_fields: 100.inputs.lora_name, 100.inputs.strength_model, 100.inputs.strength_clip, 9.inputs.text, 10.inputs.text, 11.inputs.width, 11.inputs.height, 12.inputs.seed, 12.inputs.steps, 12.inputs.cfg, 12.inputs.denoise, 14.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🖼️ 0. 이벤트 CG 제작 워크플로우

이 워크플로우는 이미지 reference 없이 Nova Anime XL IL v19 텍스트 프롬프트만으로 16:9 이벤트 CG를 생성합니다. canonical JSON은 no-ref + pose LoRA on을 기본으로 합니다.

핵심 운영 원칙:

- 이미지 reference / PuLID 없음.
- checkpoint: `novaAnimeXL_ilV190.safetensors`.
- pose LoRA: `hinaMaybeBetterPoseXL_v5-NoobAI.safetensors`, strength `0.65 / 0.65`.
- 출력 비율은 event_cg 규칙에 따라 항상 16:9(기본 1024x576)만 사용합니다.
- 캐릭터 일관성은 이미지 참조가 아니라 고정 identity/outfit block으로 유지합니다.
- 프롬프트는 `char_base no-composition 테스트 방식`을 event_cg에 이식한 계약을 사용합니다.
- README는 실행 가이드입니다. 과거 출력 경로, prompt_id, contact sheet 같은 기록은 README가 아니라 skill reference / `.analysis/` / `WORKFLOW_INDEX.json`에 둡니다.

#### 1. 기본 canonical prompt

아래 prompt는 바로 실행 가능한 기본 샘플입니다. char_base no-composition 테스트 방식 그대로, 구도/카메라 강제 태그를 기본 positive에서 제거하고 identity/outfit block 중심으로 운용합니다. event_cg 특성상 장면 태그는 최소한으로만 추가하고, 16:9 출력은 고정합니다.

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, 1girl, solo, {캐릭터 특징(연령대, 헤어스타일, 눈매, 머리색, 눈색)}, {의상 디테일(의상 이름, 색상_의상종류)}, auditorium, indoors, spotlight, depth_of_field
```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, (worst_quality, bad_quality:1.2), sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, classroom, chalkboard, blackboard, whiteboard
```

#### 2. Prompt 조립 순서

기존 캐릭터 기반 event CG를 만들 때는 README 샘플을 그대로 복붙하지 말고, 먼저 프로젝트의 캐릭터 metadata sidecar를 읽습니다.

portable game project 예시:

```text
$GAME_ROOT/docs/assets/characters/<character_id>.asset.json
```

조립 순서:

1. creator/model wrapper를 유지합니다.
2. 캐릭터 특징 block을 `{연령대, 헤어스타일, 눈매, 머리색, 눈색}`으로 고정합니다.
3. 의상 block을 `{의상 이름, 색상_의상종류}` SQLite 태그 묶음으로 고정합니다.
4. 구도/카메라 강제 태그(`upper_body`, `cowboy_shot`, `from_above`, `from_below`, `dutch_angle` 등)는 기본 positive에 넣지 않습니다.
5. scene/background/time tag는 최소한으로만 추가합니다.
6. 모든 variable tag는 로컬 Danbooru taxonomy SQLite에서 active/non-deprecated tag 또는 alias로 존재하는지 검증합니다.
7. README에 문서화된 wrapper/운영 태그와 DB 검증을 통과한 태그만 사용합니다.
8. DB에 없는 자연어 chunk, pseudo-tag, 오래된 helper script 출력은 사용하지 않습니다.

Metadata 원본 특징 guard:

- PNG metadata의 오래된 prompt나 이전 실험 prompt가 현재 캐릭터 metadata보다 우선하지 않습니다.
- 다른 캐릭터를 만들 때는 이 README의 Lia 예시 anchor를 그대로 쓰지 말고, 해당 캐릭터 metadata anchor로 교체합니다.
- 원본/승인 캐릭터의 `identity_anchor`와 선택한 outfit block을 임의로 바꾸지 않습니다. 머리 길이/스타일/색, 눈색, 핵심 의상색/소품이 바뀌면 event CG가 아니라 다른 캐릭터처럼 drift합니다.
- scene/background/time/small staging tag는 identity/outfit block 뒤에 소량 추가하고, identity/outfit과 충돌하는 태그를 넣지 않습니다.
- 의상 드리프트를 줄이겠다고 DB에 없는 자연어/pseudo-tag를 넣지 않습니다.

#### 3. 기본 안전 tag 세트

중립/대화/설명용 기본값:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer, standing, arms_at_sides
```

설명/멈칫/제지 beat:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer, standing, open_hands, reaching, serious, open_mouth, motion_lines
```

발표/지목/명령 beat:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer, standing, pointing_at_viewer, outstretched_arm, serious, open_mouth, motion_lines
```

충격/reveal beat의 close cinematic 기본값:

```text
upper_body, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
```

운영 규칙:

- 한 번에 주 동작 태그를 여러 개 섞지 않습니다. `reaching`, `pointing_*`, `outstretched_arms`, `dutch_angle/motion` 중 하나를 중심으로 둡니다.
- 손동작 프리셋은 seed A/B 후보를 여러 장 뽑고, 손가락/소매/팔 길이 QA를 통과한 것만 asset candidate로 둡니다.
- `pointing_forward`는 양팔 대칭 지시가 나올 수 있으므로 지목/명령 연출은 `pointing_at_viewer`를 우선합니다.
- 기본/중립 event CG는 얼굴 품질과 캐릭터 동일성을 위해 `upper_body` 중심으로 둡니다.

#### 4. Cinematic 후보 tag 세트

아래 블록들은 “한 batch에 다 섞는 목록”이 아닙니다. 테스트에서 잘 먹힌 안전 후보 태그 세트이며, script beat에 맞는 블록 하나를 고르고 seed reroll로 후보를 뽑습니다.

General cinematic shock/reveal:

```text
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
```

Stable cinematic fallback:

```text
cowboy_shot, from_below, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
```

Stop/reveal/presentation event:

```text
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, outstretched_arms, open_hands, surprised, open_mouth, motion_lines
```

Directed command/accusation event:

```text
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, pointing_at_viewer, outstretched_arm, serious, open_mouth, motion_lines
```

Reaching / POV involvement / rescue / interruption:

```text
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning_forward, open_hands, reaching, serious, open_mouth, motion_lines
```

Vulnerability / panic / overwhelmed shock:

```text
cowboy_shot, from_above, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
```

주의:

- `cowboy_shot`, `from_below`, `from_above`는 기본 대화/중립 프리셋이 아니라 beat-matched cinematic 후보입니다.
- `wide_shot`, `full_body`는 얼굴/identity/anatomy 리스크 때문에 기본 후보에서 제외합니다.
- cinematic 후보도 production-ready가 아니라 generation recipe입니다. contact sheet + asset QA + Ren'Py textbox/safe-area QA 후에만 사용자 리뷰 후보로 올립니다.

#### 5. 장소/장면 tag 운영

제3마법시연장/발표장 계열:

```text
auditorium, stage, curtains, spotlight, indoors, podium, presentation
```

사용하지 않을 기본 negative:

```text
classroom, chalkboard, blackboard, whiteboard
```

규칙:

- `classroom`을 magic demo hall proxy로 쓰지 않습니다.
- 정확한 장소 tag가 DB에 없으면 자연어로 억지 설명하지 말고, 배경 workflow / 별도 prop / Ren'Py staging / overlay로 해결합니다.
- text, sign, board가 나올 가능성이 있는 장소는 fake text QA를 필수로 합니다.

#### 6. 검증된 Danbooru SQLite tag 메모

출처: 로컬 Danbooru taxonomy SQLite tag oracle. 아래 tag는 README 작성 시점에 DB에서 active/non-deprecated 존재를 확인한 운영 후보입니다.

- 캐릭터/의상: `long_hair`, `wavy_hair`, `blunt_bangs`, `sidelocks`, `pink_hair`, `purple_eyes`, `school_uniform`, `white_shirt`, `red_bow`, `blue_jacket`, `gold_trim`, `capelet`
- 구도/대상: `upper_body`, `close-up`, `portrait`, `headshot`, `1girl`, `solo`, `cowboy_shot`, `wide_shot`, `full_body`
- 카메라/시선: `straight-on`, `facing_viewer`, `looking_at_viewer`, `dutch_angle`, `pov`, `from_above`, `from_below`
- 작은 연출: `sitting`, `standing`, `arms_at_sides`, `open_hands`, `reaching`, `outstretched_arm`, `outstretched_arms`, `pointing_forward`, `pointing_at_viewer`, `hand_on_own_chest`, `hand_on_own_hip`, `leaning`, `leaning_forward`
- 표정: `smile`, `sad`, `surprised`, `blush`, `tears`, `serious`, `closed_mouth`, `open_mouth`, `frown`
- 장소/조명: `auditorium`, `stage`, `curtains`, `spotlight`, `indoors`, `podium`, `presentation`, `bedroom`, `rooftop`, `street`, `park`, `library`, `sunset`, `night`, `window`, `sunlight`
- 초점/동세 보조: `depth_of_field`, `blurry_background`, `bokeh`, `motion_blur`, `motion_lines`

#### 7. 실행 / QA 규칙

1. 기본은 no-ref + pose LoRA on입니다.
2. 출력은 event_cg 규칙상 항상 16:9만 사용합니다(기본 1024x576).
3. 이 canonical route에는 `LoadImage`/PuLID reference conditioning을 추가하지 않습니다.
4. 자연어 prompt chunk나 DB에 없는 pseudo-tag를 추가하지 않습니다.
5. 로컬 Danbooru taxonomy SQLite에서 active/non-deprecated로 검증되는 `tag` 또는 active alias만 variable prompt에 사용합니다.
6. 기본 positive는 identity/outfit 중심으로 유지하고, 구도/카메라 강제 태그는 기본값에서 제외합니다.
7. 의상 드리프트를 더 줄이겠다고 기본 prompt를 장황하게 늘리지 않습니다. 같은 anchor에서 seed 후보를 더 뽑고 QA로 고릅니다.
8. QA 전에는 생성 에셋을 production-ready/final이라고 부르지 않습니다.
9. 출력은 `/history/{prompt_id}` 또는 output scan으로 정확한 파일 경로를 검증한 뒤 보고합니다.
