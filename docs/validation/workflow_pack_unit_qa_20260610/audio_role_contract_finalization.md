# Audio BGM/SFX Automation Finalization — 2026-06-11

## Decision

Keep a single canonical workflow engine:

```text
audio_bgm_with_sfx/audio_bgm_with_sfx_workflow_api.json
```

Do **not** duplicate this workflow JSON into separate `audio_bgm` and `audio_sfx` workflow folders. Instead, automation uses logical role contracts:

```text
asset_type=bgm -> audio_role=audio_bgm -> workflow_id=audio_bgm_with_sfx
asset_type=sfx -> audio_role=audio_sfx -> workflow_id=audio_bgm_with_sfx
```

## Added workflow-pack role contracts

```text
audio_bgm_with_sfx/roles/audio_bgm.md
audio_bgm_with_sfx/roles/audio_sfx.md
audio_bgm_with_sfx/roles/audio_role_contracts.json
```

## Role prompt contracts

### audio_sfx

```text
short positive-only natural-language cue + one/two material or timbre colors
```

Defaults:

```text
mode: One-shot
negative_prompt: blank
duration: 2.5s by default; use SFX mode and 3-8s when the scene requires longer foley/magic/ambience-like effects
```

### audio_bgm

```text
instrumentation + musical form/rhythm + mood + short role
```

Current owner-preferred anchor:

```text
Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.
```

Defaults:

```text
mode: Music
negative_prompt: blank
duration: 24s source candidate by default
```

## Toolkit changes

- `tools/run_audio_bgm_with_sfx_smoke.py`
  - added role contracts;
  - changed default BGM duration to 24s;
  - removed default long negative prompt fallback;
  - records `audio_role`, `prompt_shape`, `role_contract_path`, and `negative_prompt_strategy` in metadata;
  - validates declared `audio_role` in prompt slots when present.

- `tools/resolve_asset_requests.py`
  - resolved BGM/SFX requests now include recommended audio role contract fields.

- `tools/run_generation_queue.py`
  - preserves recommended audio role fields from resolved requests.

- `tools/init_vn_automation_project.py`
  - scaffolds `audio_role_contracts` into new project contracts.

- Active project contract updated:
  - `E:/workspace/renpy-project/sihanbu_villainess_badend/docs/automation/project_contract.json`

## Verification

```text
python -m pytest tests/test_level4_generation_orchestrator.py tests/test_resolve_asset_requests.py tests/test_fresh_game_lifecycle.py -q
9 passed in 2.75s

python -m pytest -q
123 passed in 39.04s
```

Prepare-only smoke verified:

```text
sfx -> audio_role=audio_sfx, mode=One-shot, duration=2.5, negative=''
bgm -> audio_role=audio_bgm, mode=Music, duration=24.0, negative=''
```

Resolver smoke verified:

```text
bgm_role_contract_resolve_smoke -> audio_bgm_with_sfx / audio_bgm / Music / 24.0
sfx_role_contract_resolve_smoke -> audio_bgm_with_sfx / audio_sfx / One-shot / 2.5
```

## Status

Audio SFX/BGM automation is now finalized as a supervised, role-contract-driven pipeline. Generation remains approval-gated: file QA and owner semantic audio QA are still required before promotion.
