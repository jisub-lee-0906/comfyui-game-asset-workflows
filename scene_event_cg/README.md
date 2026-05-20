### 🖼️ 0. 이벤트 CG 제작 워크플로우

이 워크플로우는 **이미지 reference 없이** Nova Anime XL IL v19 텍스트 프롬프트만으로 16:9 이벤트 CG를 생성합니다. 현재 canonical JSON은 **no-ref + pose LoRA 있음**을 기본 운영 기준으로 고정합니다.

핵심 방향:

- 이미지 reference / PuLID 없음
- `novaAnimeXL_ilV190.safetensors` 사용
- pose LoRA `hinaMaybeBetterPoseXL_v5-NoobAI.safetensors` 적용
- LoRA strength: `0.65 / 0.65`
- 캐릭터 일관성은 이미지 참조가 아니라 고정 캐릭터/의상 태그로 유지
- 기본 거리/구도는 얼굴이 뭉개지지 않도록 `upper_body, straight-on, facing_viewer, looking_at_viewer`를 사용
- 의상 variation을 줄이기 위해 `white_serafuku` 중심의 의상 anchor를 사용
- 단, no-ref route의 특성상 작은 의상 드리프트는 허용하고, 기본 route를 다시 PuLID/source-image로 되돌리지 않습니다.

#### 1. 기본 canonical prompt

아래 prompt는 바로 실행 가능한 기본 샘플입니다. 다른 느낌을 뽑을 때도 캐릭터/의상 고정 태그와 기본 거리/정면 anchor는 유지하고, 표정/작은 연출/배경/시간대/seed만 작게 바꿉니다.

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, scenery, 1girl, solo, medium_hair, straight_hair, brown_hair, green_eyes, school_uniform, white_serafuku, sailor_collar, blue_ribbon, pleated_skirt, upper_body, straight-on, facing_viewer, looking_at_viewer, standing, arms_at_sides, classroom, window, sunset, sunlight, BREAK, depth of field, volumetric lighting
```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, (worst_quality, bad_quality:1.2), sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated
```

#### 2. 고정 anchor

기본 캐릭터 anchor:

```text
medium_hair, straight_hair, brown_hair, green_eyes
```

기본 의상 anchor:

```text
school_uniform, white_serafuku, sailor_collar, blue_ribbon, pleated_skirt
```

기본 거리/정면 anchor:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer
```

이 세 anchor는 no-ref 기준에서 동일성과 얼굴 안정성의 핵심이므로 런마다 함부로 줄이거나 바꾸지 않습니다. 의상은 완전 고정이 아니라 `white_serafuku` 계열로 묶는 기준이며, 작은 색/레이어 variation은 후보 QA에서 감수합니다.

#### 3. 수정 가능한 영역

주로 바꿀 영역:

- 작은 연출: `standing`, `sitting`, `arms_at_sides`, `open_hands`, `hand_on_own_chest`, `leaning_forward`
- 표정/감정: `smile`, `sad`, `surprised`, `blush`, `tears`, `serious`
- 장소/시간대/조명: `classroom`, `bedroom`, `rooftop`, `street`, `park`, `library`, `sunset`, `night`, `window`, `sunlight`
- 감정 클로즈업 전용: `close-up, straight-on, facing_viewer, looking_at_viewer`
- 슬픔/약한 느낌: `upper_body, from_above, looking_at_viewer`
- 위압/권위/극적 reveal: `upper_body, from_below, looking_at_viewer`
- 대화/몸짓을 더 보여줄 때만: `cowboy_shot, straight-on, facing_viewer, looking_at_viewer`
- 배경 흐림/초점 보조: `blurry_background`, `bokeh`

#### 4. 기존 캐릭터 기반 metadata-first 규칙

이 README의 기본 prompt는 Lia `white_serafuku` 예시입니다. 기존 캐릭터 기반 event CG를 생성할 때는 README 샘플을 손으로 복붙하지 말고, 먼저 프로젝트의 캐릭터 metadata sidecar를 읽습니다.

현재 프로젝트 예시:

```text
/home/jisub-lee/workspace/vn-demo/the_accidental_architect_of_magic/docs/assets/characters/lia_bel_astrin.asset.json
```

조립 순서:

1. `identity_anchor.positive`를 읽어 캐릭터 동일성 block으로 고정합니다.
2. 사용할 의상 `outfits.<outfit_id>.positive`를 읽어 outfit block으로 고정합니다.
3. `framing_defaults.scene_event_cg`를 읽어 기본 거리/정면 block으로 고정합니다.
4. 필요한 경우 `expression_map.<expression_id>.prompt_tags`만 추가합니다.
5. scene/background/time/small staging tag를 마지막에 소량 추가합니다.
6. 모든 variable tag를 루트 `danbooru_tag.csv`로 검증합니다.

prompt builder 예시:

```bash
python /home/jisub-lee/workspace/comfyui-game-asset-workflows/scripts/build_character_prompt.py \
  --character /home/jisub-lee/workspace/vn-demo/the_accidental_architect_of_magic/docs/assets/characters/lia_bel_astrin.asset.json \
  --workflow scene_event_cg \
  --outfit white_serafuku \
  --expression serious \
  --scene-tags classroom window sunset sunlight
