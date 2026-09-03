## 문서 규격(v2)

- workflow_id: `scene_event_cg`
- modality: `image`
- input_requirement: 없음(no-reference txt2img)
- output: 1024x576 16:9 event CG PNG
- prompt_policy: `danbooru_sqlite+readme_wrapper`
- editable_fields: `100.inputs.lora_name`, `100.inputs.strength_model`, `100.inputs.strength_clip`, `9.inputs.text`, `10.inputs.text`, `11.inputs.width`, `11.inputs.height`, `12.inputs.seed`, `12.inputs.steps`, `12.inputs.cfg`, `12.inputs.denoise`, `14.inputs.filename_prefix`

운영 원칙:

- canonical JSON을 직접 덮어쓰지 않고 runtime copy를 patch합니다.
- candidate != approved != production-ready입니다.
- 얼굴·손·소품·Ren'Py safe-area를 각각 통과하기 전에는 승인하지 않습니다.
- static CI는 prompt/metadata 계약만 검사합니다. 렌더된 이미지의 얼굴·손·소품 품질이나 safe-area 적합성은 static CI로 확립할 수 없으며, 아래 visual QA가 반드시 필요합니다.

### 1. 용도와 기본 경로

이 워크플로우는 Nova Anime XL IL v19와 pose LoRA로 16:9 이벤트 CG를 만듭니다.

- checkpoint: `novaAnimeXL_ilV190.safetensors`
- pose LoRA: `hinaMaybeBetterPoseXL_v5-NoobAI.safetensors`
- LoRA strength: model/CLIP `0.65 / 0.65`
- sampler: `euler_ancestral`, normal, 30 steps, CFG 5.2
- reference/PuLID: 없음
- 기본 해상도: 1024x576
- Ren'Py 검토 해상도: 1920x1080(1.875배)
- 하단 대사창: 화면 높이의 28%

no-reference 경로이므로 캐릭터 identity와 의상은 prompt anchor로만 유도됩니다. 정확한 동일 캐릭터나 소품 형상을 보장하지 않습니다.

### 2. 얼굴 거리 제한과 기본 구도

Nova Anime XL은 16:9 장면에서 인물이 멀어질수록 눈·입·코의 픽셀 수가 줄어 얼굴이 뭉개질 수 있습니다. 얼굴이 중요한 이벤트 beat에서는 다음을 기본으로 합니다.

```text
upper_body, straight-on, facing_viewer, looking_at_viewer
```

기본 negative에는 다음 구도를 둡니다.

```text
full_body, wide_shot, cowboy_shot, profile
```

`cowboy_shot`은 canonical 추천 preset이 아니라 runtime-only cinematic 실험입니다. 실험할 때는 canonical JSON이 아닌 runtime copy에서 `cowboy_shot`을 negative prompt에서 제거하고 같은 seed로 `upper_body`와 A/B합니다. 렌더 visual QA를 통과한 후보만 채택합니다. establishing shot은 `scene_background`가 담당합니다.

### 3. 검증된 기본 샘플: 데이터 코어 발견

canonical positive:

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, scenery, 1girl, solo, medium_hair, straight_hair, blunt_bangs, black_hair, aqua_eyes, school_uniform, white_shirt, necktie, blue_jacket, pleated_skirt, upper_body, straight-on, facing_viewer, looking_at_viewer, surprised, open_mouth, holding_crystal, holding_gem, own_hands_together, hands_up, arms_up, crystal, gem, glowing, classroom, indoors, night, depth_of_field
```

canonical negative:

```text
modern, recent, old, oldest, cartoon, graphic, text, logo, sign, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, out_of_frame, very_displeasing, (worst_quality, bad_quality:1.2), sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, full_body, wide_shot, cowboy_shot, profile, multiple_girls, crowd, reaching, outstretched_arm, outstretched_arms
```

기본 seed `9064003`은 얼굴·양손·크리스털을 대사창 위에서 식별할 수 있었던 검증 후보입니다. seed를 고정했다고 다른 identity/background prompt에서도 같은 품질이 보장되지는 않습니다.

### 4. Ren'Py action-safe 구도 계약

1920x1080 Ren'Py 화면의 하단 대사창 비율은 `0.28`입니다. 따라서 action-safe 상단 경계는 숫자 `1 - 0.28 = 0.72`이며, 얼굴, 손, 스토리 소품처럼 장면 이해에 필요한 요소는 원본 프레임의 상단 `0.72` 안에서 식별 가능해야 합니다.

검토 명령:

```bash
python scripts/make_renpy_background_preview.py \
  /path/to/event_cg.png \
  /path/to/event_cg_renpy_preview.png \
  --display-width 1920 \
  --display-height 1080 \
  --textbox-fraction 0.28
