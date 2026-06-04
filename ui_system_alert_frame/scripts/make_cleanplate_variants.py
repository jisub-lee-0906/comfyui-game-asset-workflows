#!/usr/bin/env python3
"""Create optional review-only cleanplate variants for ui_system_alert_frame candidates.

This is a fallback helper, not the primary route. Prefer pure T2I frame generation first.
It never writes into a Ren'Py game/images directory unless the caller deliberately passes one.
"""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_font(font_path: str | None, size: int):
    if font_path:
        p = Path(font_path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_balanced_cleanplate(src: Image.Image) -> Image.Image:
    im = src.convert("RGBA")
    w, h = im.size
    out = im.copy()
    d = ImageDraw.Draw(out, "RGBA")
    plate = (int(w * 0.08), int(h * 0.10), int(w * 0.92), int(h * 0.78))
    d.rounded_rectangle(plate, radius=10, fill=(10, 2, 8, 246), outline=(225, 178, 64, 230), width=3)
    inner = (plate[0] + 12, plate[1] + 12, plate[2] - 12, plate[3] - 12)
    d.rounded_rectangle(inner, radius=8, outline=(145, 0, 0, 230), width=3)
    strip = (int(w * 0.16), int(h * 0.76), int(w * 0.84), int(h * 0.87))
    d.rounded_rectangle(strip, radius=8, fill=(5, 0, 0, 245), outline=(180, 25, 25, 220), width=2)
    d.rectangle((0, 0, w - 1, h - 1), outline=(255, 0, 0, 245), width=max(4, w // 220))
    return out


def draw_wide_cleanplate(src: Image.Image) -> Image.Image:
    im = src.convert("RGBA")
    w, h = im.size
    out = im.copy()
    d = ImageDraw.Draw(out, "RGBA")
    plate = (int(w * 0.045), int(h * 0.08), int(w * 0.955), int(h * 0.82))
    d.rounded_rectangle(plate, radius=8, fill=(7, 1, 5, 250), outline=(220, 176, 62, 240), width=4)
    d.rounded_rectangle((plate[0] + 12, plate[1] + 12, plate[2] - 12, plate[3] - 12), radius=6, outline=(145, 0, 0, 230), width=3)
    d.rectangle((0, 0, w - 1, h - 1), outline=(255, 0, 0, 240), width=max(4, w // 220))
    return out


def draw_deep_red(src: Image.Image) -> Image.Image:
    out = draw_balanced_cleanplate(src)
    overlay = Image.new("RGBA", out.size, (80, 0, 10, 55))
    return Image.alpha_composite(out, overlay)


def overlay_korean(src: Image.Image, font_path: str | None) -> Image.Image:
    im = src.convert("RGBA")
    d = ImageDraw.Draw(im)
    font = load_font(font_path, max(18, im.width // 34))
    lines = ["SYSTEM ALERT", "남은 수명: 30일", "계약을 제안하시겠습니까?"]
    y = int(im.height * 0.30)
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        x = (im.width - (bbox[2] - bbox[0])) // 2
        d.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 230))
        d.text((x, y), line, font=font, fill=(255, 230, 190, 255))
        y += int(im.height * 0.073)
    return im


def contact_sheet(paths: list[Path], out: Path) -> None:
    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        im.thumbnail((512, 288))
        canvas = Image.new("RGB", (512, 326), "white")
        canvas.paste(im, (0, 20))
        d = ImageDraw.Draw(canvas)
        d.rectangle([0, 0, 511, 19], fill=(30, 30, 30))
        d.text((6, 3), p.name[:68], fill=(255, 255, 255))
        thumbs.append(canvas)
    cols = 2
    rows = (len(thumbs) + 1) // 2
    sheet = Image.new("RGB", (512 * cols, 326 * rows), (220, 220, 220))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * 512, (i // cols) * 326))
    sheet.save(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="Source T2I candidate image")
    ap.add_argument("--outdir", required=True, help="Output directory for review-only variants")
    ap.add_argument("--font", default=None, help="Optional Korean-capable font path")
    args = ap.parse_args()

    source = Path(args.source)
    outdir = Path(args.outdir)
    if not source.exists():
        raise SystemExit(f"missing source: {source}")
    outdir.mkdir(parents=True, exist_ok=True)
    src = Image.open(source)

    outputs = []
    variants = [
        ("V08_production_solid_cleanplate_balanced.png", draw_balanced_cleanplate(src)),
        ("V09_production_solid_cleanplate_wide.png", draw_wide_cleanplate(src)),
        ("V10_production_deep_red_cleanplate.png", draw_deep_red(src)),
    ]
    for name, im in variants:
        p = outdir / name
        im.save(p)
        outputs.append(p)

    preview = outdir / "V08_korean_overlay_QA_preview.png"
    overlay_korean(Image.open(outputs[0]), args.font).save(preview)
    outputs.append(preview)

    sheet = outdir / "cleanplate_contact_sheet.png"
    contact_sheet(outputs, sheet)
    outputs.append(sheet)

    meta = {
        "source": str(source),
        "source_sha256": sha256(source),
        "status": "review_candidate_not_promoted",
        "promotion_allowed": False,
        "route": "optional_fallback_cleanplate_after_pure_t2i_direction_probe",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "outputs": [{"path": str(p), "sha256": sha256(p), "bytes": p.stat().st_size} for p in outputs],
    }
    meta_path = outdir / "cleanplate_metadata.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"metadata": str(meta_path), "outputs": [str(p) for p in outputs]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
