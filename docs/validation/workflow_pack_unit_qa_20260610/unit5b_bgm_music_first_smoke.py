from __future__ import annotations
from pathlib import Path
import json, shutil, subprocess, time, urllib.request, uuid, re

root=Path('E:/workspace/comfyui-game-asset-workflows')
report_dir=root/'docs/validation/workflow_pack_unit_qa_20260610'
unit_dir=report_dir/'unit5b_bgm_music_first_smoke'
runtime_dir=unit_dir/'runtime_payloads'
candidate_dir=unit_dir/'candidates'
for p in [runtime_dir,candidate_dir]: p.mkdir(parents=True, exist_ok=True)
endpoint='http://127.0.0.1:8000'
output_root=Path('C:/Users/Desktop/Documents/ComfyUI/output')
workflow_path=root/'audio_bgm_with_sfx/audio_bgm_with_sfx_workflow_api.json'
base=json.loads(workflow_path.read_text(encoding='utf-8'))
MODE_INDEX={'Music':0,'Instrument':1,'SFX':2,'One-shot':3}
scenarios=[
  {
    'id':'bgm_music_first_minor_waltz',
    'label':'A_music_first_minor_waltz',
    'intent':'music-first dark romantic fantasy dialogue BGM; waltz pulse',
    'prompt':'Soft felt piano and low strings, slow minor waltz, dark romantic fantasy, quiet dialogue underscore.',
    'duration':24.0,
    'seed':360610511,
  },
  {
    'id':'bgm_music_first_nocturne',
    'label':'B_music_first_nocturne',
    'intent':'music-first melancholic noble fantasy BGM; less waltz, more nocturne',
    'prompt':'Felt piano nocturne, warm cello sustain, sparse harp, melancholic noble fantasy, quiet background music.',
    'duration':24.0,
    'seed':360610512,
  },
]

def submit(wf):
    payload=json.dumps({'prompt':wf,'client_id':str(uuid.uuid4())}).encode('utf-8')
    req=urllib.request.Request(endpoint+'/prompt',data=payload,headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))['prompt_id']

def wait(pid):
    deadline=time.time()+600
    while time.time()<deadline:
        with urllib.request.urlopen(endpoint+'/history/'+pid,timeout=10) as r:
            hist=json.load(r)
        item=hist.get(pid)
        if isinstance(item,dict) and item.get('outputs'): return item
        time.sleep(3)
    raise TimeoutError(pid)

def paths_from_history(h):
    paths=[]
    for out in h.get('outputs',{}).values():
        if not isinstance(out,dict): continue
        for key in ['audios','audio']:
            entries=out.get(key,[])
            if isinstance(entries,dict): entries=[entries]
            for item in entries or []:
                if isinstance(item,dict) and item.get('type','output')=='output' and item.get('filename'):
                    paths.append((output_root/str(item.get('subfolder') or '').replace('\\','/')/item['filename']).resolve())
    return paths

def run(cmd): return subprocess.run(cmd,text=True,capture_output=True)
def analyze(p):
    probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration,bit_rate,size:stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(p)]).stdout)
    vol=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af','volumedetect','-f','null','-']).stderr
    mean=maxv=None
    for line in vol.splitlines():
        if 'mean_volume' in line:
            m=re.search(r'mean_volume: ([\-0-9.]+)',line); mean=float(m.group(1)) if m else None
        if 'max_volume' in line:
            m=re.search(r'max_volume: ([\-0-9.]+)',line); maxv=float(m.group(1)) if m else None
    sil=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af','silencedetect=noise=-45dB:d=1.0','-f','null','-']).stderr
    return {'ffprobe':probe,'duration':float(probe['format']['duration']),'sample_rate':probe['streams'][0].get('sample_rate'),'channels':probe['streams'][0].get('channels'),'mean_volume_db':mean,'max_volume_db':maxv,'silencedetect_-45dB_d1.0':[line for line in sil.splitlines() if 'silence_' in line]}