```

`reaching`으로 책상 위 물체에 손을 내미는 구도는 얼굴은 선명해도 손과 소품이 대사창 아래로 내려갈 수 있습니다. 얼굴과 소품이 모두 중요한 reveal에서는 아래처럼 물체를 가슴 높이로 올리는 단일 동작 묶음을 우선합니다.

```text
upper_body, holding_crystal, holding_gem, own_hands_together, hands_up, arms_up
```

`reaching`, `outstretched_arm`, `outstretched_arms`와 `holding_*`를 한 후보에 섞지 않습니다.

`cowboy_shot`, `reaching`, `outstretched_arm`, `outstretched_arms` block은 추천 preset이 아니라 명시적인 runtime-only 실험으로만 보존합니다. 선택한 실험 tag는 canonical negative와 동시에 사용할 수 없으므로 runtime copy의 negative prompt에서 같은 tag를 제거해야 합니다. canonical JSON은 변경하지 않으며, 실험 결과는 rendered visual QA 전까지 승인 후보가 아닙니다.

### 5. 동일 seed A/B 절차

프롬프트나 구도 효과를 비교할 때 seed까지 바꾸면 원인을 구분할 수 없습니다.

1. 서로 다른 seed 값 최소 3개를 고르고, 각 값을 A와 B에서 변경 없이 그대로 재사용합니다.
2. identity/outfit/scene/sampler 설정을 고정합니다.
3. A와 B에서 구도 또는 동작 block 하나만 바꿉니다.
4. 3개 seed 각각의 A/B 쌍, 즉 총 3쌍/6개 렌더를 contact sheet로 나란히 비교합니다.
5. 선택 후보는 Ren'Py 1920x1080 + 하단 28% 대사창 preview로 다시 검사합니다.

로컬 검증에서는 같은 3개 seed의 `cowboy_shot`과 `upper_body`를 비교했을 때 `upper_body`가 얼굴 크기와 눈·입 선명도를 더 안정적으로 확보했습니다. 하지만 `holding_crystal` 후보도 3개 중 하나는 소품이 선명했고, 하나는 넥타이와 융합됐으며, 하나는 소품이 사라졌습니다. 따라서 단일 seed 성공을 일반화하지 말고 최소 3개 후보를 유지합니다.

### 6. QA 합격 조건

아래 항목은 렌더된 preview를 직접 보는 visual QA 계약입니다. static CI가 tag, seed, 수치 metadata의 일관성을 확인해도 이 합격 여부나 이미지 품질을 확립할 수 없습니다.

얼굴:

- 1920x1080 preview에서 양쪽 눈동자, 입선, 코와 얼굴 윤곽이 구분됩니다.
- 배경 속 소형 인물처럼 보이지 않습니다.
- 양쪽 눈이 심하게 비대칭이거나 눈·입이 뭉개지지 않습니다.

손과 소품:

- 손가락 수, 관절, 양손 결합이 납득 가능합니다.
- 소품이 넥타이·의상·손가락과 융합되지 않습니다.
- 스토리 소품의 실루엣과 발광 중심을 대사창 위에서 식별할 수 있습니다.
- 손이나 소품이 없으면 얼굴 PASS와 관계없이 장면 전체는 FAIL입니다.

배경과 의상:

- scene/time tag와 배경이 일치합니다.
- 가짜 문자, 로고, 표지판이 없습니다.
- identity/outfit anchor의 머리색·눈색·핵심 의상색을 확인합니다.
- no-reference 경로의 경미한 의상 세부 drift는 허용하지만 다른 캐릭터로 보이는 drift는 거부합니다.

Ren'Py:

- 얼굴과 핵심 행동이 상단 `0.72`에서 이해됩니다.
- 대사창을 표시해도 손·소품·표정 중 장면 이해에 필요한 요소가 모두 사라지지 않습니다.
- 대사창을 숨겼을 때도 16:9 이벤트 CG로 완결됩니다.

### 7. 한계와 우회 경로

- 정확한 캐릭터 일치가 필수라면 no-ref canonical만으로 해결하지 말고 승인된 캐릭터 reference/IP-Adapter/PuLID 또는 얼굴 inpaint를 별도 실험합니다.
- 손-소품 상호작용은 pose LoRA를 써도 seed에 따라 실패합니다.
- 소품 형태 고정이 더 중요하면 `scene_prop_cg`로 별도 cut-in을 만들고 Ren'Py에서 연출합니다.
- 배경의 구조적 일관성이 더 중요하면 `scene_background` 결과 위에 투명 캐릭터를 합성하는 경로를 사용합니다.
- 가짜 UI와 문자는 이미지 생성에 맡기지 않고 Ren'Py 기본 GUI 또는 screen overlay로 분리합니다.
- 얼굴 보정은 원거리 구도를 정당화하는 기본 해법이 아닙니다. 먼저 인물 점유율을 확보하고, 보정은 별도 QA된 후처리로만 추가합니다.
