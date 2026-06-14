## 문서 규격(v1)

- workflow_id: `char_alpha`
- modality: `image`
- input_requirement: source image 필요
- output: transparent PNG
- prompt_policy: `no_prompt_or_minimal`
- editable_fields: 1.inputs.image, 3.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### ✂️ 배경 투명화 / alpha 워크플로우

#### 1. 목적

이 workflow는 이미 QA된 캐릭터/source/outfit/expression 이미지를 transparent PNG/sprite cutout 후보로 변환합니다.

프롬프트를 사용하지 않습니다. Danbooru tag oracle은 upstream 이미지 생성 단계에서만 관련이 있고, alpha 생성 단계에서는 시각적으로 승인된 source image를 그대로 넣어야 합니다.

#### 2. Runtime patch 대상

Toolkit runner:

```bash
python tools/run_char_alpha_smoke.py \
  --project-root <REN PY PROJECT ROOT> \
  --asset-id <transparent sprite asset id> \
  --source-image <project-confined source image> \
  --prepare-only
```

또는 source metadata에서 첫 번째 usable `candidate_copies`/`output_paths` 이미지를 가져올 수 있습니다:

```bash
python tools/run_char_alpha_smoke.py \
  --project-root <REN PY PROJECT ROOT> \
  --asset-id <transparent sprite asset id> \
  --source-metadata <project-confined source metadata.json> \
  --prepare-only
```

Runner contract:

- `--source-image`와 `--source-metadata` 중 정확히 하나만 사용합니다.
- source image/source metadata는 selected project root 아래에 있어야 합니다.
- source image는 active ComfyUI input root로 staged copy됩니다. Project contract에 `comfyui_input_root`가 없으면 `docs/automation/comfyui_input/` fallback을 사용합니다.
- `LoadImage.inputs.image`에는 staged file name만 넣습니다.
- `SaveImage.inputs.filename_prefix`는 run마다 `hermes_vn_char_alpha/<run_id>`로 patch합니다.
- `--prepare-only`는 ComfyUI 제출 없이 patched workflow와 metadata만 기록합니다.
- live generation output은 후보로만 기록되며 promotion은 별도 owner approval gate가 필요합니다.

Runtime patch fields:

- `LoadImage.inputs.image`: active Windows ComfyUI `input/` 폴더에 존재하는 source image filename.
- `SaveImage.inputs.filename_prefix`: run마다 고유한 output prefix.

Canonical JSON을 직접 덮어쓰지 말고 runtime payload/copy에서만 위 값을 바꿉니다.

#### 3. Source 보존 guard

- 이 workflow는 source image를 재해석/재생성하지 않고 배경 제거/alpha 생성만 해야 합니다.
- 입력 이미지는 이미 QA된 캐릭터/source/outfit/expression 결과여야 합니다.
- 머리색, 헤어스타일, 눈색, 의상, 표정 같은 원본 특징을 바꾸는 prompt 단계가 없습니다.
- alpha 결함을 해결하려고 다른 캐릭터 이미지를 넣거나 upstream 특징을 임의로 바꾸지 않습니다.
- source가 여러 개면 가장 최근 이미지를 추측하지 말고, 사용할 source image를 확인합니다.

#### 4. QA 규칙

- hair edge와 alpha edge가 깨끗한지 확인합니다.
- 손가락, 머리카락, 의상 끝, 장신구 등 얇은 부분이 누락되지 않았는지 확인합니다.
- 배경 찌꺼기나 halo가 남지 않았는지 확인합니다.
- 밝은 배경/어두운 배경/중립 배경에서 모두 확인하기 전에는 production-ready로 부르지 않습니다.
- 여기서 tag를 추가해 alpha 결함을 해결하려고 하지 않습니다. 결함이 크면 source image를 다시 고르거나 upstream workflow에서 재생성합니다.
