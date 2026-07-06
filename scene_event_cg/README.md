## 문서 규격(v1)

- workflow_id: `scene_event_cg`
- modality: `image`
- input_requirement: 없음 (no-ref)
- output: event CG PNG; legacy default 16:9, mobile/portrait production tests may override resolution explicitly
- prompt_policy: `danbooru_sqlite+readme_wrapper`
- editable_fields: 100.inputs.lora_name, 100.inputs.strength_model, 100.inputs.strength_clip, 9.inputs.text, 10.inputs.text, 11.inputs.width, 11.inputs.height, 12.inputs.seed, 12.inputs.steps, 12.inputs.cfg, 12.inputs.denoise, 14.inputs.filename_prefix

운영 원칙:
- README를 실행 계약으로 사용합니다.
- canonical workflow JSON은 직접 덮어쓰지 않고 runtime/in-memory patch를 우선합니다.
- candidate != approved != production-ready.

### 🖼️ 0. 이벤트 CG 제작 워크플로우

이 워크플로우는 이미지 reference 없이 Nova Anime XL IL v19 텍스트 프롬프트만으로 이벤트 CG를 생성합니다. canonical JSON은 no-ref + pose LoRA on을 기본으로 하며, 기본 해상도는 legacy 16:9입니다. 모바일/세로형 전환 검증에서는 runner의 명시적 `--width/--height` override로 portrait 후보를 생성합니다.

핵심 운영 원칙:

- 이미지 reference / PuLID 없음.
- checkpoint: `novaAnimeXL_ilV190.safetensors`.
- pose LoRA: `hinaMaybeBetterPoseXL_v5-NoobAI.safetensors`, strength `0.65 / 0.65`.
- 출력 비율은 기본 legacy route에서 16:9(1024x576)를 사용합니다. 다만 모바일/세로형 VN 전환 검증 또는 세로형 production route에서는 명시적으로 portrait 해상도(예: 832x1472)를 사용합니다.
- 캐릭터 일관성은 이미지 참조가 아니라 고정 identity/outfit block으로 유지합니다.
- 프롬프트는 `char_base no-composition 테스트 방식`을 event_cg에 이식한 계약을 사용합니다.
- README는 실행 가이드입니다. 과거 출력 경로, prompt_id, contact sheet 같은 기록은 README가 아니라 skill reference / `.analysis/` / `WORKFLOW_INDEX.json`에 둡니다.

#### 1. 기본 canonical prompt

아래 prompt는 바로 실행 가능한 기본 샘플입니다. char_base no-composition 테스트 방식 그대로, 구도/카메라 강제 태그를 기본 positive에서 제거하고 identity/outfit block 중심으로 운용합니다. event_cg 특성상 장면 태그는 최소한으로만 추가합니다. 출력 비율은 runner 인자로 고정 기록되며, legacy 기본은 16:9이고 모바일 route는 portrait로 override합니다.

**Positive prompt:**

```text
masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest, {캐릭터/subject 특징(1girl/1boy/solo/male_focus 등 포함)}, {의상 디테일(의상 이름, 색상_의상종류)}, auditorium, indoors, spotlight, depth_of_field
```

**Negative prompt:**

```text
modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, very_displeasing, (worst_quality, bad_quality:1.2), sketch, jpeg_artifacts, signature, watermark, username, conjoined, bad_ai-generated, classroom, chalkboard, blackboard, whiteboard
```

#### 2. Prompt 조립 순서

기존 캐릭터 기반 event CG를 만들 때는 README 샘플을 그대로 복붙하지 말고, 먼저 프로젝트의 캐릭터 metadata sidecar를 읽습니다.

현재 Windows workspace 예시:

```text
E:/workspace/renpy-project/<game_slug>/docs/assets/characters/<character_id>.asset.json
```

조립 순서:

