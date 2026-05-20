### 🖼️ 0. 이벤트 CG 제작 워크플로우

이 워크플로우는 **캐릭터 reference 1장만 입력**하고, 배경/구도는 프롬프트로 새로 생성합니다. 현재 canonical JSON에는 자연스러운 작은 연출을 보조하기 위한 pose LoRA가 기본 적용되어 있습니다.

#### 1. 프롬프팅 방법

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, anime_style, visual_novel, game_cg, 1girl, solo, [원본 캐릭터 핵심 특징:  {헤어 길이}, {헤어 스타일}, {머리색}, {눈색}], {감정표현}, [원본 의상 디테일: {상의, 하의, 신발, 악세서리}], {카메라 구도}, {자연스러운 작은 연출}, {배경 테마 및 장소}, {시간대 및 조명}, depth_of_field

```

*(※ 원본 캐릭터/의상 유지를 우선합니다. 캐릭터가 화면에 가깝게 나오도록 `{카메라 구도}`에는 `upper_body`, `waist_up`, `medium_shot`, `close-up` 등을 넣으면 됩니다.)*

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), shadow, depth_of_field

```

#### 2. 이벤트 CG 프롬프트 작성 팁 및 활용 가이드

**1) 카메라 구도 (Camera Angle)**

* **위에서 내려다보기:** `from_above, high_angle` (약해 보이거나 올려다보는 귀여운 연출)
* **아래서 올려다보기:** `from_below, low_angle` (웅장하거나 위압감 있는 연출)
* **초근접/얼굴 중심:** `close-up, face_focus` (감정선이 극에 달했을 때)
* **등장인물 어깨너머:** `over_the_shoulder` (플레이어와 마주 보는 듯한 1인칭 시점 연출)

**2) 상황 및 자연스러운 작은 연출 (Staging & Pose)**

* **권장 예시:** `standing`, `sitting`, `hand_on_own_chest`, `looking_at_viewer`처럼 CSV에 있는 작은 연출 태그를 우선 사용합니다. 창가/책상/세부 연출은 `classroom`, `window`, `desk`, `chair` 등 검증 태그와 seed/settings로 유도합니다.
* **주의:** CSV에 없는 자연어식 포즈 문구나 큰 액션 지시는 넣지 않습니다. 큰 포즈 변화는 이벤트 CG 재해석이 커질 수 있으므로 필요할 때만 검증된 태그로 작게 테스트합니다.

**3) 배경 및 조명 연출 보강**

* **예시 (창가에서 햇빛을 받는 씬):** `{배경 테마 및 장소}` 자리에 `classroom, window`를 넣고, `{시간대 및 조명}` 자리에 `sunset, sunlight`처럼 CSV 검증 태그를 넣습니다. 더 복잡한 빛줄기/먼지/무드 연출은 seed/settings 또는 후보 선택으로 처리합니다.

#### 3. 검증된 Danbooru CSV 태그 메모

출처: 루트 `danbooru_tag.csv`. 아래 태그들은 README에 적기 전에 해당 CSV에 실제 존재하는지 확인했습니다. `pose_variations`가 제거되었으므로 특수 포즈/액션 일러스트는 이 workflow에서 처리하되, identity/outfit 보존이 중요할 때는 포즈 변화를 작게 유지합니다.

- 구도/대상: `upper_body`, `cowboy_shot`, `close-up`, `portrait`, `1girl`, `solo`
- 카메라: `from_above`, `from_below`, `dutch_angle`, `pov`
- 작은 연출: `sitting`, `standing`, `leaning_forward`, `hand_on_own_chest`, `looking_at_viewer`
- 표정: `smile`, `sad`, `surprised`, `blush`, `tears`, `serious`
- 장소/조명: `classroom`, `bedroom`, `rooftop`, `street`, `park`, `library`, `sunset`, `night`, `window`

Event CG 규칙: 큰 액션 태그는 의상/몸을 다시 그리게 만들 수 있습니다. 과한 동작을 시도하기 전에 카메라, 배경, 조명, 작은 손/몸 연출을 우선 사용합니다.

