# comfyui-game-asset-workflows Agent 지침

이 문서는 AI agent가 `comfyui-game-asset-workflows` pack을 사용해 게임 제작 중 필요한 에셋 후보를 ComfyUI에서 자동 생성할 때 따르는 실행 규칙입니다.

이 pack은 사용자가 workflow 이름을 직접 말하지 않아도, agent가 현재 게임 제작 맥락에서 필요한 에셋을 판단해 적절한 workflow를 선택하는 것을 전제로 합니다. 예를 들어 장면 구현 중 캐릭터가 들어간 16:9 일러스트가 필요하면 `scene_event_cg`, 단서 소품 이미지가 필요하면 `scene_prop_cg`, 대사용 표정 variant가 필요하면 `char_expression`를 선택합니다.

## 필수 읽기 순서

이 pack에서 생성, 점검, 수정 작업을 하기 전에는 반드시 다음 순서로 읽습니다.

1. 루트 `README.md`
2. 루트 `WORKFLOW_INDEX.json`
3. 이 `AGENTS.md`
4. target workflow folder의 `README.md`
5. target `*_workflow_api.json`

사용자가 “README를 수정했다”, “프롬프트를 바꿨다”고 말하면 이전 기억이나 이전 run prompt를 재사용하지 말고 target README를 즉시 다시 읽습니다.

## 현재 canonical folder

- `char_base`
- `char_expression`
- `char_alpha`
- `scene_background`
- `scene_prop_cg`
- `scene_event_cg`
- `audio_bgm_ace`
- `audio_sfx_mmaudio`

각 canonical API graph는 해당 folder 바로 아래의 `*_workflow_api.json`입니다.

## 자연어 요청에서 workflow 선택하기

사용자 지시나 게임 장면 맥락을 보고 가장 작은 적절한 workflow를 고릅니다.

- “캐릭터 CG”, “이벤트 CG”, “장면 일러스트”, 포즈/액션이 있는 16:9 캐릭터 그림 → `scene_event_cg`
- 새 캐릭터의 기준 source/base/anchor image 또는 same-seed 의상 variant → `char_base`
- 표정 변경, 대사용 표정 variant → `char_expression`
- 배경 제거, transparent PNG, sprite cutout → `char_alpha`
- 의상 변경, costume variant → `char_base` same-seed outfit route
- 캐릭터 없는 VN 배경 → `scene_background`
- 소품 CG, 단서 이미지, item cut-in → `scene_prop_cg`
- 장면 BGM, 배경음악, loopable music → `audio_bgm_ace`
- 문소리, 발소리, 마법 소리, 짧은 효과음 → `audio_sfx_mmaudio`

주의:

- “캐릭터 CG”를 `char_base`로 처리하지 않습니다. 사용자가 anchor/source/base를 명시하지 않았다면 `scene_event_cg`입니다.
- `pose_variations`는 제거되었습니다. 포즈/액션 CG는 `scene_event_cg`로 처리합니다.
- Dialogue sprite는 보통 `char_base` same-seed outfit 후보 → `char_expression` → `char_alpha` route를 사용합니다.

## Canonical template 수정 금지

일반적인 생성/test run에서는 canonical workflow JSON을 수정하지 않습니다.

정상 흐름:

1. canonical JSON을 메모리에서 복사하거나 runtime/sandbox 위치로 복사합니다.
2. runtime payload/copy만 patch합니다.
3. ComfyUI에 runtime payload를 제출합니다.
4. 생성 결과는 ComfyUI output folder 또는 별도 sandbox/output 위치에 둡니다.
5. canonical JSON 또는 README 수정은 사용자가 pack maintenance를 요청했거나, QA 후 promote를 명시적으로 승인했을 때만 합니다.

## Editable field 기준

`WORKFLOW_INDEX.json`이 authoritative editable-node map입니다.

자주 patch하는 field:

- `CLIPTextEncode.inputs.text`
- `KSampler.inputs.seed`
- workflow notes가 허용하는 `KSampler.inputs.steps/cfg/denoise`
- `LoadImage.inputs.image`
- `SaveImage.inputs.filename_prefix`
- audio workflow의 `SaveAudioMP3.inputs.filename_prefix` 또는 MMAudio `SaveAudio.inputs.filename_prefix`
- audio workflow의 prompt/duration/seed/BPM/loop 같은 README/index 허용 field
- no-input txt2img workflow에서 명시적으로 필요한 `EmptyLatentImage.inputs.width/height`
- workflow에서 명시적으로 허용한 LoRA/PuLID strength 등의 runtime parameter

