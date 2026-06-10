from __future__ import annotations
from pathlib import Path
import json
import shutil
import subprocess
import time
import urllib.request
import uuid
import re

root = Path('E:/workspace/comfyui-game-asset-workflows')
report_dir = root / 'docs/validation/workflow_pack_unit_qa_20260610'
unit_dir = report_dir / 'unit4b_simplified_sfx_smoke'
runtime_dir = unit_dir / 'runtime_payloads'
candidate_dir = unit_dir / 'candidates'
for p in [runtime_dir, candidate_dir]:
    p.mkdir(parents=True, exist_ok=True)

endpoint = 'http://127.0.0.1:8000'
output_root = Path('C:/Users/Desktop/Documents/ComfyUI/output')
workflow_path = root / 'audio_bgm_with_sfx/audio_bgm_with_sfx_workflow_api.json'
base_workflow = json.loads(workflow_path.read_text(encoding='utf-8'))
MODE_INDEX = {'Music': 0, 'Instrument': 1, 'SFX': 2, 'One-shot': 3}

SCENARIOS = [
    {
        'id': 'simple_ui_system_chime',
        'label': 'A_simple_ui_system_chime',
        'intent': 'short UI/system cue using simple positive-only prompt',
        'mode': 'One-shot',
        'duration': 2.5,
        'seed': 360610411,
        'positive': 'A short glass chime rings when a visual novel system notification appears, with a clear crystal bell tone.',
        'negative': '',
    },
    {
        'id': 'simple_old_wooden_door',
        'label': 'B_simple_old_wooden_door',
        'intent': 'medium foley/action cue using simple positive-only prompt',
        'mode': 'SFX',
        'duration': 3.5,
        'seed': 360610412,
        'positive': 'An old wooden door opens slowly with one clear metal hinge creak and a soft wooden handle click.',
        'negative': '',
    },
    {
        'id': 'simple_contract_magic_seal',
        'label': 'C_simple_contract_magic_seal',
        'intent': 'longer sustained contract magic cue using simple positive-only prompt',
        'mode': 'SFX',
        'duration': 7.0,
        'seed': 360610413,
        'positive': 'A dark fantasy contract seal activates with a soft arcane hum, parchment shimmer, and gentle crystal resonance.',
        'negative': '',
    },
]


def submit_prompt(workflow: dict) -> str:
    payload = json.dumps({'prompt': workflow, 'client_id': str(uuid.uuid4())}).encode('utf-8')
    req = urllib.request.Request(endpoint + '/prompt', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8', errors='replace'))
        return data['prompt_id']


def wait_history(prompt_id: str, timeout_s: int = 600) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        with urllib.request.urlopen(endpoint + '/history/' + prompt_id, timeout=10) as r:
            hist = json.load(r)
        item = hist.get(prompt_id)
        if isinstance(item, dict) and item.get('outputs'):
            return item
        time.sleep(3)
    raise TimeoutError(prompt_id)


def history_audio_paths(history: dict) -> list[Path]:
    paths=[]
    for out in history.get('outputs', {}).values():
        if not isinstance(out, dict):
            continue
        for key in ['audios', 'audio']:
            entries=out.get(key, [])
            if isinstance(entries, dict):
                entries=[entries]
            for item in entries or []:
                if not isinstance(item, dict):
                    continue
                if item.get('type','output') != 'output':
                    continue
                fn=item.get('filename')
                sub=str(item.get('subfolder') or '').replace('\\','/')
                if fn:
                    paths.append((output_root / sub / fn).resolve())
    return paths


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)


def analyze_audio(path: Path) -> dict:
    probe = json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,bit_rate,size:stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(path)]).stdout)
    vol = run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','volumedetect','-f','null','-']).stderr
    mean=maxv=None
    for line in vol.splitlines():
        if 'mean_volume' in line:
            m=re.search(r'mean_volume: ([\-0-9.]+)', line)
            mean=float(m.group(1)) if m else None
        if 'max_volume' in line:
            m=re.search(r'max_volume: ([\-0-9.]+)', line)
            maxv=float(m.group(1)) if m else None
    sil = run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','silencedetect=noise=-45dB:d=0.5','-f','null','-']).stderr
    silence=[line for line in sil.splitlines() if 'silence_' in line]
    return {
        'ffprobe': probe,
        'duration': float(probe['format']['duration']),
        'sample_rate': probe['streams'][0].get('sample_rate'),
        'channels': probe['streams'][0].get('channels'),
        'mean_volume_db': mean,
        'max_volume_db': maxv,
        'silencedetect_-45dB_d0.5': silence,
    }

