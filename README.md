# ComfyUI 게임 에셋 생성 워크플로우 팩

이 폴더는 게임 제작 중 필요한 visual novel / dating-sim / game 에셋을 AI agent의 도움으로 ComfyUI에서 생성하기 위한 workspace-level source of truth입니다.

이 pack은 단순한 ComfyUI workflow 보관함이 아니라, 게임을 AI agent와 함께 제작하면서 필요한 에셋 후보를 즉시 뽑기 위한 실행 계약입니다. 사용자가 “소품 CG 만들어줘”, “이 장면에 쓸 캐릭터 CG가 필요해”, “교실 배경 뽑아줘”처럼 말하거나, agent가 현재 구현 중인 장면에서 필요한 에셋을 스스로 판단하면, agent는 이 문서와 각 workflow README를 읽고 적절한 workflow를 골라 runtime payload만 패치해 ComfyUI에 제출합니다.

생성 결과는 곧바로 최종 게임 에셋이 아니라 QA/promote 전의 후보입니다. 실제 게임 리소스로 승격할지는 사용자 또는 agent의 artifact QA 이후 결정합니다.

Windows workspace path:
`E:\workspace\comfyui-game-asset-workflows`

Hermes/Windows bash path:
`E:/workspace/comfyui-game-asset-workflows`

Legacy Linux-bridge source paths are historical reference only and should not be used for new work.

## 현재 구조

현재 pack은 의미 기반의 flat folder 구조를 사용합니다. 예전 번호식 `01_*`, `02_*`, `03_*` 폴더 계약은 더 이상 사용하지 않습니다.

각 workflow 폴더는 다음 파일을 포함합니다.

- `README.md` — 해당 workflow의 프롬프트 작성법과 운영 가이드. 재현에 필요한 원칙/태그/절차만 적고, 일회성 실험 로그·출력 경로·prompt_id·contact sheet 목록은 넣지 않습니다.
- `*_workflow_api.json` — canonical ComfyUI API graph template.

현재 canonical folder 목록:

| 폴더 | 목적 | 메인 API JSON |
|---|---|---|
| `char_base` | 기본 캐릭터/source image와 same-seed outfit/costume variant 생성. | `char_base/char_base_workflow_api.json` |
| `char_expression` | 캐릭터 source image에서 얼굴/표정 variant 생성. | `char_expression/char_expression_workflow_api.json` |
| `char_alpha` | source character image를 transparent PNG / alpha output으로 변환. | `char_alpha/char_alpha_workflow_api.json` |
| `scene_background` | 캐릭터 없는 16:9 VN 배경 생성. | `scene_background/scene_background_workflow_api.json` |
| `scene_prop_cg` | 16:9 소품 / 단서 / item cut-in CG 생성. | `scene_prop_cg/scene_prop_cg_workflow_api.json` |
| `scene_event_cg` | no-reference txt2img + pose LoRA로 16:9 character event CG 생성. 캐릭터/의상 일관성은 캐릭터 metadata anchor와 prompt tag로 유지합니다. | `scene_event_cg/scene_event_cg_workflow_api.json` |
| `ui_system_alert_frame` | Textless red/ornate VN system alert frame 후보 생성. Ren'Py text overlay preview는 QA/통합 확인용이며, `scene_prop_cg`와 분리된 UI 전용 route입니다. | `ui_system_alert_frame/ui_system_alert_frame_workflow_api.json` |
| `audio_bgm_with_sfx` | Stable Audio 3 기반 통합 BGM/SFX/One-shot 후보 생성. | `audio_bgm_with_sfx/audio_bgm_with_sfx_workflow_api.json` |

## AI agent 시작 지점

AI agent가 이 pack으로 에셋을 생성하거나 문서를 점검할 때는 다음 순서로 읽습니다.