```

주의:

- PNG metadata의 오래된 prompt나 이전 실험 prompt가 현재 캐릭터 metadata보다 우선하지 않습니다.
- 다른 캐릭터를 만들 때는 이 README의 Lia anchor를 그대로 쓰지 말고, 해당 캐릭터의 metadata anchor로 교체합니다.
- 의상 드리프트를 줄이겠다고 CSV에 없는 자연어/pseudo-tag를 넣지 않습니다.

#### 5. 운영 규칙

1. 기본은 no-ref + pose LoRA on입니다.
2. source image / PuLID는 이 canonical route에 넣지 않습니다.
3. 자연어 prompt chunk나 CSV에 없는 pseudo-tag를 추가하지 않습니다.
4. `danbooru_tag.csv`에 있는 `tag` 또는 `aliases`만 variable prompt에 사용합니다.
5. 얼굴 안정이 필요하면 `upper_body`를 기본으로 유지하고, `cowboy_shot`/`wide_shot`/`full_body`를 기본값으로 쓰지 않습니다.
6. `close-up`은 감정 컷 전용이며 기본값으로 남발하지 않습니다.
7. `from_below`는 ordinary dialogue보다 위압감/권위/극적 reveal에만 사용합니다.
8. 기본 negative에는 `close-up`을 넣지 않습니다. 너무 확대되는 개별 런타임에서만 추가합니다.
9. 의상 드리프트를 더 줄이겠다고 기본 prompt를 장황하게 늘리거나 pseudo-tag를 넣지 않습니다. 필요하면 동일 anchor에서 seed 후보를 더 뽑고 QA로 고릅니다.
10. QA 전에는 생성 에셋을 production-ready/final이라고 부르지 않습니다.

#### 6. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다.

- 캐릭터/의상: `medium_hair`, `straight_hair`, `brown_hair`, `green_eyes`, `school_uniform`, `white_serafuku`, `serafuku`, `sailor_collar`, `blue_ribbon`, `pleated_skirt`, `white_shirt`, `blue_sailor_collar`, `blue_neckerchief`, `blue_skirt`
- 구도/대상: `upper_body`, `cowboy_shot`, `close-up`, `portrait`, `headshot`, `1girl`, `solo`
- 카메라/시선: `straight-on`, `facing_viewer`, `looking_at_viewer`, `from_above`, `from_below`, `dutch_angle`, `pov`
- 작은 연출: `sitting`, `standing`, `arms_at_sides`, `open_hands`, `leaning_forward`, `hand_on_own_chest`
- 표정: `smile`, `sad`, `surprised`, `blush`, `tears`, `serious`
- 장소/조명: `classroom`, `bedroom`, `rooftop`, `street`, `park`, `library`, `sunset`, `night`, `window`, `sunlight`
- 초점 보조: `depth_of_field`, `blurry_background`, `bokeh`

Event CG 규칙: no-ref 기준에서는 캐릭터/의상 태그가 identity anchor입니다. 얼굴이 멀어져 뭉개지는 문제를 줄이기 위해 기본 구도는 `upper_body`로 유지합니다. 큰 액션 태그나 과한 광학 연출을 시도하기 전에 카메라, 배경, 조명, 작은 손/몸 연출을 우선 사용합니다. 이 route는 사용자 QA 기준으로 작은 의상 variation을 감수하고 진행하는 최종 운영 기준입니다.