1. creator/model wrapper를 유지합니다.
2. 캐릭터 특징 block을 `{연령대, 헤어스타일, 눈매, 머리색, 눈색}`으로 고정합니다.
3. 의상 block을 `{의상 이름, 색상_의상종류}` SQLite 태그 묶음으로 고정합니다.
4. 구도/카메라 강제 태그(`upper_body`, `cowboy_shot`, `from_above`, `from_below`, `dutch_angle` 등)는 기본 positive에 넣지 않습니다.
5. scene/background/time tag는 최소한으로만 추가합니다.
6. 모든 variable tag는 로컬 Danbooru taxonomy SQLite에서 active/non-deprecated tag 또는 alias로 존재하는지 검증합니다.
7. README에 문서화된 wrapper/운영 태그와 DB 검증을 통과한 태그만 사용합니다.
8. DB에 없는 자연어 chunk, pseudo-tag, 오래된 helper script 출력은 사용하지 않습니다.

Metadata 원본 특징 guard:

- PNG metadata의 오래된 prompt나 이전 실험 prompt가 현재 캐릭터 metadata보다 우선하지 않습니다.
- 다른 캐릭터를 만들 때는 이 README의 Lia 예시 anchor를 그대로 쓰지 말고, 해당 캐릭터 metadata anchor로 교체합니다.
- 원본/승인 캐릭터의 `identity_anchor`와 선택한 outfit block을 임의로 바꾸지 않습니다. 머리 길이/스타일/색, 눈색, 핵심 의상색/소품이 바뀌면 event CG가 아니라 다른 캐릭터처럼 drift합니다.
- scene/background/time/small staging tag는 identity/outfit block 뒤에 소량 추가하고, identity/outfit과 충돌하는 태그를 넣지 않습니다.
- 의상 드리프트를 줄이겠다고 DB에 없는 자연어/pseudo-tag를 넣지 않습니다.

#### 3. 기본 안전 tag 세트

Unit 10C automation audit note: the fixed README/model wrapper keeps `depth_of_field` as a positive quality/composition cue, so `depth_of_field` has been removed from the canonical workflow negative prompt. The canonical negative still intentionally contains several composition/camera/body-pose tags (`cowboy_shot`, `upper_body`, `full_body`, `standing`, `sitting`, `facing_viewer`, `looking_at_viewer`, `from_above`, `from_below`, `dutch_angle`) to prevent placeholder-driven pose/camera drift. The toolkit runner fails closed if any agent-authored positive placeholder tag, or any fixed positive wrapper token, also appears in the canonical negative prompt. Do not put those negative-reserved tags into `prompt_slots.scene_context`; use non-conflicting setting/mood tags such as `indoors`, `auditorium`, `spotlight`, `stage`, etc.

Legacy/historical candidate sets below contain several now negative-reserved tags. Treat them as examples of *unsafe old presets* unless the canonical negative policy is deliberately changed:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer, standing, arms_at_sides
```

설명/멈칫/제지 beat:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer, standing, open_hands, reaching, serious, open_mouth, motion_lines
```

발표/지목/명령 beat:

```text
upper_body, straight-on, facing_viewer, looking_at_viewer, standing, pointing_at_viewer, outstretched_arm, serious, open_mouth, motion_lines
```

충격/reveal beat의 close cinematic 기본값:

```text
upper_body, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
```

운영 규칙:

- 한 번에 주 동작 태그를 여러 개 섞지 않습니다. `reaching`, `pointing_*`, `outstretched_arms`, `dutch_angle/motion` 중 하나를 중심으로 둡니다.
- 손동작 프리셋은 seed A/B 후보를 여러 장 뽑고, 손가락/소매/팔 길이 QA를 통과한 것만 asset candidate로 둡니다.
- `pointing_forward`는 양팔 대칭 지시가 나올 수 있으므로 지목/명령 연출은 `pointing_at_viewer`를 우선합니다.
- 기본/중립 event CG는 얼굴 품질과 캐릭터 동일성을 위해 `upper_body` 중심으로 둡니다.

#### 4. Cinematic pose/camera policy status

Unit 10F decision: do **not** use the old cinematic pose/camera tag presets as current `prompt_slots.scene_context` recipes. The canonical negative prompt currently reserves pose/camera/body-framing tags such as:

```text
cowboy_shot, upper_body, full_body, standing, sitting, facing_viewer, looking_at_viewer, from_above, from_below, dutch_angle
```

The toolkit runner intentionally fails closed if these tags are reintroduced through agent-authored positive placeholders. This keeps the automation route stable and prevents hidden prompt self-conflicts, but it also means old event-CG cinematic recipes are **disabled until a deliberate pose/camera policy redesign is performed**.

