# 설치 및 재현 가이드

이 저장소는 워크플로 JSON만 포함합니다. 모델과 생성 결과는 Git에 넣지 않습니다. 검증 기준은 `dependencies/manifest.json`이며 모델 파일 8개, 커스텀 노드 3개, Danbooru taxonomy DB를 버전·크기·SHA-256으로 고정합니다.

## 1. 요구사항

- ComfyUI: `dependencies/manifest.json`의 tested commit 이상
- Python 3.11 이상
- `git`, `uv`, `ffmpeg`, `ffprobe`
- 모델 저장 공간: 약 23.36 GiB
- 생성 결과와 캐시를 위한 추가 여유 공간

저장소 도구 의존성:

```bash
python -m pip install -r requirements.txt
```

## 2. 환경 변수

경로를 저장소 파일에 하드코딩하지 않습니다.

```bash
export COMFYUI_URL=http://127.0.0.1:8188
export COMFYUI_ROOT=/path/to/ComfyUI/workspace
export COMFYUI_MODEL_DIR="$COMFYUI_ROOT/models"
export COMFYUI_INPUT_DIR="$COMFYUI_ROOT/input"
export COMFYUI_OUTPUT_DIR="$COMFYUI_ROOT/output"
export WORKFLOW_RUNTIME_DIR="$PWD/.runtime"
```

`COMFYUI_ROOT`는 이 설치 가이드의 편의를 위한 변수이며, 기계 판독 계약은 `WORKFLOW_INDEX.json`의 `paths`를 따릅니다.

## 3. 모델과 taxonomy 다운로드

모든 모델과 DB를 받고 SHA-256까지 확인합니다.

```bash
python scripts/manage_dependencies.py \
  --model-root "$COMFYUI_MODEL_DIR" \
  download --models --taxonomy
```

중단되면 같은 명령을 다시 실행합니다. `.part` 파일에서 HTTP Range 재개를 시도하며, 서버가 Range를 지원하지 않으면 해당 파일을 처음부터 다시 받습니다. 최종 파일은 크기와 SHA-256이 모두 일치한 뒤에만 배치됩니다.

검증:

```bash
python scripts/manage_dependencies.py \
  --model-root "$COMFYUI_MODEL_DIR" \
  check
```

`--fast`는 크기만 검사하므로 최종 재현성 판정에는 사용하지 않습니다.

## 4. 커스텀 노드 설치

`dependencies/manifest.json`의 commit을 그대로 사용합니다.

```bash
mkdir -p "$COMFYUI_ROOT/custom_nodes"

git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git \
  "$COMFYUI_ROOT/custom_nodes/ComfyUI-Impact-Pack"
git -C "$COMFYUI_ROOT/custom_nodes/ComfyUI-Impact-Pack" \
  checkout 429d0159ad429e64d2b3916e6e7be9c22d025c3c

git clone https://github.com/ltdrdata/ComfyUI-Impact-Subpack.git \
  "$COMFYUI_ROOT/custom_nodes/ComfyUI-Impact-Subpack"
git -C "$COMFYUI_ROOT/custom_nodes/ComfyUI-Impact-Subpack" \
  checkout 50c7b71a6a224734cc9b21963c6d1926816a97f1

git clone https://github.com/1038lab/ComfyUI-RMBG.git \
  "$COMFYUI_ROOT/custom_nodes/ComfyUI-RMBG"
git -C "$COMFYUI_ROOT/custom_nodes/ComfyUI-RMBG" \
  checkout 58f1947a11567a9f8b707223185570850e773856
```

각 저장소의 `requirements.txt`는 반드시 ComfyUI가 실제로 사용하는 Python 환경에 설치합니다. 설치 후 ComfyUI를 재시작하고 `/object_info`에서 manifest의 `classes`가 모두 보이는지 확인합니다.

`face_yolov9c.pt`는 pickle 기반 PyTorch 파일입니다. manifest에 기록된 고정 URL과 SHA-256 외의 파일로 대체하지 마십시오.

## 5. 정적 검증

```bash
python -m unittest discover -s tests -v
python scripts/workflow_pack.py validate
```

두 명령이 모두 성공해야 runtime 생성 단계로 진행합니다.

모델·노드 설치 후 7개 canonical workflow를 실제로 순차 실행하는 저비용 smoke test:

```bash
python scripts/e2e_smoke.py \
  --url "$COMFYUI_URL" \
  --input-root "$COMFYUI_INPUT_DIR" \
  --output-root "$COMFYUI_OUTPUT_DIR"
```

`char_base → char_expression → char_alpha`는 실제 생성 파일을 다음 workflow의 input으로 복사하고, 나머지 이미지·오디오 workflow도 실행합니다. 생성형 UI workflow는 포함하지 않습니다. 성공 보고서는 `.runtime/e2e_<run-id>_report.json`에 저장됩니다.

## 6. 안전한 runtime payload 생성

수정할 값은 dotted path를 key로 하는 JSON 파일에 기록합니다.

```json
{
  "3.inputs.text": "masterpiece, scenery, no_humans, classroom, sunset",
  "6.inputs.seed": 12345,
  "8.inputs.filename_prefix": "qa/scene_background_12345"
}
```

```bash
python scripts/workflow_pack.py render scene_background \
  --edits edits.json \
  --runtime-dir "$WORKFLOW_RUNTIME_DIR"
```

도구는 다음을 강제합니다.

- `editable_fields` 밖의 수정 거부
- unresolved placeholder가 있으면 제출용 JSON 생성 거부
- canonical JSON SHA-256 불변 확인
- runtime JSON과 metadata sidecar 생성

실제 제출은 별도 명령으로 수행합니다. `render` 출력의 `runtime_sha256` 값을 신뢰된 호출 흐름에서 즉시 보관하고 제출 시 전달해야 합니다. 수정 가능한 runtime 파일이나 metadata sidecar에서 이 값을 다시 계산하면 무결성 보호가 무효화됩니다. 완료된 `/history/{prompt_id}`를 읽고 history에 기록된 output 파일이 실제 output root에 존재하는지 확인하며, 각 artifact의 SHA-256을 보고합니다.

```bash
# render 명령이 반환한 runtime_sha256을 그대로 사용합니다.
RUNTIME_SHA256="<render-output-runtime_sha256>"
python scripts/workflow_pack.py submit "$WORKFLOW_RUNTIME_DIR/<runtime>.json" \
  --runtime-sha256 "$RUNTIME_SHA256" \
  --url "$COMFYUI_URL" \
  --output-root "$COMFYUI_OUTPUT_DIR"
```

## 7. QA와 promote

후보 파일의 SHA-256을 포함한 QA JSON을 작성하고 `status`를 명시적으로 `approved`로 바꾼 경우에만 승격합니다.

```json
{
  "status": "approved",
  "artifact_sha256": "<64-char-sha256>"
}
```

```bash
python scripts/workflow_pack.py promote candidate.png game/images/candidate.png --qa qa.json
```

복사 후 목적지 SHA-256이 다시 검증됩니다.

## 8. 라이선스 확인

모델마다 라이선스가 다릅니다. 특히 Nova Anime XL, Hina pose LoRA, Stable Audio 3는 동일한 조건으로 취급할 수 없습니다. 다운로드·로컬 평가 가능 여부와 결과물의 상업 이용 가능 여부도 별개입니다. 사용 또는 배포 전에 `LICENSES.md`와 각 manifest 항목의 `license_url`을 확인하십시오.
