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
unit_dir = report_dir / 'unit5_bgm_smoke'
runtime_dir = unit_dir / 'runtime_payloads'
candidate_dir = unit_dir / 'candidates'
for p in [runtime_dir, candidate_dir]:
    p.mkdir(parents=True, exist_ok=True)

endpoint = 'http://127.0.0.1:8000'
output_root = Path('C:/Users/Desktop/Documents/ComfyUI/output')
workflow_path = root / 'audio_bgm_with_sfx/audio_bgm_with_sfx_workflow_api.json'
workflow = json.loads(workflow_path.read_text(encoding='utf-8'))

scenario = {
    'id': 'bgm_dialogue_dark_romantic_bed',
    'label': 'A_dialogue_dark_romantic_bed',
    'intent': 'continuous dialogue-friendly BGM bed; B2/B2-anchor style direction, but not prompt/seed clone',
    'mode': 'Music',
    'duration': 24.0,
    'seed': 360610501,
    'positive': 'A quiet dark romantic fantasy background music bed for visual novel dialogue, with soft felt piano, low strings, and gentle harp texture.',
    'negative': '',
}
MODE_INDEX = {'Music': 0, 'Instrument': 1, 'SFX': 2, 'One-shot': 3}

workflow['52:31']['inputs']['value'] = scenario['positive']
workflow['52:7']['inputs']['text'] = scenario['negative']
workflow['52:43']['inputs']['choice'] = scenario['mode']
workflow['52:43']['inputs']['index'] = MODE_INDEX[scenario['mode']]
workflow['52:36']['inputs']['value'] = scenario['duration']
workflow['52:35']['inputs']['value'] = False
workflow['52:3']['inputs']['seed'] = scenario['seed']
workflow['52:3']['inputs']['steps'] = 8
workflow['52:3']['inputs']['cfg'] = 1.0
workflow['52:3']['inputs']['sampler_name'] = 'lcm'
workflow['52:3']['inputs']['scheduler'] = 'simple'
workflow['19']['inputs']['filename_prefix'] = f'workflow_pack_unit5/{scenario["id"]}'

runtime_path = runtime_dir / f'{scenario["id"]}_workflow_api.json'
runtime_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

payload = json.dumps({'prompt': workflow, 'client_id': str(uuid.uuid4())}).encode('utf-8')
req = urllib.request.Request(endpoint + '/prompt', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=30) as r:
    submit = json.loads(r.read().decode('utf-8', errors='replace'))
prompt_id = submit['prompt_id']

deadline = time.time() + 600
history = None
while time.time() < deadline:
    with urllib.request.urlopen(endpoint + '/history/' + prompt_id, timeout=10) as r:
        hist = json.load(r)
    item = hist.get(prompt_id)
    if isinstance(item, dict) and item.get('outputs'):
        history = item
        break
    time.sleep(3)
if history is None:
    raise TimeoutError(prompt_id)

history_path = runtime_dir / f'{scenario["id"]}_history.json'
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

output_paths=[]
for out in history.get('outputs', {}).values():
    if not isinstance(out, dict):
        continue
    for key in ['audios', 'audio']:
        entries = out.get(key, [])
        if isinstance(entries, dict):
            entries = [entries]
        for item in entries or []:
            if isinstance(item, dict) and item.get('type','output') == 'output' and item.get('filename'):
                output_paths.append((output_root / str(item.get('subfolder') or '').replace('\\','/') / item['filename']).resolve())

def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)

def analyze(path: Path) -> dict:
    probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,bit_rate,size:stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(path)]).stdout)
    vol=run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','volumedetect','-f','null','-']).stderr
    mean=maxv=None
    for line in vol.splitlines():
        if 'mean_volume' in line:
            m=re.search(r'mean_volume: ([\-0-9.]+)', line); mean=float(m.group(1)) if m else None
        if 'max_volume' in line:
            m=re.search(r'max_volume: ([\-0-9.]+)', line); maxv=float(m.group(1)) if m else None
    sil=run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','silencedetect=noise=-45dB:d=1.0','-f','null','-']).stderr
    return {
        'ffprobe': probe,
        'duration': float(probe['format']['duration']),
        'sample_rate': probe['streams'][0].get('sample_rate'),
        'channels': probe['streams'][0].get('channels'),
        'mean_volume_db': mean,
        'max_volume_db': maxv,
        'silencedetect_-45dB_d1.0': [line for line in sil.splitlines() if 'silence_' in line],
    }

copies=[]
analyses=[]
for i,p in enumerate(output_paths,1):
    if p.exists():
        dst = candidate_dir / f'{scenario["label"]}_candidate_{i:02d}{p.suffix.lower() or ".mp3"}'
        shutil.copy2(p, dst)
        copies.append(dst)
        analyses.append(analyze(dst))

result={
    **scenario,
    'workflow_id': 'audio_bgm_with_sfx',
    'runtime_path': str(runtime_path),
    'prompt_id': prompt_id,
    'history_path': str(history_path),
    'output_paths': [str(p) for p in output_paths],
    'candidate_copies': [str(p) for p in copies],
    'analyses': analyses,
    'verified_output_count': len(copies),
}
summary={
    'unit': 'Unit 5 — BGM single smoke',
    'endpoint': endpoint,
    'workflow_path': str(workflow_path),
    'prompting_rule': 'short natural-language BGM prompt with instruments, negative prompt intentionally blank',
    'no_promotion': True,
    'result': result,
    'errors': [] if copies else ['no verified output'],
}
(unit_dir / 'unit5_bgm_smoke.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

a = analyses[0] if analyses else {}
sil = a.get('silencedetect_-45dB_d1.0') or []
silnote = '; '.join(sil[:4]) if sil else 'none'
md = f'''# Unit 5 — BGM Single Smoke

## Scope

First BGM generation unit after SFX validation. One candidate only. No promotion.

- Endpoint: `{endpoint}`
- Workflow: `{workflow_path}`
- Candidate directory: `{candidate_dir}`

## Intent

{scenario['intent']}

## Prompt

Positive-only prompt:

```text
{scenario['positive']}
```

Negative prompt: intentionally blank.

## Settings

```text
mode: {scenario['mode']}
duration: {scenario['duration']}s
seed: {scenario['seed']}
steps: 8
cfg: 1.0
sampler: lcm
scheduler: simple
prompt_id: {prompt_id}
```

## Candidate

- `{copies[0] if copies else 'NO VERIFIED OUTPUT'}`

## Objective QA

```text
verified files: {len(copies)}
measured duration: {a.get('duration','?')}
sample_rate: {a.get('sample_rate','?')}
channels: {a.get('channels','?')}
mean/max dB: {a.get('mean_volume_db','?')} / {a.get('max_volume_db','?')}
silence: {silnote}
```

## User QA request

Please listen and judge whether this works as a BGM/music bed rather than SFX/stinger: continuous, dialogue-friendly, dark romantic fantasy mood, not too busy or too empty.
'''
(unit_dir / 'unit5_bgm_smoke.md').write_text(md, encoding='utf-8')

print('UNIT5_REPORT_MD', unit_dir / 'unit5_bgm_smoke.md')
print('UNIT5_REPORT_JSON', unit_dir / 'unit5_bgm_smoke.json')
print('prompt_id', prompt_id)
print('verified', len(copies))
for p,a in zip(copies, analyses):
    print(p, 'duration', a['duration'], 'mean/max', a['mean_volume_db'], a['max_volume_db'])