Historical disabled examples — do not paste into current `prompt_slots.scene_context` without redesigning the canonical negative policy first:

```text
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
cowboy_shot, from_below, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, outstretched_arms, open_hands, surprised, open_mouth, motion_lines
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, pointing_at_viewer, outstretched_arm, serious, open_mouth, motion_lines
cowboy_shot, from_below, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning_forward, open_hands, reaching, serious, open_mouth, motion_lines
cowboy_shot, from_above, dutch_angle, facing_viewer, looking_at_viewer, standing, leaning, surprised, open_mouth, motion_blur, motion_lines
```

Current safe event-CG `scene_context` should be limited to non-conflicting setting/mood/time/lighting tags such as:

```text
indoors, auditorium, stage, curtains, spotlight, podium, presentation, night, sunset, window, sunlight
```

Unit 10I update: same-seed framing experiments showed that face proximity materially improves eye/face quality on the active local model. For production character event CGs, the best prompt-only direction so far is the H6 identity/outfit policy plus `upper_body, looking_at_viewer`, with those exact tokens removed from the production-route negative prompt. `facing_viewer` is also viable for frontal VN event CGs. Unit 10J formalized this in `run_scene_event_cg_smoke.py` as route modes: `conservative`, `production_character`, `production_character_front`, and `cut_in`. The route mode can be passed as `--route-mode` or recorded in prompt slots as `scene_event_route_mode`. Do not apply this by silently changing the conservative fixture route; split policy modes instead:

1. conservative fixture/no-ref route: keep pose/camera tags mostly negative-reserved for broad smoke tests;
2. production character event route: use `scene_event_route_mode: production_character`, allow `upper_body` + `looking_at_viewer`, and carry full source outfit/accessory tags (`red_bow`, `brown_cardigan`, `white_shirt`, `blue_skirt`, `brown_pantyhose`). Unit 10K confirmed this route is robust enough as the default prompt-only production event route, but still requires small seed-batch QA; seed `260529217` was the best candidate in that batch. Unit 10L found a better neutral-scene micro policy: add `expressionless, closed_mouth` for neutral event CGs only;
3. production frontal route: use `scene_event_route_mode: production_character_front` only when a direct front-facing VN event CG is desired;
4. special cut-in route: use `scene_event_route_mode: cut_in` and reserve `portrait`/`close-up`/`headshot`/`solo_focus` for intentional face cut-ins, not default event CGs;
5. future reference route: add image/reference conditioning if prompt-only identity lock is still insufficient.

Unit 10M emotion/framing matrix expanded route policy:

- neutral default: `production_character` + `expressionless, closed_mouth` + `upper_body, looking_at_viewer`;
- happy default: `production_character_front` + `smile, open_mouth`;
- serious default: `production_character_front` + `serious, closed_mouth` (use `cut_in` for stronger intensity);
- surprised default: `production_character_front` + `surprised, open_mouth`;
- sad default: `production_character_front` + `sad, tears, frown, closed_mouth`;
- emotional close-up/cut-in: `cut_in` + `portrait, close-up, headshot, solo_focus`;
- medium/cowboy shot: `production_character_cowboy` + `cowboy_shot, looking_at_viewer`, optional only, not default.




#### Automation v2 tool flow

The VN toolkit now has v2 helper tools that turn Unit 10L/10M policy into repeatable production automation:

```bash
# 1) Create one resolved prompt-slot file from compact intent.
python tools/create_scene_event_cg_prompt_slots.py   --project-root <renpy-project>   --asset-id <asset-id>   --emotion sad   --framing default

# 2) Generate or prepare-check a seed batch.
python tools/run_scene_event_cg_batch.py   --project-root <renpy-project>   --asset-id-prefix <asset-prefix>   --emotion sad   --framing default   --seeds 260529217,260530001,260529203   --char-base-metadata <char_base metadata.json>

# 3) Build review sheets from the batch summary.
python tools/make_event_cg_contact_sheet.py   --batch-summary <..._scene_event_cg_batch.json>   --output <..._contact_sheet.jpg>
```

This is the recommended production path: batch first, contact-sheet review second, approval-gated promotion last. Do not auto-promote a single seed.


#### 5. 장소/장면 tag 운영

제3마법시연장/발표장 계열:

```text
auditorium, stage, curtains, spotlight, indoors, podium, presentation
```