results=[]
for sc in SCENARIOS:
    workflow = json.loads(json.dumps(base_workflow))
    workflow['52:31']['inputs']['value'] = sc['positive']
    workflow['52:7']['inputs']['text'] = sc['negative']
    workflow['52:43']['inputs']['choice'] = sc['mode']
    workflow['52:43']['inputs']['index'] = MODE_INDEX[sc['mode']]
    workflow['52:36']['inputs']['value'] = sc['duration']
    workflow['52:35']['inputs']['value'] = False
    workflow['52:3']['inputs']['seed'] = sc['seed']
    workflow['52:3']['inputs']['steps'] = 8
    workflow['52:3']['inputs']['cfg'] = 1.0
    workflow['52:3']['inputs']['sampler_name'] = 'lcm'
    workflow['52:3']['inputs']['scheduler'] = 'simple'
    workflow['19']['inputs']['filename_prefix'] = f'workflow_pack_unit4b/{sc["id"]}'
    runtime_path = runtime_dir / f'{sc["id"]}_workflow_api.json'
    runtime_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    prompt_id = submit_prompt(workflow)
    history = wait_history(prompt_id)
    history_path = runtime_dir / f'{sc["id"]}_history.json'
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    output_paths = history_audio_paths(history)
    copies=[]
    analyses=[]
    for i,p in enumerate(output_paths,1):
        if p.exists():
            dst = candidate_dir / f'{sc["label"]}_candidate_{i:02d}{p.suffix.lower() or ".mp3"}'
            shutil.copy2(p, dst)
            copies.append(dst)
            analyses.append(analyze_audio(dst))
    results.append({
        **sc,
        'workflow_id': 'audio_bgm_with_sfx',
        'runtime_path': str(runtime_path),
        'prompt_id': prompt_id,
        'history_path': str(history_path),
        'output_paths': [str(p) for p in output_paths],
        'candidate_copies': [str(p) for p in copies],
        'analyses': analyses,
        'verified_output_count': len(copies),
    })

summary={
    'unit': 'Unit 4B — simplified positive-only SFX prompts',
    'endpoint': endpoint,
    'workflow_path': str(workflow_path),
    'prompting_rule': 'short positive-only natural language sentence; negative prompt intentionally blank',
    'no_promotion': True,
    'scenario_count': len(SCENARIOS),
    'results': results,
    'errors': [r['id'] for r in results if r['verified_output_count'] == 0],
}
(unit_dir / 'unit4b_simplified_sfx_smoke.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

md=[]
md.append('# Unit 4B — Simplified Positive-only SFX Prompt Smoke\n\n')
md.append('## Scope\n\n')
md.append('Retests all three SFX situations using the owner-requested prompting style: short positive-only natural language prompts, no negative prompt. No asset was promoted.\n\n')
md.append(f'- Endpoint: `{endpoint}`\n')
md.append(f'- Workflow: `{workflow_path}`\n')
md.append(f'- Candidate directory: `{candidate_dir}`\n\n')
md.append('## Results\n\n')
md.append('| ID | mode | target duration | seed | prompt_id | verified files | measured duration | mean/max dB | silence note |\n')
md.append('|---|---|---:|---:|---|---:|---:|---:|---|\n')
for r in results:
    a=r['analyses'][0] if r['analyses'] else {}
    sil=a.get('silencedetect_-45dB_d0.5') or []
    silnote='; '.join(sil[:2]) if sil else 'none'
    md.append(f"| `{r['label']}` | `{r['mode']}` | {r['duration']}s | {r['seed']} | `{r['prompt_id']}` | {r['verified_output_count']} | {a.get('duration','?')} | {a.get('mean_volume_db','?')} / {a.get('max_volume_db','?')} | {silnote} |\n")
md.append('\n## Prompts and files\n\n')
for r in results:
    md.append(f"### {r['label']}\n\n")
    md.append(f"Intent: {r['intent']}\n\n")
    md.append(f"Positive-only prompt: `{r['positive']}`\n\n")
    md.append('Negative prompt: intentionally blank.\n\n')
    for p in r['candidate_copies']:
        md.append(f'- `{p}`\n')
    md.append('\n')
md.append('## User QA request\n\n')
md.append('Please compare against Unit 4 and judge whether simplified positive-only prompting improves semantic accuracy for UI cue, door foley, and sustained contract magic SFX.\n')
(unit_dir / 'unit4b_simplified_sfx_smoke.md').write_text(''.join(md), encoding='utf-8')

print('UNIT4B_REPORT_MD', unit_dir / 'unit4b_simplified_sfx_smoke.md')
print('UNIT4B_REPORT_JSON', unit_dir / 'unit4b_simplified_sfx_smoke.json')
for r in results:
    print(r['label'], 'mode', r['mode'], 'duration_target', r['duration'], 'seed', r['seed'], 'prompt_id', r['prompt_id'], 'verified', r['verified_output_count'])
    for p,a in zip(r['candidate_copies'], r['analyses']):
        print(' ', p, 'duration', a['duration'], 'mean/max', a['mean_volume_db'], a['max_volume_db'])