1. 루트 `README.md`를 읽습니다.
2. `WORKFLOW_INDEX.json`을 읽고 workflow path, editable field, input placeholder를 확인합니다.
3. `AGENTS.md`를 읽고 실행 규칙을 확인합니다.
4. target workflow folder의 `README.md`를 읽고 prompt template과 주의사항을 확인합니다.
5. 기존 캐릭터 기반 에셋이면 프로젝트의 `docs/assets/characters/*.asset.json` sidecar를 읽고, workflow별로 필요한 metadata subset만 prompt로 조립합니다.
6. target `*_workflow_api.json`을 load하고, index에 적힌 editable field만 runtime patch합니다.

사용자가 “README 프롬프트를 수정했다”고 말하면, 기존 기억이나 이전 run prompt를 재사용하지 말고 target README를 즉시 다시 읽습니다.

## 사용자/장면 요청 라우팅 가이드

게임 제작은 보통 AI agent와 함께 진행되므로, 사용자가 매번 workflow 이름을 직접 말하지 않아도 됩니다. Agent는 현재 장면 구현 맥락과 사용자 자연어 지시를 보고 필요한 에셋 종류를 판단한 뒤 아래 기준으로 workflow를 선택합니다.

| 사용자 또는 장면 맥락 | 사용할 workflow | 입력 이미지 | 판단 기준 / 주의사항 |
|---|---|---|---|
| “캐릭터 CG 만들어줘”, “이벤트 CG 뽑아줘”, “이 장면용 캐릭터 일러스트가 필요해” | `scene_event_cg` | 없음 | 16:9 캐릭터 CG입니다. 사용자가 source/base/anchor를 명시하지 않았다면 `char_base`로 가지 않습니다. 기존 캐릭터 기반이면 캐릭터 metadata의 identity/outfit/framing anchor를 먼저 사용합니다. |
| 새 캐릭터의 기본 source, anchor, base image가 필요함 | `char_base` | 없음 | downstream expression/event workflow에 넣을 기준 캐릭터 이미지를 만듭니다. |
| 표정만 바꾸고 싶음, 대사창용 표정 variation이 필요함 | `char_expression` | source character image | 몸/의상을 유지하고 얼굴/표정만 바꾸는 route입니다. |
| 투명 배경 PNG, sprite cutout, 배경 제거가 필요함 | `char_alpha` | source image | QA된 캐릭터/표정/의상 이미지를 transparent PNG 후보로 만듭니다. |
| 의상 변경, costume variation이 필요함 | `char_base` | 없음 | 같은 seed와 identity/framing tag를 유지하고 outfit block만 바꾸는 route를 사용합니다. 기존 `char_outfit` source-image inpaint route는 backup으로 이동했습니다. |
| 교실, 복도, 방, 거리 같은 VN 배경이 필요함 | `scene_background` | 없음 | 캐릭터 없는 16:9 배경을 생성합니다. |
| 소품 CG, 단서 이미지, item cut-in이 필요함 | `scene_prop_cg` | 없음 | 16:9 단일 소품 후보를 생성합니다. 전체 소품이 보여야 하면 과한 close-up/detail 태그를 줄입니다. |
| VN 시스템 알림창, 경고/계약 알림 UI frame, textless message frame이 필요함 | `ui_system_alert_frame` | 없음 | 소품이 아니라 UI frame입니다. frame/ornament 제작이 1차 목표이고, Ren'Py overlay preview는 QA입니다. 중앙 plate와 외곽 ornament를 분리 QA하고, baked text/logo/symbol/nameplate/object는 reject합니다. |
| 장면 BGM, 루프 가능한 음악, 대사용 배경음악이 필요함 | `audio_bgm_with_sfx` | 없음 | Stable Audio 3 기반 통합 engine을 `audio_bgm` role로 사용합니다. prompt는 `instrumentation + musical form/rhythm + mood + short role`처럼 음악 정체성을 먼저 둡니다. raw MP3는 source 후보이며, Ren'Py용은 무음 trim + fade loop edit + OGG 변환 후 loop preview 청감 QA가 필요합니다. |
| 문 열림, 발소리, 마법 crack 같은 짧은/중간/긴 효과음이 필요함 | `audio_bgm_with_sfx` | 없음 | Stable Audio 3 기반 통합 engine을 `audio_sfx` role로 사용합니다. prompt는 짧은 positive 자연어 cue + 재질/음색 1~2개가 기본이며, 상황에 따라 `One-shot`/`SFX` mode와 duration을 조절합니다. trim/normalize와 listening QA가 필요합니다. |
| 포즈나 액션이 있는 장면 일러스트가 필요함 | `scene_event_cg` | 없음 | `pose_variations`는 제거되었습니다. Dialogue sprite 재생성이 아니라 event CG로 처리합니다. 기존 캐릭터 기반이면 캐릭터 metadata anchor를 고정한 뒤 작은 staging/background/seed만 바꿉니다. |