results=[]
for sc in scenarios:
    wf=json.loads(json.dumps(base))
    wf['52:31']['inputs']['value']=sc['prompt']
    wf['52:7']['inputs']['text']=''
    wf['52:43']['inputs']['choice']='Music'; wf['52:43']['inputs']['index']=MODE_INDEX['Music']
    wf['52:36']['inputs']['value']=sc['duration']
    wf['52:35']['inputs']['value']=False
    wf['52:3']['inputs']['seed']=sc['seed']; wf['52:3']['inputs']['steps']=8; wf['52:3']['inputs']['cfg']=1.0
    wf['52:3']['inputs']['sampler_name']='lcm'; wf['52:3']['inputs']['scheduler']='simple'
    wf['19']['inputs']['filename_prefix']=f'workflow_pack_unit5b/{sc["id"]}'
    runtime_path=runtime_dir/f'{sc["id"]}_workflow_api.json'
    runtime_path.write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pid=submit(wf); hist=wait(pid)
    hist_path=runtime_dir/f'{sc["id"]}_history.json'
    hist_path.write_text(json.dumps(hist,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    copies=[]; analyses=[]
    for i,p in enumerate(paths_from_history(hist),1):
        if p.exists():
            dst=candidate_dir/f'{sc["label"]}_candidate_{i:02d}{p.suffix.lower() or ".mp3"}'
            shutil.copy2(p,dst); copies.append(dst); analyses.append(analyze(dst))
    results.append({**sc,'workflow_id':'audio_bgm_with_sfx','mode':'Music','negative':'','runtime_path':str(runtime_path),'prompt_id':pid,'history_path':str(hist_path),'candidate_copies':[str(x) for x in copies],'analyses':analyses,'verified_output_count':len(copies)})

summary={'unit':'Unit 5B — BGM music-first prompt smoke','endpoint':endpoint,'workflow_path':str(workflow_path),'prompting_rule':'music identity first; concise prompt; negative blank','no_promotion':True,'results':results,'errors':[r['id'] for r in results if r['verified_output_count']==0]}
(unit_dir/'unit5b_bgm_music_first_smoke.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# Unit 5B — BGM Music-first Prompt Smoke\n\n','## Scope\n\n','Retest BGM with shorter prompts that put musical identity first. Two candidates, no promotion.\n\n',f'- Endpoint: `{endpoint}`\n',f'- Workflow: `{workflow_path}`\n',f'- Candidate directory: `{candidate_dir}`\n\n','## Results\n\n','| ID | prompt | seed | prompt_id | duration | mean/max dB | silence | file |\n','|---|---|---:|---|---:|---:|---|---|\n']
for r in results:
    a=r['analyses'][0] if r['analyses'] else {}
    sil='; '.join((a.get('silencedetect_-45dB_d1.0') or [])[:2]) or 'none'
    file=r['candidate_copies'][0] if r['candidate_copies'] else 'NO VERIFIED OUTPUT'
    md.append(f"| `{r['label']}` | `{r['prompt']}` | {r['seed']} | `{r['prompt_id']}` | {a.get('duration','?')} | {a.get('mean_volume_db','?')} / {a.get('max_volume_db','?')} | {sil} | `{file}` |\n")
md.append('\n## User QA request\n\nPlease compare these against Unit 5. Judge whether putting musical identity first improves the BGM direction, and which of A/B is closer.\n')
(unit_dir/'unit5b_bgm_music_first_smoke.md').write_text(''.join(md),encoding='utf-8')
print('UNIT5B_REPORT_MD',unit_dir/'unit5b_bgm_music_first_smoke.md')
print('UNIT5B_REPORT_JSON',unit_dir/'unit5b_bgm_music_first_smoke.json')
for r in results:
    print(r['label'], 'prompt_id', r['prompt_id'], 'verified', r['verified_output_count'])
    for p,a in zip(r['candidate_copies'],r['analyses']): print(' ',p,'duration',a['duration'],'mean/max',a['mean_volume_db'],a['max_volume_db'])
