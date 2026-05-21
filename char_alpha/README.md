### ✂️ 배경 투명화 / alpha 워크플로우

#### 1. 목적

이 workflow는 이미 QA된 캐릭터/source/outfit/expression 이미지를 transparent PNG/sprite cutout 후보로 변환합니다.

프롬프트를 사용하지 않습니다. 루트 `danbooru_tag.csv`는 upstream 이미지 생성 단계에서만 관련이 있고, alpha 생성 단계에서는 시각적으로 승인된 source image를 그대로 넣어야 합니다.

#### 2. Runtime patch 대상

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