중요한 용어 구분:

- “캐릭터 CG”는 기본적으로 `scene_event_cg`입니다.
- `char_base`는 “캐릭터 앵커/source/base”와 same-seed outfit/costume variant를 만듭니다.
- “대사 중 서 있는 캐릭터 sprite”는 보통 `char_base` same-seed outfit 후보 → `char_expression` → `char_alpha` route로 만듭니다.
- “장면 삽화 / 이벤트 일러스트 / 포즈 있는 CG”는 `scene_event_cg`로 만듭니다.
- “BGM / 배경음악 / 루프 음악”은 `audio_bgm_with_sfx`의 `audio_bgm` role로 만듭니다.
- “효과음 / SFX / 문소리 / 발소리 / 마법 소리”는 `audio_bgm_with_sfx`의 `audio_sfx` role로 만듭니다. SFX는 길이가 항상 짧지는 않으므로 장면 기능에 맞게 `One-shot`/`SFX` mode와 duration을 조절하고, trim/normalize/listening QA를 거칩니다.

## 에셋 생성 lifecycle

1. 요청 또는 장면 필요 인식
   - 사용자 지시 또는 agent의 게임 구현 맥락에서 필요한 에셋을 판단합니다.
2. 라우팅
   - 위 표에 따라 가장 작은 적절한 workflow를 선택합니다.
3. 프롬프트 작성
   - target workflow README의 템플릿을 읽고 모든 placeholder를 실제 태그/문장으로 채웁니다.
   - 기존 캐릭터 기반 에셋은 README 샘플 prompt나 과거 PNG metadata를 직접 복붙하지 말고, 캐릭터 metadata sidecar에서 `identity_anchor`, `outfits`, `expression_map`, `framing_defaults`를 읽어 조립합니다.
   - prompt에는 target workflow README에 문서화된 태그와 로컬 Danbooru taxonomy SQLite tag oracle에서 active/non-deprecated로 검증되는 태그만 사용합니다.
   - DB에 없는 자연어 chunk, pseudo-tag, 오래된 helper script 출력은 사용하지 않습니다.
4. Runtime patch
   - canonical JSON은 직접 수정하지 않고, runtime payload/copy의 editable field만 바꿉니다.
5. ComfyUI 제출
   - backend, queue, object_info, input image 존재 여부를 확인한 뒤 `/prompt`에 제출합니다.
6. 후보 생성
   - 결과는 ComfyUI output folder에 저장됩니다.
7. QA
   - 캐릭터 identity, 의상 drift, 소품 잘림, 가짜 텍스트, 배경 구도, alpha edge 등을 확인합니다.
8. Promote 또는 재시도
   - 마음에 드는 후보만 game asset directory로 승격하고, 나머지는 prompt/runtime 설정을 조정해 다시 생성합니다.

## Workflow 역할 구분

일반적인 asset flow는 다음과 같습니다.

