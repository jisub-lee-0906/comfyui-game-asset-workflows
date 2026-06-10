from __future__ import annotations
from pathlib import Path
import json, hashlib, re

root = Path('E:/workspace/comfyui-game-asset-workflows')
report_dir = root / 'docs/validation/workflow_pack_unit_qa_20260610'
report_dir.mkdir(parents=True, exist_ok=True)
index_path = root / 'WORKFLOW_INDEX.json'

errors=[]
warnings=[]

try:
    index=json.loads(index_path.read_text(encoding='utf-8'))
except Exception as e:
    raise SystemExit(f'FATAL: cannot parse WORKFLOW_INDEX.json: {e}')

workflows=index.get('workflows', [])
ids=[]
rows=[]
for w in workflows:
    wid=w.get('id')
    ids.append(wid)
    folder=root / w.get('folder','')
    readme=root / w.get('readme','')
    api=root / w.get('api','')
    row={
        'id': wid,
        'folder': str(folder),
        'folder_exists': folder.exists() and folder.is_dir(),
        'readme': str(readme),
        'readme_exists': readme.exists() and readme.is_file(),
        'api': str(api),
        'api_exists': api.exists() and api.is_file(),
        'requires_input_images': w.get('requires_input_images', False),
        'requires_input_video': w.get('requires_input_video', False),
        'editable_fields_count': len(w.get('editable_fields', [])),
        'status': w.get('status'),
    }
    if row['api_exists']:
        try:
            data=json.loads(api.read_text(encoding='utf-8'))
            row['api_node_count']=len(data)
            row['api_sha256']=hashlib.sha256(api.read_bytes()).hexdigest()
            row['class_types']=sorted({v.get('class_type') for v in data.values() if isinstance(v,dict) and v.get('class_type')})
            missing=[]
            for nid,node in data.items():
                if not isinstance(node,dict):
                    continue
                for k,v in (node.get('inputs') or {}).items():
                    if isinstance(v,list) and len(v)==2 and isinstance(v[0],str):
                        if v[0] not in data:
                            missing.append({'node':nid,'input':k,'missing_ref':v[0]})
            row['dangling_refs']=missing
            if missing:
                errors.append(f'{wid}: dangling refs {missing[:3]}')
        except Exception as e:
            row['api_parse_error']=str(e)
            errors.append(f'{wid}: api parse failed: {e}')
    for key in ['folder_exists','readme_exists','api_exists']:
        if not row[key]:
            errors.append(f'{wid}: {key}=False')
    rows.append(row)

for wid in sorted(set(ids)):
    if ids.count(wid)>1:
        errors.append(f'duplicate workflow id: {wid}')

actual=[]
for p in sorted(root.iterdir()):
    if p.is_dir() and (p/'README.md').exists() and list(p.glob('*_workflow_api.json')):
        actual.append(p.name)
indexed=[w.get('folder') for w in workflows]
extra=[x for x in actual if x not in indexed]
missing=[x for x in indexed if x not in actual]
if extra:
    warnings.append(f'workflow-like folders not indexed: {extra}')
if missing:
    errors.append(f'indexed workflow folders missing from actual scan: {missing}')

old_terms=['audio_bgm_ace','audio_sfx_mmaudio','run_audio_sfx_mmaudio']
old_refs=[]
for p in root.rglob('*'):
    if 'backups' in p.parts:
        continue
    if report_dir in p.parents:
        continue
    if p.is_file() and p.suffix.lower() in {'.md','.json','.py','.txt','.yaml','.yml'}:
        try:
            txt=p.read_text(encoding='utf-8')
        except Exception:
            continue
        for term in old_terms:
            if term in txt:
                old_refs.append({'file':str(p),'term':term})
if old_refs:
    errors.append(f'old audio refs in active files: {old_refs[:10]}')

placeholder_re=re.compile(r'TEMPLATE_[A-Za-z0-9_.*-]+|\{[^{}\n]{1,80}\}')
placeholders=[]
for row in rows:
    for fkey in ['api','readme']:
        p=Path(row[fkey])
        if p.exists():
            txt=p.read_text(encoding='utf-8')
            hits=sorted(set(m.group(0) for m in placeholder_re.finditer(txt)))
            if hits:
                placeholders.append({'workflow_id':row['id'],'file':str(p),'placeholders':hits})

summary={
    'root': str(root),
    'index_version': index.get('version'),
    'workflow_count': len(workflows),
    'workflow_ids': ids,
    'actual_workflow_like_folders': actual,
    'extra_workflow_like_folders': extra,
    'missing_workflow_like_folders': missing,
    'errors': errors,
    'warnings': warnings,
    'old_active_refs': old_refs,
    'placeholders': placeholders,
    'workflows': rows,
}
(report_dir/'unit1_static_inventory.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

md=[]
md.append('# Unit 1 — Workflow Pack Static Inventory QA\n\n')
md.append('## Scope\n\n')
md.append(f'Root: `{root}`\n\n')
md.append('No ComfyUI generation was run in this unit. This only checks the pack map and static files.\n\n')
md.append('## Result\n\n')
md.append(f'- Workflow count in index: **{len(workflows)}**\n')
md.append(f'- Errors: **{len(errors)}**\n')
md.append(f'- Warnings: **{len(warnings)}**\n')
md.append(f'- Active old audio refs: **{len(old_refs)}**\n')
md.append('\n## Canonical workflows\n\n')
md.append('| # | workflow_id | folder | API | README | input image? | editable fields | node count |\n')
md.append('|---:|---|---|---|---|---:|---:|---:|\n')
for i,row in enumerate(rows,1):
    md.append(f"| {i} | `{row['id']}` | {'OK' if row['folder_exists'] else 'MISSING'} | {'OK' if row['api_exists'] else 'MISSING'} | {'OK' if row['readme_exists'] else 'MISSING'} | {row['requires_input_images']} | {row['editable_fields_count']} | {row.get('api_node_count','?')} |\n")
md.append('\n## Actual workflow-like folders found\n\n')
for x in actual:
    md.append(f'- `{x}`\n')
md.append('\n## Deleted/legacy audio workflow active-reference check\n\n')
if old_refs:
    for r in old_refs:
        md.append(f"- FAIL `{r['term']}` in `{r['file']}`\n")
else:
    md.append('- PASS: no active refs to `audio_bgm_ace`, `audio_sfx_mmaudio`, or `run_audio_sfx_mmaudio`.\n')
md.append('\n## Placeholder inventory for later runtime tests\n\n')
if placeholders:
    for item in placeholders:
        rel=Path(item['file']).relative_to(root)
        hits=', '.join('`'+h+'`' for h in item['placeholders'][:20])
        md.append(f"- `{item['workflow_id']}` / `{rel}`: {hits}\n")
else:
    md.append('- No placeholders found.\n')
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
md.append('Please confirm whether this canonical list and scope are correct before Unit 2. Unit 2 will check ComfyUI endpoint/object_info/model availability without generating assets.\n')
(report_dir/'unit1_static_inventory.md').write_text(''.join(md), encoding='utf-8')

print('UNIT1_REPORT_MD', report_dir/'unit1_static_inventory.md')
print('UNIT1_REPORT_JSON', report_dir/'unit1_static_inventory.json')
print('workflow_count', len(workflows))
print('errors', len(errors))
print('warnings', len(warnings))
print('old_active_refs', len(old_refs))
print('workflow_ids', ', '.join(ids))
