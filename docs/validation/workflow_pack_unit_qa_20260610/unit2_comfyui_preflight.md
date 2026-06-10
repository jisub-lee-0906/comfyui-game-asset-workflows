# Unit 2 — ComfyUI Endpoint / object_info / Model Preflight

## Scope

No generation was run. This unit only checks live ComfyUI API readiness and workflow dependency visibility.

## Endpoint discovery

- `http://127.0.0.1:8000`: OK
  - `/system_stats`: OK status=200 elapsed=0.006s count=2
  - `/queue`: OK status=200 elapsed=0.012s count=2
  - `/object_info`: OK status=200 elapsed=0.643s count=1938
- `http://127.0.0.1:8188`: NOT READY
  - `/system_stats`: FAIL URLError: <urlopen error [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다>
  - `/queue`: FAIL URLError: <urlopen error [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다>
  - `/object_info`: FAIL URLError: <urlopen error [WinError 10061] 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다>
- `http://127.0.0.1:8001`: OK
  - `/system_stats`: OK status=200 elapsed=0.007s count=2
  - `/queue`: OK status=200 elapsed=0.001s count=2
  - `/object_info`: OK status=200 elapsed=0.184s count=1938

Selected live endpoint: `http://127.0.0.1:8000`

## Summary

- object_info class count: **1938**
- required class count from workflows: **35**
- missing class entries: **0**
- model/input choice mismatches: **0**
- errors: **0**
- warnings: **0**

## Workflow class availability

| workflow_id | class count | missing classes | model choice checks | choice mismatches |
|---|---:|---:|---:|---:|
| `char_base` | 6 | 0 | 2 | 0 |
| `char_expression` | 17 | 0 | 5 | 0 |
| `char_alpha` | 3 | 0 | 1 | 0 |
| `scene_background` | 7 | 0 | 2 | 0 |
| `scene_event_cg` | 8 | 0 | 3 | 0 |
| `scene_prop_cg` | 7 | 0 | 2 | 0 |
| `ui_system_alert_frame` | 7 | 0 | 2 | 0 |
| `audio_bgm_with_sfx` | 17 | 0 | 5 | 0 |

## Errors

- None.

## Warnings

- None.

## User QA request

Please confirm whether this environment dependency preflight is acceptable before Unit 3. Unit 3 will do runtime patch dry-runs only, still without generation.