1. `char_base` — opaque base/source character와 same-seed outfit/costume variant를 생성합니다.
2. `char_alpha` — 승인된 character source/outfit/expression 후보를 transparent PNG로 변환합니다.
3. `char_expression` — source character image에서 표정 variant를 만듭니다.
4. `scene_background` — 16:9 scene background를 만듭니다.
5. `scene_prop_cg` — Ren'Py 연출용 16:9 prop/clue cut-in을 만듭니다.
6. `scene_event_cg` — no-reference txt2img + pose LoRA로 full 16:9 event CG를 만듭니다. 캐릭터/의상 일관성은 metadata anchor와 prompt tag로 유지하며, 제거된 `pose_variations` sprite route 대신 특수 포즈/액션 illustration에 사용합니다.
7. `ui_system_alert_frame` — textless VN system alert frame 후보를 만듭니다. 소품 CG와 분리하고, frame identity / 중앙 plate / 외곽 ornament / baked content를 별도로 QA합니다. Ren'Py overlay preview는 통합 QA입니다.
8. `audio_bgm_with_sfx` — Stable Audio 3 기반 통합 route로 BGM/SFX/One-shot 후보를 만듭니다.

이 폴더들은 필수 linear pipeline이 아니라 재사용 도구입니다. 현재 장면에 필요한 가장 작은 workflow를 선택합니다.

## 생성 결과 저장 위치

이 workflow pack 자체에는 생성 이미지/오디오를 저장하지 않습니다. ComfyUI의 `SaveImage.inputs.filename_prefix`에 따라 active Windows ComfyUI output directory 아래에 저장됩니다.

현재 이 환경의 ComfyUI 경로:

- Windows output root: `C:\Users\Desktop\Documents\ComfyUI\output`
- Windows output root: `C:/Users/Desktop/Documents/ComfyUI/output`
- Windows input root: `C:\Users\Desktop\Documents\ComfyUI\input`
- Windows input root: `C:/Users/Desktop/Documents/ComfyUI/input`

예를 들어 runtime에서 `filename_prefix`를 `<unique_run_folder>/scene_event_cg_scene`으로 패치하면 결과는 active output root 아래 `<unique_run_folder>/...`에 생성됩니다.

Agent는 생성 후 `/history/{prompt_id}` 또는 output folder scan으로 실제 파일명을 확인하고, 예시 경로가 아니라 exact output path를 보고해야 합니다.

QA 후 실제 게임 프로젝트에 사용할 이미지만 별도 game asset directory로 promote합니다. 이 workflow pack 안으로 생성 이미지를 복사하지 않습니다.

## Canonical JSON 취급 규칙

일반 생성 중에는 canonical API JSON을 덮어쓰지 않습니다.

권장 패턴:

1. canonical `*_workflow_api.json`을 canonical folder 밖의 runtime/sandbox 위치로 deep-copy하거나, 메모리에서만 payload를 복사합니다.
2. prompt, seed, input image name, output prefix, 명시적으로 허용된 parameter만 patch합니다.
3. runtime payload를 ComfyUI에 제출합니다.
4. 생성 결과는 reusable pack 안이 아니라 ComfyUI output folder나 명시적인 sandbox/output 위치에 둡니다.
5. canonical JSON 변경은 사용자 QA/승인 후에만 promote합니다.

## Placeholder와 input file 규칙

일부 template에는 다음 placeholder가 의도적으로 들어 있습니다.

- `TEMPLATE_character_anchor_source.png`
- `TEMPLATE_source_image.png`
- `TEMPLATE_featureless_mannequin_source.png`
- `TEMPLATE_*` output prefix fragment
- `{감정표현}`, `{배경 테마 및 장소}`, `{아이템 이름 및 형태}` 같은 한국어 prompt placeholder

Live ComfyUI 제출 전 agent는 이것들을 실제 ComfyUI `input/` filename, prompt text, seed, output prefix로 교체해야 합니다.

Input image가 필요한 workflow에서 사용자가 특정 이미지를 지정하지 않았다면:

