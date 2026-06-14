from __future__ import annotations

import json
import shutil
import time
import urllib.request
import uuid
from pathlib import Path

from PIL import Image

WORKFLOW_ROOT = Path('E:/workspace/comfyui-game-asset-workflows')
PROJECT_ROOT = Path('E:/workspace/renpy-project/sihanbu_villainess_badend')
WORKFLOW_PATH = WORKFLOW_ROOT / 'char_base/char_base_workflow_api.json'
OUTPUT_ROOT = Path('C:/Users/Desktop/Documents/ComfyUI/output')
RUN_ROOT = PROJECT_ROOT / 'docs/automation/generation_runs/unit9d_prime_char_base_prompt_policy'
CANDIDATE_ROOT = PROJECT_ROOT / 'docs/automation/generated_candidates/characters/unit9d_prime_char_base_prompt_policy'
ENDPOINT = 'http://127.0.0.1:8000'
SEED = 260529202

BASE_NEG = (
    'modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, '
    'abstract, glitch, deformed, mutated, ugly, disfigured, long_body, lowres, '
    'bad_anatomy, bad_hands, missing_fingers, extra_digits, fewer_digits, cropped, '
    'close-up, very_displeasing, sketch, jpeg_artifacts, signature, watermark, username, '
    'conjoined, bad_ai-generated, (worst_quality, bad_quality:1.2), shadow, depth_of_field'
)

QUALITY = 'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, ultra-detailed, absurdres, newest'
FEATURES = 'medium_hair, straight_hair, blunt_bangs, brown_hair, brown_eyes, tareme'
POSE = '1girl, solo, cowboy_shot, standing, facing_viewer, looking_at_viewer, expressionless, closed_mouth, arms_at_sides'

VARIANTS = [
    {
        'id': 'A_baseline_medium_breasts_cardigan',
        'positive': f'{QUALITY}, {POSE}, medium_breasts, {FEATURES}, school_uniform, white_shirt, brown_cardigan, blue_skirt, brown_pantyhose, grey_background',
        'negative': BASE_NEG,
    },
    {
        'id': 'B_small_breasts_red_necktie_no_badge',
        'positive': f'{QUALITY}, {POSE}, small_breasts, {FEATURES}, school_uniform, white_shirt, brown_cardigan, red_necktie, blue_skirt, brown_pantyhose, grey_background',
        'negative': BASE_NEG + ', badge, emblem, crest, school_emblem, bow, ribbon',
    },
    {
        'id': 'C_no_breast_size_red_necktie_no_badge',
        'positive': f'{QUALITY}, {POSE}, {FEATURES}, school_uniform, white_shirt, brown_cardigan, red_necktie, blue_skirt, brown_pantyhose, grey_background',
        'negative': BASE_NEG + ', badge, emblem, crest, school_emblem, bow, ribbon, large_breasts, huge_breasts',
    },
    {
        'id': 'D_blazer_red_necktie_no_cardigan',
        'positive': f'{QUALITY}, {POSE}, small_breasts, {FEATURES}, school_uniform, white_shirt, blazer, red_necktie, blue_skirt, brown_pantyhose, grey_background',
        'negative': BASE_NEG + ', badge, emblem, crest, school_emblem, bow, ribbon, cardigan',
    },
]


def url_json(url: str, timeout: float = 5.0):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        body = r.read().decode('utf-8', errors='replace')
        return r.status, json.loads(body) if body else None


def submit(workflow: dict) -> str:
    payload = json.dumps({'prompt': workflow, 'client_id': str(uuid.uuid4())}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT + '/prompt', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8'))
        return data['prompt_id']


def wait(prompt_id: str) -> dict:
    deadline = time.time() + 600
    while time.time() < deadline:
        try:
            status, hist = url_json(ENDPOINT + '/history/' + prompt_id, timeout=10)
            if status == 200 and isinstance(hist, dict) and prompt_id in hist:
                return hist[prompt_id]
        except Exception:
            pass
        time.sleep(3)
    raise TimeoutError(prompt_id)


def outputs(history: dict) -> list[Path]:
    found = []
    for node_out in history.get('outputs', {}).values():
        if not isinstance(node_out, dict):
            continue
        for img in node_out.get('images', []):
            if img.get('type') == 'output' and img.get('filename'):
                found.append((OUTPUT_ROOT / (img.get('subfolder') or '') / img['filename']).resolve())
    return found


def main():
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    CANDIDATE_ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for i, v in enumerate(VARIANTS, 1):
        workflow = json.loads(WORKFLOW_PATH.read_text(encoding='utf-8'))
        workflow['3']['inputs']['text'] = v['positive']
        workflow['4']['inputs']['text'] = v['negative']
        workflow['5']['inputs']['width'] = 1152
        workflow['5']['inputs']['height'] = 1536
        workflow['6']['inputs']['seed'] = SEED
        workflow['6']['inputs']['steps'] = 28
        workflow['6']['inputs']['cfg'] = 5.0
        prefix = f'hermes_vn_char_base/unit9d_prime_{i:02d}_{v["id"]}_seed{SEED}'
        workflow['8']['inputs']['filename_prefix'] = prefix
        patched = RUN_ROOT / f'unit9d_prime_{i:02d}_{v["id"]}.json'
        patched.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding='utf-8')
        prompt_id = submit(workflow)
        hist = wait(prompt_id)
        (RUN_ROOT / f'history_{i:02d}_{v["id"]}.json').write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding='utf-8')
        copied = []
        for p in outputs(hist):
            print('OUTPUT', v['id'], p, p.exists())
            if p.exists():
                dst = CANDIDATE_ROOT / f'unit9d_prime_{i:02d}_{v["id"]}.png'
                shutil.copy2(p, dst)
                with Image.open(dst) as im:
                    copied.append({'path': str(dst), 'size': list(im.size)})
        records.append({**v, 'seed': SEED, 'prompt_id': prompt_id, 'patched_workflow': str(patched), 'outputs': copied})
    metadata = {'unit': '9D-prime', 'purpose': 'char_base prompt policy refinement', 'variants': records}
    (RUN_ROOT / 'unit9d_prime_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(RUN_ROOT / 'unit9d_prime_metadata.json')


if __name__ == '__main__':
    main()
