#!/usr/bin/env python3
"""Run a low-cost end-to-end smoke test for all canonical workflows."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.workflow_pack import render_workflow, submit_runtime
except ModuleNotFoundError:
    from workflow_pack import render_workflow, submit_runtime


def build_smoke_edits(
    run_id: str, source_input: str, expression_input: str
) -> dict[str, dict[str, Any]]:
    prefix = f"workflow_pack_e2e/{run_id}"
    return {
        "char_base": {
            "3.inputs.text": "masterpiece, best_quality, amazing_quality, 1girl, solo, cowboy_shot, standing, facing_viewer, looking_at_viewer, expressionless, closed_mouth, medium_hair, straight_hair, blunt_bangs, brown_hair, brown_eyes, school_uniform, white_shirt, necktie, pleated_skirt, cardigan, grey_background",
            "5.inputs.width": 512,
            "5.inputs.height": 768,
            "6.inputs.seed": 260526204,
            "6.inputs.steps": 8,
            "6.inputs.cfg": 5.0,
            "8.inputs.filename_prefix": f"{prefix}/char_base",
        },
        "char_expression": {
            "1.inputs.image": source_input,
            "6.inputs.text": "masterpiece, best_quality, amazing_quality, 1girl, solo, medium_breasts, cowboy_shot, standing, facing_viewer, looking_at_viewer, arms_at_sides, medium_hair, straight_hair, brown_hair, brown_eyes, happy, smile, closed_mouth",
            "7.inputs.text": "lowres, bad_anatomy, cropped, jpeg_artifacts, signature, watermark, sad, angry, crying, tears, expressionless",
            "13.inputs.seed": 719251301,
            "13.inputs.steps": 8,
            "13.inputs.cfg": 5.0,
            "13.inputs.denoise": 0.4,
            "19.inputs.filename_prefix": f"{prefix}/char_expression",
        },
        "char_alpha": {
            "1.inputs.image": expression_input,
            "3.inputs.filename_prefix": f"{prefix}/char_alpha",
        },
        "scene_background": {
            "3.inputs.text": "masterpiece, best_quality, amazing_quality, scenery, no_humans, wide_shot, landscape, classroom, desk, window, sunset, sunlight, orange_sky, depth_of_field",
            "5.inputs.width": 768,
            "5.inputs.height": 432,
            "6.inputs.seed": 812345001,
            "6.inputs.steps": 8,
            "6.inputs.cfg": 5.5,
            "8.inputs.filename_prefix": f"{prefix}/scene_background",
        },
        "scene_event_cg": {
            "11.inputs.width": 768,
            "11.inputs.height": 432,
            "12.inputs.seed": 260521401,
            "12.inputs.steps": 8,
            "12.inputs.cfg": 5.2,
            "14.inputs.filename_prefix": f"{prefix}/scene_event_cg",
        },
        "scene_prop_cg": {
            "3.inputs.text": "masterpiece, best_quality, amazing_quality, no_humans, still_life, object_focus, key, scratches, wooden_table, indoors, depth_of_field",
            "5.inputs.width": 768,
            "5.inputs.height": 432,
            "6.inputs.seed": 812348102,
            "6.inputs.steps": 8,
            "6.inputs.cfg": 5.2,
            "8.inputs.filename_prefix": f"{prefix}/scene_prop_cg",
        },
        "ui_system_alert_frame": {
            "5.inputs.width": 768,
            "5.inputs.height": 432,
            "6.inputs.seed": 260604912,
            "6.inputs.steps": 8,
            "6.inputs.cfg": 3.6,
            "8.inputs.filename_prefix": f"{prefix}/ui_system_alert_frame",
        },
        "audio_bgm_with_sfx": {
            "52:31.inputs.value": "A short clean fantasy UI confirmation chime with bright bell attack and soft magical shimmer. Length: 5 seconds",
            "52:7.inputs.text": "voice, speech, lyrics",
            "52:43.inputs.choice": "SFX",
            "52:43.inputs.index": 2,
            "52:36.inputs.value": 5,
            "52:35.inputs.value": False,
            "52:3.inputs.seed": 1038503484137406,
            "52:3.inputs.steps": 4,
            "52:3.inputs.cfg": 1,
            "19.inputs.filename_prefix": f"{prefix}/audio_bgm_with_sfx",
        },
    }


def _copy_to_input(artifact_path: str, input_root: Path, relative_stem: str) -> str:
    source = Path(artifact_path)
    relative = Path(relative_stem).with_suffix(source.suffix)
    destination = (input_root / relative).resolve()
    input_root = input_root.resolve()
    if not destination.is_relative_to(input_root):
        raise ValueError("input destination escapes input root")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return relative.as_posix()


def run_smoke(
    root: Path,
    comfyui_url: str,
    input_root: Path,
    output_root: Path,
    runtime_dir: Path,
    run_id: str,
    timeout: float,
) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", run_id):
        raise ValueError("run_id may contain only letters, digits, dot, underscore, and hyphen")
    plan = build_smoke_edits(run_id, "pending/source.png", "pending/expression.png")
    results: dict[str, Any] = {}

    def execute(workflow_id: str) -> dict[str, Any]:
        rendered = render_workflow(root, workflow_id, plan[workflow_id], runtime_dir)
        submitted = submit_runtime(
            rendered["runtime_path"],
            comfyui_url,
            output_root,
            root=root,
            expected_runtime_sha256=rendered["runtime_sha256"],
            timeout=timeout,
        )
        result = {"render": rendered, "submit": submitted}
        results[workflow_id] = result
        return result

    char_base = execute("char_base")
    source_input = _copy_to_input(
        char_base["submit"]["artifacts"][0]["path"],
        input_root,
        f"workflow_pack_e2e/{run_id}/char_base_source",
    )
    plan["char_expression"]["1.inputs.image"] = source_input
    char_expression = execute("char_expression")
    expression_input = _copy_to_input(
        char_expression["submit"]["artifacts"][0]["path"],
        input_root,
        f"workflow_pack_e2e/{run_id}/char_expression_source",
    )
    plan["char_alpha"]["1.inputs.image"] = expression_input
    execute("char_alpha")

    for workflow_id in (
        "scene_background",
        "scene_event_cg",
        "scene_prop_cg",
        "ui_system_alert_frame",
        "audio_bgm_with_sfx",
    ):
        execute(workflow_id)

    report = {
        "ok": len(results) == 8,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "workflows": results,
    }
    runtime_dir.mkdir(parents=True, exist_ok=True)
    report_path = runtime_dir / f"e2e_{run_id}_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path.resolve())
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8188")
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, default=root / ".runtime")
    parser.add_argument(
        "--run-id", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    parser.add_argument("--timeout", type=float, default=900)
    args = parser.parse_args()
    report = run_smoke(
        root,
        args.url,
        args.input_root,
        args.output_root,
        args.runtime_dir,
        args.run_id,
        args.timeout,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