- “방금 뽑은 캐릭터”, “이 캐릭터”처럼 맥락이 분명할 때만 가장 최근의 관련 image를 사용합니다.
- 후보가 여러 개이거나 source가 불분명하면 사용자에게 물어봅니다.
- 관계없는 오래된 이미지를 조용히 사용하지 않습니다.
- `LoadImage.inputs.image`에 넣기 전에 active Windows ComfyUI `input/` directory에 파일이 실제로 있는지 확인합니다.

Source/metadata 보존 guard:

- `char_expression`, `char_alpha`처럼 source image가 있는 workflow는 원본 이미지의 캐릭터 특징을 보존하는 route입니다. hair length/style/color, eye color, face identity, 핵심 의상/표정 상태를 임의로 바꾸지 않습니다. `char_base` 의상 variant는 source image 없이 same seed + identity/outfit prompt tag로 일관성을 유지합니다.
- `scene_event_cg`처럼 현재 no-ref route인 workflow는 source image 대신 승인된 character metadata/sidecar의 `identity_anchor`와 outfit block을 원본 특징 guard로 사용합니다.
- prompt slot의 `{헤어 길이}`, `{헤어 스타일}`, `{머리색}`, `{눈색}`은 새로 창작하는 칸이 아니라 source/metadata에서 가져오는 칸입니다.
- source/metadata와 충돌하는 tag를 추가해야 할 것 같으면 runtime 제출 전에 멈추고 사용자 확인 또는 sidecar 업데이트가 필요합니다.

## Prompt 작성 규칙

각 workflow folder의 `README.md`가 해당 workflow의 prompt contract입니다.

Live generation 전:

- target workflow README를 다시 읽습니다.
- `{감정표현}`, `{배경 테마 및 장소}`, `{아이템 이름 및 형태}` 같은 placeholder를 모두 채웁니다.
- README의 prompt ordering을 기본적으로 유지합니다.
- 사용자가 README를 수정했다고 말하면 즉시 다시 읽습니다.
- unresolved placeholder를 ComfyUI에 제출하지 않습니다.
- 이미지 workflow의 variable prompt에는 로컬 Danbooru taxonomy SQLite tag oracle에서 active/non-deprecated로 검증되는 tag/alias만 사용합니다. DB에 없는 자연어 구도 보정은 이미지 prompt에 넣지 말고 workflow 선택, seed/settings, 별도 배경/소품/overlay, Ren'Py staging으로 해결합니다. audio workflow는 해당 README가 명시한 자연어 prompt 규칙을 따릅니다.

## QA와 promote 규칙

Workflow가 runnable하다는 것은 production-approved와 다릅니다.

생성 결과는 다음 기준으로 확인합니다.

### Character / event CG

- identity drift
- hair color/style drift
- outfit drift
- hand/anatomy issue
- framing
- unwanted duplicate character
- background lighting/composition integration

### Prop CG

- 단일 main prop 여부
- 전체 object가 잘리지 않고 보이는지
- fake text/logo 여부
- 불필요한 duplicate object 여부

### Background

- 사람/캐릭터가 없는지
- fake text/signage가 없는지
- VN composition으로 사용 가능한지
- 캐릭터를 세울 foreground/headroom 여유가 있는지

### UI / System alert frame

- red/ornate VN system alert frame으로 먼저 읽히는지
- 중앙 plate가 깨끗하고 외곽 ornament와 분리되어 있는지
- 외곽 ornament가 중앙 plate를 침범하지 않고 frame/border로 읽히는지
- baked text/logo/symbol/nameplate/icon/emblem/object가 없는지
- Korean sample text overlay preview에서 명백한 통합 blocker가 없는지
- 승인 전 `game/images/ui/`로 promote하지 않았는지

### Transparent PNG

- alpha edge
- hair edge
- body part 누락
- leftover background artifact

### Audio / BGM / SFX

