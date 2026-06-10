from __future__ import annotations
from pathlib import Path
import copy
import hashlib
import json
import re
from typing import Any

root = Path('E:/workspace/comfyui-game-asset-workflows')
report_dir = root / 'docs/validation/workflow_pack_unit_qa_20260610'
runtime_root = report_dir / 'unit3_runtime_payloads'
runtime_root.mkdir(parents=True, exist_ok=True)
index = json.loads((root / 'WORKFLOW_INDEX.json').read_text(encoding='utf-8'))
endpoint_lock = 'http://127.0.0.1:8000'
(report_dir / 'qa_session_config.json').write_text(json.dumps({
    'comfyui_endpoint_locked_for_validation': endpoint_lock,
    'note': 'User approved using 127.0.0.1:8000 and ignoring 8001 for this workflow-pack validation session.',
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

placeholder_re = re.compile(r'TEMPLATE_[A-Za-z0-9_.*-]+|\{[^{}\n]{1,80}\}')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_field(path: str):
    parts = path.split('.')
    if len(parts) < 3 or parts[1] != 'inputs':
        return None
    return parts[0], parts[2]


def set_input(data: dict[str, Any], node: str, key: str, value: Any):
    if node not in data:
        raise KeyError(f'missing node {node}')
    data[node].setdefault('inputs', {})[key] = value


def changed_input_paths(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    paths=[]
    node_ids=sorted(set(before) | set(after), key=str)
    for nid in node_ids:
        b=before.get(nid)
        a=after.get(nid)
        if b != a:
            b_inputs = b.get('inputs', {}) if isinstance(b,dict) else {}
            a_inputs = a.get('inputs', {}) if isinstance(a,dict) else {}
            input_keys=sorted(set(b_inputs) | set(a_inputs), key=str)
            input_changes=[]
            for k in input_keys:
                if b_inputs.get(k) != a_inputs.get(k):
                    paths.append(f'{nid}.inputs.{k}')
                    input_changes.append(k)
            # If something besides inputs changed, mark whole node.
            b_non = {k:v for k,v in b.items() if k!='inputs'} if isinstance(b,dict) else b
            a_non = {k:v for k,v in a.items() if k!='inputs'} if isinstance(a,dict) else a
            if b_non != a_non:
                paths.append(f'{nid}.__node_non_input__')
    return paths


def unresolved_placeholders(data: dict[str, Any]) -> list[dict[str, str]]:
    hits=[]
    for nid,node in data.items():
        if not isinstance(node,dict):
            continue
        for key,value in (node.get('inputs') or {}).items():
            if isinstance(value,str):
                found=placeholder_re.findall(value)
                if found:
                    hits.append({'node':nid, 'input':key, 'value':value, 'placeholders': ', '.join(sorted(set(found)))})
    return hits


def patch_workflow(wid: str, data: dict[str, Any]):
    prefix=f'unit3_dryrun/{wid}/candidate'
    if wid == 'char_base':
        set_input(data,'3','text','masterpiece, best_quality, amazing_quality, 1girl, solo, visual_novel, standing, looking_at_viewer, medium_hair, brown_hair, brown_eyes, school_uniform, neutral_expression, simple_background')
        set_input(data,'4','text','text, watermark, logo, bad_anatomy, bad_hands, lowres, worst_quality, bad_quality')
        set_input(data,'5','width',1152); set_input(data,'5','height',1536)
        set_input(data,'6','seed',360610301); set_input(data,'6','steps',8); set_input(data,'6','cfg',4.0)
        set_input(data,'8','filename_prefix',prefix)
    elif wid == 'char_expression':
        set_input(data,'1','image','UNIT3_DRYRUN_source_character.png')
        set_input(data,'6','text','masterpiece, best_quality, 1girl, solo, same character, worried expression, open_mouth, brown_hair, brown_eyes, medium_hair, school_uniform')
        set_input(data,'7','text','happy, smile, text, watermark, bad_anatomy, identity_drift, outfit_drift')
        set_input(data,'13','seed',360610302); set_input(data,'13','denoise',0.35)
        set_input(data,'19','filename_prefix',prefix)
    elif wid == 'char_alpha':
        set_input(data,'1','image','UNIT3_DRYRUN_source_character.png')
        set_input(data,'3','filename_prefix',prefix)
    elif wid == 'scene_background':
        set_input(data,'3','text','masterpiece, best_quality, visual_novel, scenery, empty classroom, no_humans, desks, chairs, window, sunset, warm_light, indoors, depth_of_field')
        set_input(data,'4','text','1girl, boy, person, human, text, watermark, logo, signature, lowres, worst_quality, bad_quality')
        set_input(data,'5','width',1024); set_input(data,'5','height',576)
        set_input(data,'6','seed',360610303); set_input(data,'6','steps',8); set_input(data,'6','cfg',4.5)
        set_input(data,'8','filename_prefix',prefix)
    elif wid == 'scene_event_cg':
        set_input(data,'9','text','masterpiece, best_quality, visual_novel, game_cg, 1girl, solo, upper_body, pink_hair, purple_eyes, blue_jacket, red_bow, serious, looking_at_viewer, dark_noble_room, red_light, dramatic_lighting')
        set_input(data,'10','text','text, watermark, logo, duplicate_character, bad_anatomy, bad_hands, extra_fingers, lowres, worst_quality, bad_quality')
        set_input(data,'11','width',1024); set_input(data,'11','height',576)
        set_input(data,'12','seed',360610304); set_input(data,'12','steps',8); set_input(data,'12','cfg',4.5); set_input(data,'12','denoise',1.0)
        set_input(data,'14','filename_prefix',prefix)
    elif wid == 'scene_prop_cg':
        set_input(data,'3','text','masterpiece, best_quality, visual_novel, game_cg, single object, ornate red contract letter, sealed envelope, wax seal, dark wooden desk, dramatic shadow, no_humans')
        set_input(data,'4','text','text, readable letters, logo, watermark, duplicate object, hands, people, lowres, worst_quality, bad_quality')
        set_input(data,'5','width',1024); set_input(data,'5','height',576)
        set_input(data,'6','seed',360610305); set_input(data,'6','steps',8); set_input(data,'6','cfg',4.5)
        set_input(data,'8','filename_prefix',prefix)
    elif wid == 'ui_system_alert_frame':
        set_input(data,'3','text','masterpiece, best_quality, game_cg, visual_novel, user_interface, ornate_border, red_border, black_border, gold_trim, red_theme, black_theme, dark_background, no_humans, border, corner')
        set_input(data,'4','text','text, letters, logo, watermark, symbol, icon, emblem, character, face, person, object, gem, cross, lowres, worst_quality, bad_quality')
        set_input(data,'5','width',1024); set_input(data,'5','height',576)
        set_input(data,'6','seed',360610306); set_input(data,'6','steps',8); set_input(data,'6','cfg',4.0)
        set_input(data,'8','filename_prefix',prefix)
    elif wid == 'audio_bgm_with_sfx':
        set_input(data,'52:31','value','short dark fantasy visual novel user interface notification, clear glass bell chime, subtle ominous pulse, quick decay, no voice, no speech, no music, no melody')
        set_input(data,'52:7','text','speech, human voice, talking, singing, lyrics, background music, melody, distorted, clipping')
        set_input(data,'52:43','choice','One-shot'); set_input(data,'52:43','index',3)
        set_input(data,'52:36','value',2.5)
        set_input(data,'52:35','value',False)
        set_input(data,'52:3','seed',360610307); set_input(data,'52:3','steps',8); set_input(data,'52:3','cfg',1.0); set_input(data,'52:3','sampler_name','lcm'); set_input(data,'52:3','scheduler','simple')
        set_input(data,'19','filename_prefix',prefix)
    else:
        raise ValueError(f'No dry-run patch recipe for {wid}')


results=[]
errors=[]
warnings=[]
for w in index.get('workflows', []):
    wid=w['id']
    api=root / w['api']
    before_bytes=api.read_bytes()
    before_text=before_bytes.decode('utf-8')
    before=json.loads(before_text)
    before_hash=hashlib.sha256(before_bytes).hexdigest()
    after=copy.deepcopy(before)
    try:
        patch_workflow(wid, after)
    except Exception as e:
        errors.append(f'{wid}: patch recipe failed: {type(e).__name__}: {e}')
        continue
    changed=changed_input_paths(before, after)
    allowed=set(w.get('editable_fields', []))
    disallowed=[p for p in changed if p not in allowed]
    unresolved=unresolved_placeholders(after)
    runtime_dir=runtime_root / wid
    runtime_dir.mkdir(parents=True, exist_ok=True)
    runtime_path=runtime_dir / f'{wid}_unit3_dryrun_workflow_api.json'
    runtime_path.write_text(json.dumps(after, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    after_hash=sha(api)
    canonical_unchanged = before_hash == after_hash
    if disallowed:
        errors.append(f'{wid}: changed fields outside editable_fields: {disallowed}')
    if unresolved:
        errors.append(f'{wid}: unresolved placeholders remain: {unresolved[:5]}')
    if not canonical_unchanged:
        errors.append(f'{wid}: canonical JSON hash changed during dry-run')
    if not changed:
        warnings.append(f'{wid}: no changed fields detected')
    results.append({
        'workflow_id': wid,
        'canonical_api': str(api),
        'runtime_path': str(runtime_path),
        'canonical_sha256_before': before_hash,
        'canonical_sha256_after': after_hash,
        'canonical_unchanged': canonical_unchanged,
        'changed_fields': changed,
        'changed_fields_count': len(changed),
        'disallowed_changes': disallowed,
        'unresolved_placeholders': unresolved,
        'allowed_editable_fields_count': len(allowed),
    })

summary={
    'root': str(root),
    'endpoint_lock': endpoint_lock,
    'runtime_root': str(runtime_root),
    'workflow_count': len(index.get('workflows', [])),
    'errors': errors,
    'warnings': warnings,
    'results': results,
}
(report_dir / 'unit3_runtime_patch_dryrun.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

md=[]
md.append('# Unit 3 — Runtime Patch Dry-run QA\n\n')
md.append('## Scope\n\n')
md.append('No generation was run and `/prompt` was not called. This unit only writes runtime workflow copies and verifies patch safety.\n\n')
md.append(f'- Endpoint locked for later generation: `{endpoint_lock}`\n')
md.append(f'- Runtime payload root: `{runtime_root}`\n\n')
md.append('## Summary\n\n')
md.append(f'- Workflows patched: **{len(results)}**\n')
md.append(f'- Errors: **{len(errors)}**\n')
md.append(f'- Warnings: **{len(warnings)}**\n\n')
md.append('## Per-workflow dry-run result\n\n')
md.append('| workflow_id | changed fields | disallowed changes | unresolved placeholders | canonical unchanged | runtime path |\n')
md.append('|---|---:|---:|---:|---|---|\n')
for r in results:
    rel=Path(r['runtime_path']).relative_to(root)
    md.append(f"| `{r['workflow_id']}` | {r['changed_fields_count']} | {len(r['disallowed_changes'])} | {len(r['unresolved_placeholders'])} | {r['canonical_unchanged']} | `{rel}` |\n")
md.append('\n## Errors\n\n')
if errors:
    for e in errors: md.append(f'- {e}\n')
else:
    md.append('- None.\n')
md.append('\n## Warnings\n\n')
if warnings:
    for w in warnings: md.append(f'- {w}\n')
else:
    md.append('- None.\n')
md.append('\n## User QA request\n\n')
md.append('Please confirm whether these runtime patch dry-runs are acceptable before Unit 4. Unit 4 will be the first actual generation smoke, starting with the smallest audio SFX smoke unless you choose otherwise.\n')
(report_dir / 'unit3_runtime_patch_dryrun.md').write_text(''.join(md), encoding='utf-8')

print('UNIT3_REPORT_MD', report_dir / 'unit3_runtime_patch_dryrun.md')
print('UNIT3_REPORT_JSON', report_dir / 'unit3_runtime_patch_dryrun.json')
print('runtime_root', runtime_root)
print('patched_workflows', len(results))
print('errors', len(errors))
print('warnings', len(warnings))
for r in results:
    print(r['workflow_id'], 'changed', r['changed_fields_count'], 'disallowed', len(r['disallowed_changes']), 'placeholders', len(r['unresolved_placeholders']), 'canonical_unchanged', r['canonical_unchanged'])
