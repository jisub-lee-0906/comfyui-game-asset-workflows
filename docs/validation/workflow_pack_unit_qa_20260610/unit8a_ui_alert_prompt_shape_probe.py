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
WORKFLOW_PATH = WORKFLOW_ROOT / 'ui_system_alert_frame/ui_system_alert_frame_workflow_api.json'
OUTPUT_ROOT = Path('C:/Users/Desktop/Documents/ComfyUI/output')
RUN_DIR = PROJECT_ROOT / 'docs/automation/generation_runs/unit8a_ui_alert_prompt_shape_probe'
CANDIDATE_DIR = PROJECT_ROOT / 'docs/automation/generated_candidates/ui/unit8a_ui_alert_prompt_shape_probe'
ENDPOINT = 'http://127.0.0.1:8000'

NEG = (
    'worst quality, low quality, bad quality, lowres, jpeg artifacts, blurry, bad anatomy, bad hands, '
    'missing fingers, extra fingers, extra digits, fewer digits, cropped, very displeasing, artist name, '
    'signature, watermark, text, fake_text, text_focus, english_text, korean_text, logo, label, caption, '
    'speech_bubble, dialogue_options, 1girl, 1boy, people, portrait, glowing_eye, animal, cat, scenery, '
    'indoors, outdoors, city, building, window_(computing), dialogue_box, icon_(computing), emblem, crest, '
    'magic_circle, runes, glyph, circle, red_circle, heart, halo, lens_flare, spotlight, gem, jewel, crystal, '
    'cross, medallion, box, paper, book, empty_picture_frame, picture_frame, photo_frame, painting, painting_(object)'
)

VARIANTS = [
    {
        'id': 'A_minimal_red_gold_border',
        'seed': 260604912,
        'positive': 'masterpiece, best quality, highres, black_background, no_humans, border, red_border, gold_border',
    },
    {
        'id': 'B_minimal_red_gold_border_dark_background',
        'seed': 260604912,
        'positive': 'masterpiece, best quality, highres, black_background, no_humans, border, red_border, gold_border, dark_background',
    },
    {
        'id': 'C_canonical_corner_backdrop',
        'seed': 260604912,
        'positive': 'masterpiece, best quality, amazing quality, very aesthetic, absurdres, highres, newest, game_cg, visual_novel, border, outside_border, red_border, black_border, gold_border, corner, red_theme, black_theme, dark_background, black_background, no_humans',
    },
]


def submit_prompt(workflow: dict) -> str:
    payload = json.dumps({'prompt': workflow, 'client_id': str(uuid.uuid4())}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT + '/prompt', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8', errors='replace'))['prompt_id']


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


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    base = json.loads(WORKFLOW_PATH.read_text(encoding='utf-8'))
    results = []
    for i, variant in enumerate(VARIANTS, 1):
        wf = json.loads(json.dumps(base))
        run_id = f"unit8a_{i:02d}_{variant['id']}"
        wf['3']['inputs']['text'] = variant['positive']
        wf['4']['inputs']['text'] = NEG
        wf['5']['inputs']['width'] = 1024
        wf['5']['inputs']['height'] = 576
        wf['6']['inputs']['seed'] = variant['seed']
        wf['6']['inputs']['steps'] = 30
        wf['6']['inputs']['cfg'] = 3.6
        wf['8']['inputs']['filename_prefix'] = f'hermes_vn_ui_system_alert_frame/{run_id}'
        (RUN_DIR / f'{run_id}_workflow_api.json').write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding='utf-8')
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
        results.append({'variant': variant['id'], 'prompt_id': prompt_id, 'seed': variant['seed'], 'positive': variant['positive'], 'negative': NEG, 'copies': copies})
    (RUN_DIR / 'unit8a_ui_alert_prompt_shape_probe.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
