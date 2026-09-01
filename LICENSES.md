# 라이선스 및 재배포 상태

## 저장소 코드와 문서

이 저장소에서 직접 작성한 코드, 문서 및 workflow 정의는 루트 `LICENSE`의 Apache License 2.0에 따라 배포됩니다. Apache-2.0은 조건을 준수하는 개인·연구·상업적 사용, 수정 및 재배포를 허용합니다. 다만 아래 외부 모델, 데이터베이스와 커스텀 노드는 각 upstream 라이선스를 별도로 따르며 루트 라이선스의 적용 대상으로 간주하면 안 됩니다.

## 워크플로와 외부 모델

워크플로 JSON에 모델 파일이 포함되어 있지 않더라도 각 모델의 사용 조건은 그대로 적용됩니다. `dependencies/manifest.json`은 다운로드 URL과 알려진 라이선스 상태를 기록하지만 법률 자문을 제공하지 않습니다.

| 구성요소 | manifest ID | 현재 기록된 상태 |
|---|---|---|
| Nova Anime XL IL v19 | `nova-anime-xl-il-v19` | Civitai creator의 모델별 상업 이용 제한 확인 필요 |
| Xinsir ControlNet Union SDXL | `xinsir-controlnet-union-sdxl-promax` | upstream 라이선스와 재배포 조건 확인 필요 |
| Hina Maybe Better Pose XL v5 | `hina-maybe-better-pose-xl-v5` | 명시적인 모델 카드 라이선스를 확인하지 못했으므로 권리 확인 전 로컬 평가 전용 |
| face_yolov9c | `face-yolov9c` | pickle 기반 파일이며 고정 SHA-256만 사용; upstream 데이터·모델 라이선스 확인 필요 |
| Segment Anything ViT-B | `sam-vit-b` | Segment Anything Apache-2.0; 미러의 재배포 조건도 확인 |
| Stable Audio 3 Medium | `stable-audio-3-medium` | Stability AI Community License |
| T5Gemma encoder | `t5gemma-b-b-ul2` | Stable Audio 및 적용 가능한 encoder 조건 확인 |
| Qwen 3.5 2B | `qwen-3.5-2b-bf16` | Apache-2.0 |
| Danbooru taxonomy DB | `danbooru-taxonomy-26.05.23` | DB exporter와 원천 데이터 조건 확인 후 재배포 |

## 커스텀 노드

커스텀 노드는 각각의 원 저장소 라이선스를 따릅니다. 이 저장소는 소스 코드를 vendoring하지 않고 commit만 고정합니다.

- `ltdrdata/ComfyUI-Impact-Pack`
- `ltdrdata/ComfyUI-Impact-Subpack`
- `1038lab/ComfyUI-RMBG`

## 배포 원칙

- 모델, taxonomy DB, 생성 결과를 이 Git 저장소에 commit하지 않습니다.
- manifest의 URL, 크기, SHA-256은 재현과 무결성 검증용이며 재배포 허가를 뜻하지 않습니다.
- 상업 프로젝트에 사용하기 전 모델별 약관과 매출/조직 규모 조건을 다시 확인합니다.
- 라이선스를 확인할 수 없는 구성요소는 교체하거나 로컬 평가 전용으로 분리합니다.