Index에 없는 node를 임의로 수정하지 않습니다. 필요하면 runtime 실험으로만 처리하고, canonical 반영은 사용자 승인 후 진행합니다.

## Placeholder 규칙

Live ComfyUI 제출 전에 모든 placeholder를 실제 값으로 교체합니다.

일반적으로 교체해야 하는 예:

- `TEMPLATE_*`
- `{헤어 길이}`
- `{감정표현}`
- `{배경 테마 및 장소}`
- `{시간대 및 조명}`
- `{아이템 이름 및 형태}`
- `{재질 및 질감 디테일}`
- `{놓여있는 장소/배경}`
- `{캐릭터 의상/특징}`

ComfyUI에 unresolved placeholder를 제출하지 않습니다.

## Input image 선택 규칙

`LoadImage.inputs.image`가 필요한 workflow에서는 source image를 신중하게 선택합니다.

1. 사용자가 image path를 지정하면 그 이미지를 사용합니다.
2. 사용자가 “방금 뽑은 캐릭터”, “이 캐릭터”처럼 명확히 지칭하면 가장 최근의 관련 output을 사용합니다.
3. 현재 장면 구현 맥락에서 agent가 필요한 source를 알고 있고 후보가 하나뿐이면 그 이미지를 사용합니다.
4. 후보가 여러 개이거나 source가 불명확하면 사용자에게 물어봅니다.
5. 관계없는 오래된 이미지를 조용히 사용하지 않습니다.
6. 제출 전 active Windows ComfyUI `input/` directory에 파일을 복사하고 실제 존재 여부를 확인합니다.

## Source/metadata 보존 guard

- `char_expression`, `char_alpha`는 source image의 기존 캐릭터 특징을 보존하는 route입니다. hair length/style/color, eye color, face identity, 핵심 의상/표정 상태를 임의로 바꾸지 않습니다. `char_base` 의상 variant는 source image 대신 같은 seed와 identity/outfit prompt tag로 일관성을 유지합니다.
- `scene_event_cg`는 현재 no-ref route이므로 source image 대신 승인된 character metadata/sidecar의 `identity_anchor`와 outfit block을 원본 특징 guard로 사용합니다.
- prompt slot의 `{헤어 길이}`, `{헤어 스타일}`, `{머리색}`, `{눈색}`은 새로 창작하는 칸이 아니라 source/metadata에서 가져오는 칸입니다.
- source/metadata와 충돌하는 tag를 추가해야 할 것 같으면 runtime 제출 전에 멈추고 사용자 확인 또는 sidecar 업데이트가 필요합니다.

## Output 위치 규칙

이 pack의 생성 이미지는 workflow pack 폴더 안에 저장하지 않습니다. ComfyUI `SaveImage` node의 `filename_prefix` 기준으로 active Windows ComfyUI output directory 아래에 저장됩니다.

현재 환경 기준:

- Windows workspace root: `E:\workspace\comfyui-game-asset-workflows`
- Hermes/Windows bash workspace root: `E:/workspace/comfyui-game-asset-workflows`
- Windows output root: `C:\Users\Desktop\Documents\ComfyUI\output`
- WSL output root: `/mnt/c/Users/Desktop/Documents/ComfyUI/output`
- Windows input root: `C:\Users\Desktop\Documents\ComfyUI\input`
- WSL input root: `/mnt/c/Users/Desktop/Documents/ComfyUI/input`

Run마다 `SaveImage.inputs.filename_prefix`를 고유한 run folder 형태로 runtime patch합니다. 예:

`hermes_vn_event_YYYYMMDD_HHMMSS/scene_event_cg_scene`

생성 후에는 `/history/{prompt_id}`와 실제 output file 존재 여부를 확인해 exact path를 보고합니다. 추정 경로만 보고하지 않습니다.

## Live ComfyUI run 전 확인

제출 전 반드시 확인합니다.

- target backend 접근 가능 여부
- queue 상태
- `/object_info` 접근 가능 여부
- workflow에서 사용하는 custom node class 존재 여부
- runtime input image 존재 여부
- 모든 placeholder 교체 여부
- output prefix가 현재 run을 구분할 수 있는지
- audio workflow는 필요한 모델/node/auth 상태가 맞는지

