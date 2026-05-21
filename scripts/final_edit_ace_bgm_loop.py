#!/usr/bin/env python3
"""Final-edit ACE-Step BGM candidates for Ren'Py loop use.

Input: ACE-Step MP3/WAV/FLAC/etc candidate.
Output:
  - trimmed/faded FLAC master
  - Ren'Py-friendly OGG
  - optional two-repeat preview to hear the loop seam

This does not magically make every generated song seamless. It removes leading/trailing
silence, applies a short fade-in and longer fade-out, and produces a loop-preview file
so the seam can be listening-QA'd before promotion.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def run(cmd: List[str], *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ffprobe_duration(path: Path) -> float:
    p = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ])
    return float(p.stdout.strip())


def detect_silence(path: Path, noise: str, min_silence: float) -> Tuple[List[Tuple[float, float]], str]:
    p = run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
        "-af", f"silencedetect=noise={noise}:d={min_silence}",
        "-f", "null", "-"
    ], check=False)
    text = p.stderr
    starts: List[float] = []
    ranges: List[Tuple[float, float]] = []
    for line in text.splitlines():
        m = re.search(r"silence_start: ([0-9.]+)", line)
        if m:
            starts.append(float(m.group(1)))
        m = re.search(r"silence_end: ([0-9.]+)", line)
        if m:
            end = float(m.group(1))
            start = starts.pop(0) if starts else 0.0
            ranges.append((start, end))
    return ranges, text


def choose_trim(duration: float, silence_ranges: List[Tuple[float, float]], pad_start: float, pad_end: float, min_keep: float, merge_gap: float) -> Tuple[float, float]:
    start = 0.0
    end = duration
    # Leading silence that starts near 0.
    for a, b in silence_ranges:
        if a <= 0.10 and b > start:
            start = min(duration, b)
            break
    # Trailing silence cluster that reaches file end. ACE can produce a near-silent
    # tail with tiny residual blips; merge close silence ranges so we cut at the
    # first silence_start of that tail instead of preserving mostly-dead audio.
    trailing_start: Optional[float] = None
    last_a: Optional[float] = None
    last_b: Optional[float] = None
    for a, b in reversed(silence_ranges):
        if trailing_start is None:
            if b >= duration - 0.25:
                trailing_start = a
                last_a, last_b = a, b
            continue
        assert last_a is not None
        gap = last_a - b
        if gap <= merge_gap:
            trailing_start = a
            last_a, last_b = a, b
        else:
            break
    if trailing_start is not None:
        end = max(0.0, trailing_start)
    start = max(0.0, start - pad_start)
    end = min(duration, end + pad_end)
    if end - start < min_keep:
        # Too aggressive / silence detector failed weirdly; keep source.
        return 0.0, duration
    return start, end


def make_outputs(src: Path, out_base: Path, start: float, length: float, fade_in: float, fade_out: float, ogg_quality: int, preview: bool) -> dict:
    out_base.parent.mkdir(parents=True, exist_ok=True)
    flac = out_base.with_suffix(".flac")
    ogg = out_base.with_suffix(".ogg")
    preview_ogg = out_base.with_name(out_base.name + "_loop_preview_2x").with_suffix(".ogg")

    fade_out = max(0.0, min(fade_out, max(0.0, length - fade_in - 0.1)))
    filters = ["aformat=sample_fmts=s16:sample_rates=44100:channel_layouts=stereo"]
    if fade_in > 0:
        filters.append(f"afade=t=in:st=0:d={fade_in:.3f}")
    if fade_out > 0:
        filters.append(f"afade=t=out:st={max(0.0, length - fade_out):.3f}:d={fade_out:.3f}")
    af = ",".join(filters)

    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{length:.3f}", "-i", str(src), "-af", af, str(flac)])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(flac), "-c:a", "libvorbis", "-q:a", str(ogg_quality), str(ogg)])
    result = {"flac": str(flac), "ogg": str(ogg)}
    if preview:
        # Preview only: two repeats with no gap. This lets QA hear end->start seam.
        run([
            "ffmpeg", "-y", "-v", "error",
            "-stream_loop", "1", "-i", str(ogg),
            "-t", f"{length * 2:.3f}",
            "-c:a", "libvorbis", "-q:a", str(ogg_quality), str(preview_ogg)
        ])
        result["loop_preview_2x_ogg"] = str(preview_ogg)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Trim silence and fade ACE-Step BGM for Ren'Py loop use.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--name", default=None, help="output basename without extension")
    ap.add_argument("--noise", default="-45dB", help="silencedetect threshold")
    ap.add_argument("--min-silence", type=float, default=0.8)
    ap.add_argument("--pad-start", type=float, default=0.05)
    ap.add_argument("--pad-end", type=float, default=0.05)
    ap.add_argument("--min-keep", type=float, default=8.0)
    ap.add_argument("--merge-gap", type=float, default=0.75, help="merge near-tail silence ranges separated by tiny residual blips")
    ap.add_argument("--fade-in", type=float, default=0.15)
    ap.add_argument("--fade-out", type=float, default=2.0)
    ap.add_argument("--ogg-quality", type=int, default=5)
    ap.add_argument("--no-preview", action="store_true")
    args = ap.parse_args()

    src = args.input.expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"input not found: {src}")
    out_dir = args.out_dir or (src.parent / "edited_loops")
    out_base = out_dir / (args.name or f"{src.stem}_loop_edit")

    dur = ffprobe_duration(src)
    silences, _ = detect_silence(src, args.noise, args.min_silence)
    start, end = choose_trim(dur, silences, args.pad_start, args.pad_end, args.min_keep, args.merge_gap)
    length = end - start
    outputs = make_outputs(src, out_base, start, length, args.fade_in, args.fade_out, args.ogg_quality, not args.no_preview)

    report = {
        "source": str(src),
        "source_duration": round(dur, 3),
        "silence_ranges": [[round(a, 3), round(b, 3)] for a, b in silences],
        "selected": {"start": round(start, 3), "end": round(end, 3), "duration": round(length, 3)},
        "edits": {"fade_in": args.fade_in, "fade_out": min(args.fade_out, max(0.0, length - args.fade_in - 0.1)), "ogg_quality": args.ogg_quality},
        "outputs": outputs,
        "note": "loop-edit candidate; listen to loop_preview_2x_ogg seam before production promotion",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
