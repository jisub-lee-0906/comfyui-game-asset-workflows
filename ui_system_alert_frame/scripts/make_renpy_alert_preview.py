#!/usr/bin/env python3
"""Create a deterministic Ren'Py top-left alert overlay preview."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

MAX_DISPLAY_PIXELS = 20_000_000
MAX_SOURCE_PIXELS = 20_000_000
TEXT_HORIZONTAL_PADDING = 50
TEXT_VERTICAL_PADDING = 24


def _positive_size(size: tuple[int, int], name: str) -> tuple[int, int]:
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError(f"{name} dimensions must be positive")
    return width, height


def _validate_box(box: tuple[int, int, int, int], display_size: tuple[int, int], name: str) -> None:
    left, top, right, bottom = box
    width, height = display_size
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f"{name} must fit inside the display")


def _intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def _load_font(font_path: Path | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if font_path is None:
        return ImageFont.load_default(size=size)
    if not font_path.is_file():
        raise ValueError(f"font does not exist: {font_path}")
    try:
        return ImageFont.truetype(str(font_path), size)
    except OSError as exc:
        raise ValueError(f"font cannot be loaded: {font_path}") from exc


def _load_source(path: Path, target_size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        if source.width * source.height > MAX_SOURCE_PIXELS:
            raise ValueError("source image exceeds maximum pixel count")
        return source.convert("RGBA").resize(target_size, Image.Resampling.LANCZOS)


def _save_output(image: Image.Image, output_path: Path, overwrite: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent,
            prefix=f".{output_path.stem}-",
            suffix=output_path.suffix,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        image.save(temporary_path)
        if overwrite:
            os.replace(temporary_path, output_path)
        else:
            os.link(temporary_path, output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _split_oversized_word(draw: ImageDraw.ImageDraw, word: str, font, max_width: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for character in word:
        proposed = current + character
        if current and draw.textlength(proposed, font=font) > max_width:
            chunks.append(current)
            current = character
        else:
            current = proposed
    if current:
        chunks.append(current)
    return chunks


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words: list[str] = []
    for word in text.split():
        if draw.textlength(word, font=font) <= max_width:
            words.append(word)
        else:
            words.extend(_split_oversized_word(draw, word, font, max_width))

    lines: list[str] = []
    current = ""
    for word in words:
        proposed = word if not current else f"{current} {word}"
        if draw.textlength(proposed, font=font) <= max_width:
            current = proposed
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_alert_preview(
    frame_path: Path,
    background_path: Path,
    output_path: Path,
    *,
    message: str,
    font_path: Path | None = None,
    display_size: tuple[int, int] = (1920, 1080),
    panel_size: tuple[int, int] = (720, 240),
    margin: tuple[int, int] = (48, 48),
    protected_box: tuple[int, int, int, int] | None = None,
    panel_opacity: int = 245,
    font_size: int = 34,
    max_lines: int = 3,
    overwrite: bool = False,
) -> dict:
    display_width, display_height = _positive_size(display_size, "display")
    panel_width, panel_height = _positive_size(panel_size, "panel")
    frame_path = Path(frame_path)
    background_path = Path(background_path)
    output_path = Path(output_path)
    resolved_output = output_path.resolve()
    input_paths = (frame_path, background_path)
    same_input = resolved_output in {path.resolve() for path in input_paths}
    if output_path.exists():
        same_input = same_input or any(output_path.samefile(path) for path in input_paths)
    if same_input:
        raise ValueError("output must not overwrite an input image")
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {output_path}")
    margin_x, margin_y = margin
    if display_width * display_height > MAX_DISPLAY_PIXELS:
        raise ValueError("display exceeds maximum pixel count")
    if margin_x < 0 or margin_y < 0:
        raise ValueError("margins must be non-negative")
    panel_box = (margin_x, margin_y, margin_x + panel_width, margin_y + panel_height)
    _validate_box(panel_box, display_size, "panel box")
    if not message.strip():
        raise ValueError("message must not be empty")
    if font_path is None and not message.isascii():
        raise ValueError("non-ASCII text requires an explicit font")
    if not 1 <= panel_opacity <= 255:
        raise ValueError("panel opacity must be between 1 and 255")
    if font_size <= 0 or max_lines <= 0:
        raise ValueError("font size and max lines must be positive")

    intersection = False
    if protected_box is not None:
        _validate_box(protected_box, display_size, "protected box")
        intersection = _intersects(panel_box, protected_box)
        if intersection:
            raise ValueError("alert panel intersects protected content")

    background = _load_source(background_path, display_size)
    panel = _load_source(frame_path, panel_size)
    if panel_opacity < 255:
        alpha = panel.getchannel("A").point(lambda value: value * panel_opacity // 255)
        panel.putalpha(alpha)
    background.alpha_composite(panel, (margin_x, margin_y))

    draw = ImageDraw.Draw(background)
    font = _load_font(font_path, font_size)
    max_text_width = panel_width - 2 * TEXT_HORIZONTAL_PADDING
    if max_text_width <= 0:
        raise ValueError("text does not fit inside panel padding")
    lines = wrap_text(draw, message.strip(), font, max_text_width)
    if not lines or len(lines) > max_lines:
        raise ValueError(f"message requires {len(lines)} lines; maximum is {max_lines}")
    if any(draw.textlength(line, font=font) > max_text_width for line in lines):
        raise ValueError("text does not fit inside panel padding")
    line_height = max(font_size + 14, int(panel_height * 0.20))
    total_height = len(lines) * line_height
    if total_height > panel_height - 2 * TEXT_VERTICAL_PADDING:
        raise ValueError("text does not fit inside panel padding")
    y = margin_y + (panel_height - total_height) // 2
    for line in lines:
        text_width = draw.textlength(line, font=font)
        x = margin_x + (panel_width - text_width) / 2
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 230))
        draw.text((x, y), line, font=font, fill=(255, 232, 198, 255))
        y += line_height

    _save_output(background.convert("RGB"), output_path, overwrite)
    return {
        "output": str(output_path),
        "display_size": [display_width, display_height],
        "presentation_mode": "top_left_nonmodal",
        "panel_box": list(panel_box),
        "protected_box": list(protected_box) if protected_box is not None else None,
        "protected_box_intersection": intersection,
        "message_lines": lines,
        "panel_opacity": panel_opacity,
    }


def _parse_pair(value: str) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("expected WIDTH,HEIGHT")
    return int(parts[0]), int(parts[1])


def _parse_box(value: str) -> tuple[int, int, int, int]:
    parts = value.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("expected LEFT,TOP,RIGHT,BOTTOM")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frame", type=Path)
    parser.add_argument("background", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--message", required=True)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--display-size", type=_parse_pair, default=(1920, 1080))
    parser.add_argument("--panel-size", type=_parse_pair, default=(720, 240))
    parser.add_argument("--margin", type=_parse_pair, default=(48, 48))
    parser.add_argument("--protected-box", type=_parse_box)
    parser.add_argument("--panel-opacity", type=int, default=245)
    parser.add_argument("--font-size", type=int, default=34)
    parser.add_argument("--max-lines", type=int, default=3)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = render_alert_preview(
        args.frame,
        args.background,
        args.output,
        message=args.message,
        font_path=args.font,
        display_size=args.display_size,
        panel_size=args.panel_size,
        margin=args.margin,
        protected_box=args.protected_box,
        panel_opacity=args.panel_opacity,
        font_size=args.font_size,
        max_lines=args.max_lines,
        overwrite=args.overwrite,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
