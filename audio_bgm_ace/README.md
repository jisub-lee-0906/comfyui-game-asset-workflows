## 문서 규격(v1)

- workflow_id: `audio_bgm_ace`
- modality: `audio`
- input_requirement: 없음
- output: mp3 candidate (post OGG)
- prompt_policy: `audio_tags_natural_language`
- editable_fields: 2.inputs.tags, 2.inputs.lyrics, 2.inputs.seed, 2.inputs.bpm, 2.inputs.duration, 2.inputs.keyscale, 2.inputs.cfg_scale, 2.inputs.temperature, 4.inputs.seconds, 6.inputs.seed, 6.inputs.steps, 6.inputs.cfg, 8.inputs.filename_prefix, 8.inputs.quality

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🎵 0. VN BGM 생성 워크플로우 — ACE-Step 1.5

#### 1. 목적

`audio_bgm_ace`은 visual novel / dating-sim 장면에 사용할 instrumental BGM 후보를 생성하는 workflow입니다.

이 workflow는 현재 Windows ComfyUI stack의 core ACE-Step 1.5 audio route를 사용합니다.

- 로컬 checkpoint: `ace_step_1.5_turbo_aio.safetensors`
- 주요 node: `TextEncodeAceStepAudio1.5`, `EmptyAceStep1.5LatentAudio`, `ModelSamplingAuraFlow`, `KSampler`, `VAEDecodeAudio`, `SaveAudioMP3`
- 출력: MP3 후보. Ren'Py promote 전에는 OGG 변환과 listening QA가 필요합니다.

#### 2. Prompt 작성법

ACE-Step BGM prompt는 Danbooru image tag가 아니라 audio tag / natural-language music direction입니다. 이미지 workflow의 `danbooru_tag.csv` 규칙을 그대로 적용하지 않습니다.

**Tags 기본형:**

```text
instrumental only, no vocals, no singing, no lyrics, loopable visual novel background music, {장면 분위기}, {악기 구성}, {감정/텐션}, dialogue-friendly, seamless loop
```

**Lyrics:**

```text

```

`lyrics`는 빈 문자열로 둡니다. 단, 이것만으로 vocal이 절대 나오지 않는다는 보장은 없으므로 listening QA가 필요합니다.

#### 3. 장면별 prompt 예시

**1) 학원/신비/도입 BGM**

```text
instrumental only, no vocals, no singing, no lyrics, loopable visual novel background music, warm after-school fantasy academy, gentle piano, soft strings, light celesta, calm wonder, subtle romantic tension, dialogue-friendly, seamless loop
```

추천값:

- duration: smoke 30초, 후보 60~90초
- bpm: 80~95
- keyscale: `C major`, `G major`, `A minor` 중 장면에 맞게 선택

**2) 가벼운 패닉 / 마법 사고**

```text
instrumental only, no vocals, no singing, no lyrics, loopable visual novel background music, light panic, unstable magic accident, pizzicato strings, soft percussion, ticking rhythm, playful tension, not horror, dialogue-friendly, seamless loop
```

추천값:

- duration: 30~45초
- bpm: 110~130
- keyscale: `A minor` 또는 `D minor`

**3) 리아 작업실 조사**

```text
instrumental only, no vocals, no singing, no lyrics, loopable visual novel background music, curious magical investigation, quiet workshop, glass chimes, celesta, muted piano, soft synth pad, intelligent and mysterious, dialogue-friendly, seamless loop
```

추천값:

- duration: 45~75초
- bpm: 85~105
- keyscale: `C minor`, `A minor`, `E minor`

#### 4. Runtime patch 대상

`WORKFLOW_INDEX.json`의 editable field를 기준으로 runtime에서만 patch합니다.

자주 바꾸는 값:

- `2.inputs.tags`
- `2.inputs.lyrics`
- `2.inputs.seed`
- `2.inputs.bpm`
- `2.inputs.duration`
- `2.inputs.keyscale`
- `4.inputs.seconds`
- `6.inputs.seed`
- `6.inputs.steps`
- `8.inputs.filename_prefix`

`2.inputs.duration`과 `4.inputs.seconds`는 같은 길이로 맞춥니다.

#### 5. QA / promote 규칙

BGM 생성 성공은 production pass가 아닙니다.

확인해야 할 것:

- `ffprobe`로 duration/audio stream 확인
- vocal/lyrics가 섞이지 않았는지 listening QA
- 대사와 충돌하지 않는 볼륨/밀도인지 확인
- loop로 썼을 때 끊김이 심하지 않은지 확인
- Ren'Py에서 `play music ... loop` smoke

Ren'Py promote 전 권장 편집:

ACE-Step 출력은 duration이 맞아도 앞/뒤 또는 중간 이후에 무음 tail이 생길 수 있습니다. 게임에 넣을 때는 원본 MP3를 그대로 쓰지 말고, 소리 안 나는 앞/뒤 tail을 최대한 자른 뒤 마지막에 짧은 fade-out을 걸고 OGG로 변환합니다. 루프 이음새는 2회 반복 preview를 들어보고 QA합니다.

기본 후처리 스크립트:

```bash
python E:/workspace/comfyui-game-asset-workflows/scripts/final_edit_ace_bgm_loop.py \
  C:/Users/Desktop/Documents/ComfyUI/output/<run>/audio_bgm_ace/<source>.mp3 \
  --name <bgm_id>_loop_edit
```

출력:

```text
edited_loops/<bgm_id>_loop_edit.flac
edited_loops/<bgm_id>_loop_edit.ogg
edited_loops/<bgm_id>_loop_edit_loop_preview_2x.ogg
```

보고 단위:

```text
원본 MP3, 감지된 무음 구간, 선택/trim 구간, fade-in/out, 최종 FLAC, Ren'Py OGG, 2회 loop preview, ffprobe/silencedetect, 청감 QA 필요 여부
```

단, fade-out 방식은 “부드럽게 다시 시작되는 후보”를 만드는 편집입니다. 완전 seamless loop는 음악 구조/박자/마디가 맞아야 하므로 loop preview 청감 QA 후 필요하면 수동 loop point/crossfade 편집을 추가합니다.

#### 6. 출력 위치

`SaveAudioMP3.inputs.filename_prefix`는 Windows ComfyUI output root 기준 상대 경로입니다.

예:

```text
hermes_vn_bgm_template/academic_wonder
```

출력은 active output root 아래 `<unique_run_folder>/...`에 생성됩니다. Agent는 생성 후 `/history/{prompt_id}` 또는 output scan으로 정확한 파일 경로를 확인해야 합니다.