- `ffprobe`로 duration/audio stream이 정상인지 확인
- BGM은 vocal/lyrics가 섞이지 않았는지 listening QA
- BGM은 raw MP3를 그대로 promote하지 않고 무음 trim/fade/OGG 변환/2회 loop preview를 만든 뒤 loop 지점이 너무 튀지 않는지 확인
- SFX는 불필요한 voice/music/말소리가 섞이지 않았는지 확인
- 대사와 충돌하지 않는 볼륨/밀도인지 확인
- Ren'Py promote 전 BGM은 편집본 OGG로 `play music ... loop` smoke, SFX는 single-hit 편집본 OGG로 `play sound` smoke

사용자가 직접 눈으로 QA하겠다고 하면 agent는 품질을 단정하지 말고 prompt id, seed, runtime JSON path, output path만 보고합니다.

## 고정 상태

현재 canonical pack은 위에 적힌 8개 workflow 폴더로 의도적으로 제한합니다. `pose_variations`는 canonical pack에서 제거되었으므로, 포즈/액션이 필요한 경우 dialogue sprite 재생성이 아니라 16:9 `scene_event_cg`로 처리합니다.

고정 전 audit 상태:

- canonical API JSON 파일은 pack maintenance 시 모두 정상 파싱되어야 합니다.
- `WORKFLOW_INDEX.json`은 실제 존재하는 workflow 폴더와 API 파일만 가리킵니다.
- 각 그래프를 출력 노드에서 역방향으로 추적했을 때 미사용/분리 노드는 발견되지 않았습니다.
- 존재하지 않는 노드를 참조하는 dangling reference는 발견되지 않았습니다.
- `WORKFLOW_INDEX.json`은 editable field, primary node, placeholder, observed default의 machine-readable 기준 문서입니다.
- 각 workflow README는 간결한 운영 가이드로 유지합니다. 실험 이력이나 일시적인 튜닝 노트를 넣기 위해 수정하지 않습니다.

최신 audit report는 현재 game project root의 `.analysis/` 아래에서 확인합니다. Windows 이관 후 active workspace 기준은 `E:\workspace\renpy-project`입니다.

## 현재 주의사항

- 현재 폴더명은 번호식 이름이 아니라 flat semantic name입니다. 예전 `01_*`부터 `07_*`까지의 참조는 stale일 수 있습니다.
- `scene_background`와 `scene_prop_cg`는 이미지 입력이 없는 16:9 txt2img 계열 workflow입니다.
- `audio_bgm_with_sfx`는 이미지/영상 입력이 없는 local Stable Audio 3 workflow입니다. BGM, SFX, One-shot 모두 이 통합 route로 생성합니다.
- `char_expression`, `char_alpha`는 runtime에서 `LoadImage.inputs.image`를 실제 ComfyUI input 파일명으로 패치해야 합니다. `char_base`와 `scene_event_cg`는 현재 canonical 기준으로 `LoadImage`가 없는 txt2img route입니다.
- `pose_variations`는 pose/action sprite 테스트에서 색감/의상/구도/해부학 drift가 커서 canonical pack에서 제거했습니다. 포즈/액션 CG는 `scene_event_cg`로 처리하고, dialogue sprite는 `char_base` same-seed outfit → `char_expression` → `char_alpha` 경로를 유지합니다.
- 일부 README의 prompt 텍스트는 운영 가이드이며, `Positive prompt`/`Negative prompt`로 명시된 canonical block은 해당 workflow JSON과 동기화합니다. 실행 가능한 node/field 기준은 `WORKFLOW_INDEX.json`과 실제 JSON입니다.
- 로컬 `danbooru-taxonomy.release.sqlite`는 README tag note의 primary 검증 기준입니다. DB에서 active/non-deprecated로 확인되거나 실제 생성물로 테스트된 태그가 아니라면, 기억이나 실패한 web fetch 기반으로 tag guidance를 추가하지 않습니다.
