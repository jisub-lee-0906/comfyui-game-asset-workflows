from __future__ import annotations
from pathlib import Path
import json
import urllib.request
import urllib.error
import time

root = Path('E:/workspace/comfyui-game-asset-workflows')
report_dir = root / 'docs/validation/workflow_pack_unit_qa_20260610'
report_dir.mkdir(parents=True, exist_ok=True)
index = json.loads((root / 'WORKFLOW_INDEX.json').read_text(encoding='utf-8'))

candidate_endpoints = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8188',
    'http://127.0.0.1:8001',
]


def fetch_json(url: str, timeout: float = 5.0):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        body = r.read().decode('utf-8', errors='replace')
        return r.status, json.loads(body) if body else None


endpoint_results = []
live_endpoint = None
for base in candidate_endpoints:
    item = {'endpoint': base, 'checks': {}}
    all_ok = True
    for path in ['/system_stats', '/queue', '/object_info']:
        try:
            t0 = time.time()
            status, data = fetch_json(base + path, timeout=8.0)
            elapsed = round(time.time() - t0, 3)
            item['checks'][path] = {
                'ok': status == 200,
                'status': status,
                'elapsed_s': elapsed,
                'top_level_type': type(data).__name__,
                'top_level_count': len(data) if hasattr(data, '__len__') else None,
            }
            if status != 200:
                all_ok = False
        except Exception as e:
            all_ok = False
            item['checks'][path] = {'ok': False, 'error': f'{type(e).__name__}: {e}'}
    item['all_ok'] = all_ok
    endpoint_results.append(item)
    if all_ok and live_endpoint is None:
        live_endpoint = base

object_info = {}
system_stats = None
queue = None
if live_endpoint:
    _, system_stats = fetch_json(live_endpoint + '/system_stats', timeout=10.0)
    _, queue = fetch_json(live_endpoint + '/queue', timeout=10.0)
    _, object_info = fetch_json(live_endpoint + '/object_info', timeout=20.0)

workflow_rows = []
all_required_classes = set()
missing_classes = []
choice_mismatches = []
choice_checks = []

MODEL_INPUT_KEYWORDS = (
    'ckpt', 'checkpoint', 'model', 'lora', 'clip', 'vae', 'sam', 'bbox', 'detector', 'control_net', 'controlnet'
)


def get_choice_list(class_schema: dict, input_name: str):
    # ComfyUI object_info format usually:
    # object_info[class]['input']['required'][input_name] = [[choices], {...}]
    inp = class_schema.get('input') if isinstance(class_schema, dict) else None
    if not isinstance(inp, dict):
        return None
    for section in ['required', 'optional']:
        sec = inp.get(section)
        if not isinstance(sec, dict) or input_name not in sec:
            continue
        spec = sec[input_name]
        if isinstance(spec, list) and spec:
            first = spec[0]
            if isinstance(first, list):
                return first
            if isinstance(first, tuple):
                return list(first)
        if isinstance(spec, tuple) and spec:
            first = spec[0]
            if isinstance(first, (list, tuple)):
                return list(first)
    return None


for w in index.get('workflows', []):
    api = root / w['api']
    data = json.loads(api.read_text(encoding='utf-8'))
    classes = sorted({node.get('class_type') for node in data.values() if isinstance(node, dict) and node.get('class_type')})
    missing = [c for c in classes if live_endpoint and c not in object_info]
    all_required_classes.update(classes)
    for c in missing:
        missing_classes.append({'workflow_id': w['id'], 'class_type': c})
    row = {
        'workflow_id': w['id'],
        'api': str(api),
        'class_count': len(classes),
        'classes': classes,
        'missing_classes': missing,
    }
    # Check model-like string inputs against object_info choices when choices are available.
    checks = []
    for node_id, node in data.items():
        if not isinstance(node, dict):
            continue
        cls = node.get('class_type')
        schema = object_info.get(cls, {}) if live_endpoint else {}
        for input_name, value in (node.get('inputs') or {}).items():
            if not isinstance(value, str):
                continue
            lname = input_name.lower()
            if not any(k in lname for k in MODEL_INPUT_KEYWORDS):
                continue
            choices = get_choice_list(schema, input_name)
            check = {
                'workflow_id': w['id'],
                'node_id': node_id,
                'class_type': cls,
                'input': input_name,
                'value': value,
                'choices_known': choices is not None,
                'ok': None,
            }
            if choices is not None:
                check['choice_count'] = len(choices)
                check['ok'] = value in choices
                if value not in choices:
                    check['sample_choices'] = choices[:20]
                    choice_mismatches.append(check)
            checks.append(check)
            choice_checks.append(check)
    row['model_choice_checks'] = checks
    workflow_rows.append(row)