Windows ComfyUI는 공유 환경으로 취급합니다. 사용자 승인 없이 queue를 clear하거나 ComfyUI를 restart하거나 custom node를 설치/삭제하지 않습니다.

## Prompt 작성 규칙

각 workflow folder README가 해당 workflow의 prompt contract입니다.

- target README를 읽고 그 템플릿 순서를 기본적으로 따릅니다.
- 한국어 placeholder를 실제 Danbooru tag 또는 해당 workflow README가 명시한 audio 자연어 prompt로 채웁니다. 이미지 workflow의 variable prompt는 local `danbooru_tag.csv`에 있는 tag/alias만 사용합니다.
- README에 사용자가 최근 수정한 prompt가 있으면 그 내용을 우선합니다.
- 단일 소품처럼 local `danbooru_tag.csv`에 정확한 태그가 없는 경우, README에 적힌 대체 전략을 따릅니다.
- 캐릭터 보존이 중요하면 metadata/source 기준의 identity/hair/eye/outfit tag를 유지하고, 큰 action/pose tag는 줄입니다. `char_base` outfit variant는 같은 seed에서 outfit block만 교체합니다. `scene_event_cg`는 현재 no-ref route이므로 source image reference가 아니라 metadata anchor를 사용합니다.

## Reporting style

사용자가 직접 시각 QA를 할 가능성이 높으므로, 기본 보고는 간결한 evidence 중심으로 합니다.

보고할 것:

- 사용한 workflow
- input image path 또는 ComfyUI input filename
- runtime JSON path, 있다면
- prompt id
- seed
- exact output path
- 사용자가 확인해야 할 QA 포인트

하지 말 것:

- 실제 artifact를 보지 않았는데 production quality라고 말하지 않기
- 사용자가 QA하겠다고 한 이미지에 대해 과도한 미적 평가를 invent하지 않기
- canonical JSON을 수정하지 않았는데 수정했다고 말하지 않기
- runtime-only patch를 canonical 변경처럼 표현하지 않기

## 생성 결과 QA 포인트

### Character / event CG

- no-ref event CG는 metadata anchor와 현재 prompt 기준으로 hair/eye/face가 유지되는지
- outfit drift가 과한지
- 손/팔/몸 anatomy가 깨졌는지
- duplicate character가 생겼는지
- 16:9 framing이 장면에 쓸 수 있는지
- 배경과 캐릭터 조명 통합이 자연스러운지

### Prop CG

- main prop이 하나인지
- object가 잘리지 않고 전체가 보이는지
- duplicate object가 생겼는지
- fake text/logo/UI가 생겼는지
- 너무 과한 close-up이나 macro crop이 아닌지

### Background

- 사람/캐릭터가 없는지
- fake sign/text가 없는지
- VN character를 세울 공간이 있는지
- 구도와 원근이 사용할 수 있는지

### Transparent PNG

- hair edge와 alpha edge가 깨끗한지
- body part가 누락되지 않았는지
- 배경 찌꺼기가 남지 않았는지

### Audio / BGM / SFX

- `ffprobe`로 duration/audio stream 확인
- BGM은 vocal/lyrics가 섞이지 않았는지 listening QA
- BGM은 raw MP3를 그대로 promote하지 않고 `scripts/final_edit_ace_bgm_loop.py`로 무음 trim/fade/OGG 변환/2회 loop preview를 만든 뒤 loop 지점과 대사 방해 여부 확인
- SFX는 불필요한 voice/music/말소리가 섞이지 않았는지 확인
- Ren'Py promote 전 BGM은 loop-edit OGG로 `play music ... loop` smoke, SFX는 single-hit OGG로 `play sound` smoke

## Pack maintenance 완료 전 검증

문서나 canonical 파일을 수정한 뒤에는 다음을 확인합니다.

- `WORKFLOW_INDEX.json`에 적힌 모든 file path가 존재합니다.
- 모든 `*_workflow_api.json`이 JSON parse됩니다.
- 루트 문서/index가 예전 numbered folder path를 요구하지 않습니다.
- 의도한 파일만 변경되었습니다.
- canonical workflow JSON은 사용자 승인 없이 수정되지 않았습니다.
- README 문서는 사용자도 읽을 수 있도록 한국어로 유지합니다.