사용하지 않을 기본 negative:

```text
classroom, chalkboard, blackboard, whiteboard
```

규칙:

- `classroom`을 magic demo hall proxy로 쓰지 않습니다.
- 정확한 장소 tag가 DB에 없으면 자연어로 억지 설명하지 말고, 배경 workflow / 별도 prop / Ren'Py staging / overlay로 해결합니다.
- text, sign, board가 나올 가능성이 있는 장소는 fake text QA를 필수로 합니다.

#### 6. 검증된 Danbooru SQLite tag 메모

출처: 로컬 Danbooru taxonomy SQLite tag oracle. 아래 tag는 README 작성 시점에 DB에서 active/non-deprecated 존재를 확인한 운영 후보입니다.

- 캐릭터/의상: `long_hair`, `wavy_hair`, `blunt_bangs`, `sidelocks`, `pink_hair`, `purple_eyes`, `school_uniform`, `white_shirt`, `red_bow`, `blue_jacket`, `gold_trim`, `capelet`
- 구도/대상: `upper_body`, `close-up`, `portrait`, `headshot`, `1girl`, `solo`, `cowboy_shot`, `wide_shot`, `full_body`
- 카메라/시선: `straight-on`, `facing_viewer`, `looking_at_viewer`, `dutch_angle`, `pov`, `from_above`, `from_below`
- 작은 연출: `sitting`, `standing`, `arms_at_sides`, `open_hands`, `reaching`, `outstretched_arm`, `outstretched_arms`, `pointing_forward`, `pointing_at_viewer`, `hand_on_own_chest`, `hand_on_own_hip`, `leaning`, `leaning_forward`
- 표정: `smile`, `sad`, `surprised`, `blush`, `tears`, `serious`, `closed_mouth`, `open_mouth`, `frown`
- 장소/조명: `auditorium`, `stage`, `curtains`, `spotlight`, `indoors`, `podium`, `presentation`, `bedroom`, `rooftop`, `street`, `park`, `library`, `sunset`, `night`, `window`, `sunlight`
- 초점/동세 보조: `depth_of_field`, `blurry_background`, `bokeh`, `motion_blur`, `motion_lines`

#### 7. 실행 / QA 규칙

1. 기본은 no-ref + pose LoRA on입니다.
2. 출력은 legacy 기본 16:9(1024x576)이나, 모바일/세로형 production에서는 runner 인자 `--width 832 --height 1472` 또는 fallback `--width 768 --height 1344` 같은 true 9:16 portrait override를 사용합니다. 비율 변경은 metadata에 기록되어야 합니다.
3. 이 canonical route에는 `LoadImage`/PuLID reference conditioning을 추가하지 않습니다. Unit 10G live smoke confirmed that this no-ref seed-only route can produce a mechanically valid 16:9 event CG, but it may not preserve production-grade identity/outfit details from the source char_base metadata (example drift: bow color/cardigan/face impression). Treat source metadata/seed handoff as provenance and weak continuity only, not as reference conditioning. Unit 10H prompt-only same-seed experiments showed that the current model responds much better when full source outfit/accessory tags are carried forward explicitly: put fragile identity tags early (`brown_eyes`, `tareme`, `blunt_bangs`), include exact outfit tags (`red_bow`, `brown_cardigan`, `white_shirt`, `blue_skirt`, `brown_pantyhose`), and keep scene context compact (`auditorium`, `spotlight`) before adding extra scenery.
4. 자연어 prompt chunk나 DB에 없는 pseudo-tag를 추가하지 않습니다.
5. 로컬 Danbooru taxonomy SQLite에서 active/non-deprecated로 검증되는 `tag` 또는 active alias만 variable prompt에 사용합니다.
6. 기본 positive는 identity/outfit 중심으로 유지하고, 구도/카메라 강제 태그는 기본값에서 제외합니다.
7. 의상 드리프트를 더 줄이겠다고 기본 prompt를 장황하게 늘리지 않습니다. 같은 anchor에서 seed 후보를 더 뽑고 QA로 고릅니다.
8. QA 전에는 생성 에셋을 production-ready/final이라고 부르지 않습니다.
9. 출력은 `/history/{prompt_id}` 또는 output scan으로 정확한 파일 경로를 검증한 뒤 보고합니다.
