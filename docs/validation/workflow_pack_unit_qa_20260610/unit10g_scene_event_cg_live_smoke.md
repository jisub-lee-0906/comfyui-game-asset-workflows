# Unit 10G scene_event_cg live smoke + identity/composition QA — 2026-06-11

## Purpose

Close the missing live-generation validation for `scene_event_cg` after Unit 10C/10F only covered prepare-only and prompt-policy behavior.

Scope:

```text
workflow: scene_event_cg
mode: live ComfyUI smoke
source: generic Unit 9A neutral schoolgirl char_base metadata
prompt: safe non-conflicting Unit 10G fixture
promotion: forbidden
```

## Prompt slots

Created:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10g_fixture_neutral_character_handoff_live.json
```

Safe placeholders:

```json
{
  "character_features": ["medium_hair", "straight_hair", "blunt_bangs", "brown_hair", "brown_eyes"],
  "outfit_detail": ["school_uniform", "white_shirt", "blue_skirt"],
  "scene_context": ["indoors", "auditorium", "spotlight"]
}
```

The first live attempt intentionally failed closed because an older safe prompt slot file had a mismatched `asset_id`:

```text
Prompt slots asset_id mismatch
```

This confirms the runner's prompt-slot binding guard works.

## Live run

Command:

```bash
python tools/run_scene_event_cg_smoke.py \
  --project-root E:/workspace/renpy-project/sihanbu_villainess_badend \
  --asset-id event_unit10g_fixture_neutral_character_handoff_live \
  --scene-id workflow_pack_unit10g \
  --description 'Automation audit fixture: scene_event_cg live smoke from neutral char_base metadata' \
  --char-base-metadata E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/char_base_char_unit9a_neutral_schoolgirl_base_smoke_20260611_190248/metadata.json \
  --prompt-slots E:/workspace/renpy-project/sihanbu_villainess_badend/docs/production/prompt_slots/event_unit10g_fixture_neutral_character_handoff_live.json
```

Observed:

```text
RUN_ID scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316
ENDPOINT http://127.0.0.1:8000
prompt_submit_status 200
PROMPT_ID efe8999c-7c7b-4dcc-aa45-2a4574425e97
OUTPUT_PATH C:\Users\Desktop\Documents\ComfyUI\output\hermes_vn_scene_event_cg_smoke\scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316_seed260529202_00001_.png exists= True
CANDIDATE_COPY E:\workspace\renpy-project\sihanbu_villainess_badend\docs\automation\generated_candidates\event_cg\scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316\candidate_01.png
GENERATION_OUTPUT_VERIFIED
```

Metadata:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generation_runs/scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316/metadata.json
```

Candidate:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316/candidate_01.png
```

Compare sheet:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/generated_candidates/event_cg/scene_event_cg_event_unit10g_fixture_neutral_character_handoff_live_20260611_232316/unit10g_event_cg_source_compare_sheet.jpg
```

QA report:

```text
E:/workspace/renpy-project/sihanbu_villainess_badend/docs/validation/workflow_pack_unit_qa_20260610/unit10g_scene_event_cg_live_smoke/unit10g_scene_event_cg_live_qa_partial_pass.json
```

## File QA

```text
mode: RGB
size: 1024 x 576
aspect: 16:9
output verified: true
```

Result:

```text
PASS
```

## Visual QA

Result:

```text
PARTIAL PASS
```

Automation route passed:

```text
- 16:9 event CG output generated
- single character present
- auditorium/spotlight/indoor context present
- no obvious text/watermark
- no major anatomy artifact at review scale
```

Identity/outfit handoff caveats:

```text
- source red bow changed to blue bow
- source brown cardigan disappeared; output uses short-sleeve white shirt
- face/eye impression differs from source
- same seed/source metadata handoff alone does not preserve production-grade identity/outfit
```

## Outcome

```text
PARTIAL PASS: scene_event_cg live route works mechanically, but current no-ref seed-only/source-metadata handoff is not sufficient for production-grade character identity/outfit preservation.
```

This is an important automation finding. Earlier prepare-only/policy checks were necessary but not enough to validate actual event-CG visual handoff.

## Recommended follow-up

If production event CG identity preservation is required, do not rely on seed-only metadata handoff. Create a separate redesign unit for one of these approaches:

```text
1. source-image/reference conditioning route for scene_event_cg;
2. explicit outfit/identity lock with stronger prompt slots and QA-driven seed batches;
3. separate event CG route using approved char_base image as conditioning input;
4. conservative no-ref route only for non-production fixture coverage, with clear caveat.
```

Until then, keep generated Unit 10G output as:

```text
not_promoted_pending_owner_approval
automation fixture only
```
