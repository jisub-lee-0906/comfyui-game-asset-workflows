# audio_sfx_mmaudio

MMAudio video-to-audio 기반 VN/게임 SFX 후보 생성 workflow입니다.

현재 SFX 기본 route는 사용자가 청감상 가장 좋다고 선택한 MMAudio video baseline입니다.

- 기준 prompt_id: `e2941581-4bec-4065-878c-d259c034c538`
- 기준 출력: `/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_official/mmaudio_video_car_horn_8s_seed202_00001_.flac`
- 기준 입력 영상: `/mnt/c/Users/Desktop/Documents/ComfyUI/input/mmaudio_official_car_horn_8s_25fps_384.mp4`
- canonical API workflow: `audio_sfx_mmaudio/audio_sfx_mmaudio_workflow_api.json`

주의: 이 workflow는 후보 생성용입니다. `production-ready` 판정은 청감 QA, 노이즈/볼륨/컷 편집/fade/Ren'Py 재생 확인 후에만 합니다. MMAudio가 8초 안에 같은 효과를 여러 번 반복하거나 문 열림/닫힘처럼 두 동작을 모두 낼 수 있으므로, 실제 게임용 SFX는 청감상 가장 깨끗한 한 번의 hit/segment만 잘라내어 사용합니다.

운영 고정: ComfyUI graph는 8초 source take를 생성하고, 최종 게임용 파일은 외부 후처리 단계에서 자동 single-hit 편집본으로 만듭니다. 기본 후처리 스크립트는 `/home/jisub-lee/workspace/comfyui-game-asset-workflows/scripts/final_edit_mmaudio_sfx.py`이며, 원본 FLAC/WAV를 분석해 가장 강한 1회 이벤트를 잘라 `edited_single_hits/`에 FLAC+OGG로 저장합니다.

예:

```bash
python3 /home/jisub-lee/workspace/comfyui-game-asset-workflows/scripts/final_edit_mmaudio_sfx.py \
  /mnt/c/Users/Desktop/Documents/ComfyUI/output/<run>/audio_sfx_mmaudio/<source_take>.flac \
  --name <sfx_id>_final
```

보고 단위는 항상 `8초 원본 take + 선택 구간 + 최종편집 FLAC + Ren'Py용 OGG + ffprobe/silencedetect`입니다.

## 기본값

```json
{
  "model": "mmaudio_large_44k.safetensors",
  "base_precision": "fp16",
  "vae_model": "mmaudio_vae_44k_fp16.safetensors",
  "synchformer_model": "mmaudio_synchformer_fp16.safetensors",
  "clip_model": "apple_DFN5B-CLIP-ViT-H-14-384_fp16.safetensors",
  "mode": "44k",
  "feature_precision": "fp16",
  "duration": 8.0,
  "steps": 25,
  "cfg": 4.5,
  "seed": 202,
  "mask_away_clip": false,
  "force_offload": true,
  "video_custom_width": 384,
  "video_custom_height": 384,
  "format": "None"
}
```

운영 원칙:

1. 기본 비교에서는 `duration`, `steps`, `cfg`, `mode`, `precision`을 바꾸지 않습니다.
2. 먼저 `video`, `prompt`, `negative_prompt`, `filename_prefix`만 runtime copy에서 바꿉니다.
3. 품질 비교가 필요할 때만 `seed`를 바꿉니다.
4. canonical JSON을 직접 덮어쓰지 말고 runtime payload/copy를 만들어 제출합니다.
5. MMAudio 원본 README 기준 기본/학습 duration은 8초입니다. 큰 편차는 품질 저하 가능성이 있습니다.

## 입력 영상 규칙

MMAudio video-to-audio는 프롬프트만큼 영상 cue가 중요합니다.

권장:

- 길이: 8초
- FPS: 25fps 권장
- 해상도/구도: 384x384 중심 crop에서 원인 물체와 동작이 보여야 함
- 소리가 나는 순간을 시각적으로 알 수 있어야 함
- 고해상도 입력은 품질 향상보다 처리 시간만 늘릴 수 있음

좋은 cue:

- 경적: 차 정면, 헤드라이트 점멸, sound wave 표시, honk 타이밍 반복
- 문소리: 문이 실제로 열리고 닫히는 움직임
- 발소리: 발이 바닥에 닿는 순간
- 충돌음: 물체가 표면에 부딪히는 순간
- 비소리: 비 streak/droplet이 계속 보이고 장면 전체가 비 상황

나쁜 cue:

- 정적인 일러스트 1장
- 추상 패턴만 있는 영상
- 소리 원인이 화면 바깥에 있음
- 소리 원인과 다른 움직임
- 핵심 동작이 화면 가장자리/crop 밖에 있음

## Positive prompt 폼

