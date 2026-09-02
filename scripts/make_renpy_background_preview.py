#!/usr/bin/env python3
"""Create a deterministic Ren'Py staging preview for a background candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def _positive_size(size: tuple[int, int]) -> tuple[int, int]:
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError("display dimensions must be positive")
    return width, height


def _fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize without distortion, then center-crop to the target display."""
    target_width, target_height = _positive_size(size)
    scale = max(target_width / image.width, target_height / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_width) // 2
    top = (resized.height - target_height) // 2
    return resized.crop((left, top, left + target_width, top + target_height))


def render_preview(
    background_path: Path,
    output_path: Path,
    *,
    character_path: Path | None = None,
    display_size: tuple[int, int] = (1920, 1080),
    textbox_fraction: float = 0.28,
    character_height_fraction: float = 0.94,
) -> dict[str, object]:
    """Render a background, optional sprite, and bottom textbox safe area."""
    display_width, display_height = _positive_size(display_size)
    if not 0 < textbox_fraction < 1:
        raise ValueError("textbox_fraction must be between 0 and 1")
    if not 0 < character_height_fraction <= 1:
        raise ValueError("character_height_fraction must be between 0 and 1")

    with Image.open(background_path) as source:
        source_size = source.size
        canvas = _fit_cover(source.convert("RGBA"), display_size)

    character_box: list[int] | None = None
    if character_path is not None:
        with Image.open(character_path) as source_character:
            character = source_character.convert("RGBA")
        alpha_box = character.getchannel("A").getbbox()
        if alpha_box is None:
            raise ValueError("character image has no visible alpha content")
        character = character.crop(alpha_box)
        target_height = max(1, round(display_height * character_height_fraction))
        target_width = max(1, round(character.width * target_height / character.height))
        if target_width > display_width:
            target_width = display_width
            target_height = max(1, round(character.height * target_width / character.width))
        character = character.resize((target_width, target_height), Image.Resampling.LANCZOS)
        left = (display_width - target_width) // 2
        top = display_height - target_height
        canvas.alpha_composite(character, (left, top))
        character_box = [left, top, left + target_width, top + target_height]

    textbox_top = round(display_height * (1 - textbox_fraction))
    margin_x = round(display_width * 0.035)
    margin_bottom = round(display_height * 0.035)
    radius = max(8, round(display_height * 0.018))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle(
        (margin_x, textbox_top, display_width - margin_x, display_height - margin_bottom),
        radius=radius,
        fill=(12, 16, 25, 218),
        outline=(230, 235, 245, 225),
        width=max(1, round(display_height / 540)),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)
    result: dict[str, object] = {
        "output": str(output_path),
        "background_source_size": list(source_size),
        "display_size": [display_width, display_height],
        "renpy_scale_exact": display_width * source_size[1] == display_height * source_size[0],
        "textbox_fraction": textbox_fraction,
        "textbox_top": textbox_top,
        "character_box": character_box,
    }
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("background", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--character", type=Path)
    parser.add_argument("--display-width", type=int, default=1920)
    parser.add_argument("--display-height", type=int, default=1080)
    parser.add_argument("--textbox-fraction", type=float, default=0.28)
    parser.add_argument("--character-height-fraction", type=float, default=0.94)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = render_preview(
        args.background,
        args.output,
        character_path=args.character,
        display_size=(args.display_width, args.display_height),
        textbox_fraction=args.textbox_fraction,
        character_height_fraction=args.character_height_fraction,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
