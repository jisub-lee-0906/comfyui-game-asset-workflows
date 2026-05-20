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

Ren'Py promote 전 권장 변환:

```bash
ffmpeg -y -i input.mp3 -c:a libvorbis -q:a 4 output.ogg
```

#### 6. 출력 위치

`SaveAudioMP3.inputs.filename_prefix`는 Windows ComfyUI output root 기준 상대 경로입니다.

예:

```text
hermes_vn_bgm_template/academic_wonder
```

출력은 보통 다음 아래에 생성됩니다.

```text
/mnt/c/Users/Desktop/Documents/ComfyUI/output/hermes_vn_bgm_template/
```

Agent는 생성 후 `/history/{prompt_id}` 또는 output scan으로 정확한 파일 경로를 확인해야 합니다.