```text
[a/an/the] [sound source] [action/event], [timing or repetition], synchronized with [visible cue], realistic [material/domain] foley, [acoustic space], no [major unwanted sound], no music, no speech
```

기준 성공 prompt:

```text
a car horn honking short loud beeps synchronized with the flashing headlights and sound wave marks, realistic automobile horn, no engine, no music, no speech
```

왜 좋은가:

- `car horn`과 `automobile horn`으로 소리 정체성을 고정합니다.
- `short loud beeps`로 길이와 형태를 제한합니다.
- `synchronized with ...`로 영상 cue와 연결합니다.
- `no engine, no music, no speech`로 흔한 오염을 차단합니다.

## Negative prompt 폼

```text
Low quality, music, melody, speech, voice, talking, singing, crowd, [scene-specific unwanted sounds], distorted, robotic, electronic
```

경적 기준 negative prompt:

```text
Low quality, music, melody, speech, voice, talking, singing, crowd, rain, wind, siren, police, ambulance, engine rumble, traffic noise, distorted, robotic, electronic
```

원칙:

- 공통 오염: `music, melody, speech, voice, talking, singing`
- 모델 질감 오염: `distorted, robotic, electronic`
- 장면별 오염: 목표 소리와 헷갈리는 사촌 소리를 명시적으로 제외

## 예시

운영 우선순위: 모든 SFX 요청은 먼저 현실에 존재하는 유사 소리로 변환합니다. 핵심은 “일상 소리만”이 아니라 “실제로 들을 수 있는 자연/물리 현상으로 대체”하는 것입니다. 마법/추상음 요청도 직접 `magic sparkle`처럼 만들지 말고, 소리의 물리적 유사물을 정합니다. 예: 전기 마법은 천둥, 번개, 전기 스파크, 전선 지직거림으로 치환하고, 화염 마법은 불이 붙는 화르륵 소리, 가스레인지 점화, 장작 타는 소리, 짧은 불꽃 whoosh로 치환합니다. 구조선/감지는 연필·분필 긁힘, 공간 진동은 창틀·문틀 떨림, 물/얼음 계열은 물방울·얼음 깨짐처럼 source가 분명한 현실 cue를 씁니다.

### 자동차 경적

```text
a car horn honking short loud beeps synchronized with the flashing headlights and sound wave marks, realistic automobile horn, no engine, no music, no speech
```

Negative:

```text
Low quality, music, melody, speech, voice, talking, singing, crowd, rain, wind, siren, police, ambulance, engine rumble, traffic noise, distorted, robotic, electronic
```

### 비오는 소리

```text
heavy rain falling on a window, continuous raindrops synchronized with visible rainfall, realistic rain ambience, wet pavement, no thunder, no music, no speech
```

Negative:

```text
Low quality, music, melody, rhythm, speech, voice, talking, singing, crowd, wind, distorted, robotic, electronic, footsteps, birds, traffic
```

### 문 삐걱임

```text
a wooden door slowly creaking open synchronized with the visible door movement, realistic dry foley, close microphone, quiet room, no music, no speech
```

Negative:

```text
Low quality, music, melody, speech, voice, talking, singing, crowd, wind, rain, footsteps, knocking, distorted, robotic, electronic
```

### 발소리

```text
slow footsteps on an old wooden floor synchronized with each visible footstep, realistic close foley, dry indoor room, no music, no speech
```

Negative:

```text
Low quality, music, melody, speech, voice, talking, singing, crowd, rain, wind, running, metal, distorted, robotic, electronic
```

### 마법 짧은 효과음

```text
a short magical sparkle burst synchronized with the glowing visual effect, bright crystalline chime, clean fantasy game sound effect, no music, no speech
```

Negative:

```text
Low quality, music, melody, singing, speech, voice, talking, explosion, thunder, crowd, distorted, noisy, robotic
```

## 제출 전 체크

- ComfyUI server가 살아 있음
- `ComfyUI-MMAudio` custom node가 설치되어 있음
- `ComfyUI/models/mmaudio` 모델 파일이 존재함
- 입력 영상이 active ComfyUI `input/` 폴더에 존재함
- API JSON에 unresolved placeholder가 없음
- `MMAudioFeatureUtilsLoader`에는 `mode: "44k"`, `precision: "fp16"`을 명시함

## QA 라벨

- `smoke`: 노드/모델/API가 파일을 냄
- `official-guided baseline`: 공식/원본 가이드에 맞춘 길이/설정으로 생성됨
- `candidate`: 사람이 듣고 장면에 쓸 가능성이 있음
- `production-ready`: 청감 QA, 편집, 볼륨, 노이즈, 페이드, 게임 내 재생 확인 통과

현재 기준 prompt_id `e2941581-4bec-4065-878c-d259c034c538`는 사용자가 가장 좋다고 선택한 `candidate baseline`입니다.