summary = {
    'root': str(root),
    'candidate_endpoints': candidate_endpoints,
    'endpoint_results': endpoint_results,
    'live_endpoint': live_endpoint,
    'system_stats_summary': {
        'keys': sorted(system_stats.keys()) if isinstance(system_stats, dict) else None,
        'devices': system_stats.get('devices') if isinstance(system_stats, dict) else None,
    },
    'queue_summary': queue,
    'object_info_class_count': len(object_info) if isinstance(object_info, dict) else 0,
    'required_class_count': len(all_required_classes),
    'missing_classes': missing_classes,
    'choice_mismatches': choice_mismatches,
    'workflow_rows': workflow_rows,
}
(report_dir / 'unit2_comfyui_preflight.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

errors = []
warnings = []
if not live_endpoint:
    errors.append('No live endpoint with /system_stats, /queue, and /object_info all OK.')
if missing_classes:
    errors.append(f'Missing object_info classes: {len(missing_classes)}')
if choice_mismatches:
    warnings.append(f'Model/input choice mismatches found: {len(choice_mismatches)}')

md = []
md.append('# Unit 2 — ComfyUI Endpoint / object_info / Model Preflight\n\n')
md.append('## Scope\n\n')
md.append('No generation was run. This unit only checks live ComfyUI API readiness and workflow dependency visibility.\n\n')
md.append('## Endpoint discovery\n\n')
for item in endpoint_results:
    md.append(f"- `{item['endpoint']}`: {'OK' if item['all_ok'] else 'NOT READY'}\n")
    for path, c in item['checks'].items():
        if c.get('ok'):
            md.append(f"  - `{path}`: OK status={c.get('status')} elapsed={c.get('elapsed_s')}s count={c.get('top_level_count')}\n")
        else:
            md.append(f"  - `{path}`: FAIL {c.get('error') or c}\n")
md.append(f"\nSelected live endpoint: `{live_endpoint}`\n\n")

md.append('## Summary\n\n')
md.append(f"- object_info class count: **{len(object_info) if isinstance(object_info, dict) else 0}**\n")
md.append(f"- required class count from workflows: **{len(all_required_classes)}**\n")
md.append(f"- missing class entries: **{len(missing_classes)}**\n")
md.append(f"- model/input choice mismatches: **{len(choice_mismatches)}**\n")
md.append(f"- errors: **{len(errors)}**\n")
md.append(f"- warnings: **{len(warnings)}**\n\n")

md.append('## Workflow class availability\n\n')
md.append('| workflow_id | class count | missing classes | model choice checks | choice mismatches |\n')
md.append('|---|---:|---:|---:|---:|\n')
for row in workflow_rows:
    mismatches = [m for m in choice_mismatches if m['workflow_id'] == row['workflow_id']]
    md.append(f"| `{row['workflow_id']}` | {row['class_count']} | {len(row['missing_classes'])} | {len(row['model_choice_checks'])} | {len(mismatches)} |\n")

if missing_classes:
    md.append('\n## Missing classes\n\n')
    for m in missing_classes:
        md.append(f"- `{m['workflow_id']}` requires `{m['class_type']}`\n")

if choice_mismatches:
    md.append('\n## Model/input choice mismatches\n\n')
    for m in choice_mismatches:
        md.append(f"- `{m['workflow_id']}` node `{m['node_id']}` `{m['class_type']}.{m['input']}` value `{m['value']}` not in object_info choices. Sample choices: {m.get('sample_choices')}\n")

md.append('\n## Errors\n\n')
if errors:
    for e in errors:
        md.append(f'- {e}\n')
else:
    md.append('- None.\n')

md.append('\n## Warnings\n\n')
if warnings:
    for w in warnings:
        md.append(f'- {w}\n')
else:
    md.append('- None.\n')

md.append('\n## User QA request\n\n')
md.append('Please confirm whether this environment dependency preflight is acceptable before Unit 3. Unit 3 will do runtime patch dry-runs only, still without generation.\n')
(report_dir / 'unit2_comfyui_preflight.md').write_text(''.join(md), encoding='utf-8')

print('UNIT2_REPORT_MD', report_dir / 'unit2_comfyui_preflight.md')
print('UNIT2_REPORT_JSON', report_dir / 'unit2_comfyui_preflight.json')
print('live_endpoint', live_endpoint)
print('object_info_class_count', len(object_info) if isinstance(object_info, dict) else 0)
print('required_class_count', len(all_required_classes))
print('missing_classes', len(missing_classes))
print('choice_mismatches', len(choice_mismatches))
print('errors', len(errors))
print('warnings', len(warnings))
