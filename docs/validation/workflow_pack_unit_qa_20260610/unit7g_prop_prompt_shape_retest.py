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
WORKFLOW_PATH = WORKFLOW_ROOT / 'scene_prop_cg/scene_prop_cg_workflow_api.json'
OUTPUT_ROOT = Path('C:/Users/Desktop/Documents/ComfyUI/output')
RUN_DIR = PROJECT_ROOT / 'docs/automation/generation_runs/unit7g_prop_prompt_shape_retest'
CANDIDATE_DIR = PROJECT_ROOT / 'docs/automation/generated_candidates/props/unit7g_prop_prompt_shape_retest'
ENDPOINT = 'http://127.0.0.1:8000'

NEG_BASE = (
    '1girl, 1boy, cropped, out_of_frame, duplicate, close-up, modern, recent, old, oldest, '
    'cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, '
    'ugly, lowres, bad_anatomy, sketch, jpeg_artifacts, signature, watermark, username, '
    'bad_ai-generated, (worst_quality, bad_quality:1.2), fake_text, logo, label, screenshot, '
    'dialogue_box, caption'
)
NEG_PHONE = NEG_BASE + ', logo, icon, app icon, apple logo, user interface, letters, numbers, text, status bar, notification, symbol, cup, glass, drink'
NEG_DOC = NEG_BASE + ', handwriting, writing, text, letters, words, envelope, folded letter, book, printed text, signature, stamp, logo, label'

VARIANTS = [
    {
        'id': 'phone_A_current_wrapper',
        'seed': 360610709,
        'negative': NEG_PHONE,
        'positive': (
            'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, '
            'ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, '
            'smartphone, screen, glass, desk, shadow, BREAK, depth_of_field, BREAK, '
            'plain modern smartphone lying on desk, completely blank black screen, screen turned off, '
            'dark reflection only, no logo, no icons, no app UI, no text'
        ),
    },
    {
        'id': 'phone_B_object_first_compact',
        'seed': 360610709,
        'negative': NEG_PHONE,
        'positive': (
            'plain smartphone, blank black screen, screen turned off, smartphone, screen, glass, desk, shadow, '
            'still_life, object_focus, no_humans, no logo, no icons, no app UI, no text, dark reflection only, '
            'depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution'
        ),
    },
    {
        'id': 'doc_A_current_wrapper',
        'seed': 360610710,
        'negative': NEG_DOC,
        'positive': (
            'masterpiece, best_quality, amazing_quality, 4k, very_aesthetic, high_resolution, '
            'ultra-detailed, absurdres, newest, no_humans, still_life, object_focus, '
            'blank_page, paper, wooden_table, shadow, BREAK, depth_of_field, BREAK, '
            'blank parchment sheet on wooden table, empty paper prop, no writing visible, no handwriting, '
            'not an envelope, simple item cut-in'
        ),
    },
    {
        'id': 'doc_B_object_first_compact',
        'seed': 360610710,
        'negative': NEG_DOC,
        'positive': (
            'blank parchment sheet, empty paper, blank_page, paper, wooden_table, shadow, '
            'still_life, object_focus, no_humans, no writing visible, no handwriting, not an envelope, '
            'simple item cut-in, depth_of_field, masterpiece, best_quality, very_aesthetic, high_resolution'
        ),
    },
]


def submit_prompt(workflow: dict) -> str:
    payload = json.dumps({'prompt': workflow, 'client_id': str(uuid.uuid4())}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT + '/prompt', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8', errors='replace'))
        return data['prompt_id']


def wait_history(prompt_id: str, timeout_s: int = 600) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(ENDPOINT + '/history/' + prompt_id, timeout=10) as r:
                hist = json.loads(r.read().decode('utf-8', errors='replace'))
                if isinstance(hist, dict) and prompt_id in hist:
                    return hist[prompt_id]
        except Exception:
            pass
        time.sleep(3)
    raise TimeoutError(prompt_id)


def output_paths_from_history(history: dict) -> list[Path]:
    paths = []
    for node_out in history.get('outputs', {}).values():
        if not isinstance(node_out, dict):
            continue
        for img in node_out.get('images', []):
            if img.get('type') == 'output' and img.get('filename'):
                paths.append((OUTPUT_ROOT / (img.get('subfolder') or '') / img['filename']).resolve())
    return paths


def main():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    base = json.loads(WORKFLOW_PATH.read_text(encoding='utf-8'))
    results = []
    for i, variant in enumerate(VARIANTS, 1):
        wf = json.loads(json.dumps(base))
        run_id = f"unit7g_{i:02d}_{variant['id']}"
        wf['3']['inputs']['text'] = variant['positive']
        wf['4']['inputs']['text'] = variant['negative']
        wf['5']['inputs']['width'] = 1024
        wf['5']['inputs']['height'] = 576
        wf['6']['inputs']['seed'] = variant['seed']
        wf['6']['inputs']['steps'] = 30
        wf['6']['inputs']['cfg'] = 5.2
        wf['8']['inputs']['filename_prefix'] = f'hermes_vn_prop_cg_smoke/{run_id}'
        patched = RUN_DIR / f'{run_id}_workflow_api.json'
        patched.write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding='utf-8')
        prompt_id = submit_prompt(wf)
        history = wait_history(prompt_id)
        (RUN_DIR / f'{run_id}_history.json').write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')
        copies = []
        for p in output_paths_from_history(history):
            if p.exists():
                dst = CANDIDATE_DIR / f'{run_id}{p.suffix.lower() or ".png"}'
                shutil.copy2(p, dst)
                with Image.open(dst) as im:
                    copies.append({'path': str(dst), 'size': list(im.size), 'format': im.format})
        results.append({
            'variant': variant['id'],
            'prompt_id': prompt_id,
            'seed': variant['seed'],
            'positive': variant['positive'],
            'negative': variant['negative'],
            'copies': copies,
        })
    out = RUN_DIR / 'unit7g_prop_prompt_shape_retest.json'
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
