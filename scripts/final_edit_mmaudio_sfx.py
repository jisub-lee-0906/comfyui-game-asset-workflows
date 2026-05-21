#!/usr/bin/env python3
"""Final-edit MMAudio VN SFX takes into one clean hit/segment.

Input: an 8s-ish MMAudio FLAC/WAV/MP3/etc source take.
Output: short FLAC + Ren'Py-friendly OGG containing the strongest single event.

This is intentionally conservative: it does not call an output production-ready;
it only creates final-edit candidates that still need human listening QA.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import List, Tuple


def run(cmd: List[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def ffprobe_duration(path: Path) -> float:
    p = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ])
    return float(p.stdout.strip())


def decode_mono_wav(src: Path, dst: Path, sr: int = 44100) -> None:
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(sr), "-sample_fmt", "s16", str(dst)])


def frame_rms(samples: List[int], sr: int, frame_ms: float) -> Tuple[List[float], int]:
    frame = max(1, int(sr * frame_ms / 1000.0))
    out: List[float] = []
    for i in range(0, len(samples), frame):
        chunk = samples[i:i+frame]
        if not chunk:
            break
        out.append(math.sqrt(sum(x*x for x in chunk) / len(chunk)) / 32768.0)
    return out, frame


def smooth(vals: List[float], radius: int) -> List[float]:
    if radius <= 0:
        return vals[:]
    out = []
    for i in range(len(vals)):
        lo = max(0, i - radius)
        hi = min(len(vals), i + radius + 1)
        out.append(sum(vals[lo:hi]) / (hi - lo))
    return out


def read_samples(wav_path: Path) -> Tuple[List[int], int]:
    with wave.open(str(wav_path), "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        sw = w.getsampwidth()
        if nch != 1 or sw != 2:
            raise RuntimeError(f"expected mono s16 wav, got channels={nch}, sampwidth={sw}")
        raw = w.readframes(w.getnframes())
    # little-endian signed 16-bit
    return [int.from_bytes(raw[i:i+2], "little", signed=True) for i in range(0, len(raw), 2)], sr


def pick_segment(rms: List[float], frame_sec: float, total_sec: float, *,
                 min_duration: float, max_duration: float, pre: float, post: float,
                 threshold_ratio: float) -> dict:
    if not rms:
        raise RuntimeError("empty audio")
    sm = smooth(rms, radius=2)
    peak_i = max(range(len(sm)), key=lambda i: sm[i])
    peak = sm[peak_i]
    if peak <= 0:
        center = total_sec / 2.0
        return {"start": max(0.0, center - min_duration / 2), "end": min(total_sec, center + min_duration / 2), "peak_sec": center, "peak_rms": peak, "threshold": 0.0}

    threshold = peak * threshold_ratio
    left = peak_i
    right = peak_i
    while left > 0 and sm[left] >= threshold:
        left -= 1
    while right < len(sm) - 1 and sm[right] >= threshold:
        right += 1

    start = max(0.0, left * frame_sec - pre)
    end = min(total_sec, (right + 1) * frame_sec + post)

    # Enforce minimum around peak.
    if end - start < min_duration:
        center = peak_i * frame_sec
        start = max(0.0, center - min_duration / 2.0)
        end = min(total_sec, start + min_duration)
        start = max(0.0, end - min_duration)

    # Enforce maximum around peak if a broad/continuous cue was selected.
    if end - start > max_duration:
        center = peak_i * frame_sec
        start = max(0.0, center - max_duration * 0.45)
        end = min(total_sec, start + max_duration)
        start = max(0.0, end - max_duration)

    return {
        "start": round(start, 3),
        "end": round(end, 3),
        "duration": round(end - start, 3),
        "peak_sec": round(peak_i * frame_sec, 3),
        "peak_rms": round(float(peak), 6),
        "threshold": round(float(threshold), 6),
    }


def export_segment(src: Path, out_base: Path, start: float, duration: float, fade_ms: int, ogg_quality: int) -> Tuple[Path, Path]:
    out_base.parent.mkdir(parents=True, exist_ok=True)
    flac = out_base.with_suffix(".flac")
    ogg = out_base.with_suffix(".ogg")
    fade = max(0.0, fade_ms / 1000.0)
    af = []
    if fade > 0:
        # Short fades prevent clicks without smearing transient timing.
        af = ["-af", f"afade=t=in:st=0:d={fade},afade=t=out:st={max(0.0, duration-fade):.3f}:d={fade}"]
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-t", f"{duration:.3f}", "-i", str(src), "-ac", "1", "-ar", "44100", *af, str(flac)])
    run(["ffmpeg", "-y", "-v", "error", "-i", str(flac), "-ac", "1", "-ar", "44100", "-c:a", "libvorbis", "-q:a", str(ogg_quality), str(ogg)])
    return flac, ogg


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto-final-edit an MMAudio source take into one short SFX hit.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--name", default=None, help="output basename without extension")
    ap.add_argument("--min-duration", type=float, default=0.45)
    ap.add_argument("--max-duration", type=float, default=1.6)
    ap.add_argument("--pre", type=float, default=0.10)
    ap.add_argument("--post", type=float, default=0.25)
    ap.add_argument("--frame-ms", type=float, default=20.0)
    ap.add_argument("--threshold-ratio", type=float, default=0.34)
    ap.add_argument("--fade-ms", type=int, default=8)
    ap.add_argument("--ogg-quality", type=int, default=6)
    args = ap.parse_args()

    src = args.input.expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"input not found: {src}")
    out_dir = args.out_dir or (src.parent / "edited_single_hits")
    base_name = args.name or f"{src.stem}_single_hit"
    out_base = out_dir / base_name

    total = ffprobe_duration(src)
    with tempfile.TemporaryDirectory() as td:
        wav_path = Path(td) / "decode.wav"
        decode_mono_wav(src, wav_path)
        samples, sr = read_samples(wav_path)
        rms, frame = frame_rms(samples, sr, args.frame_ms)
        seg = pick_segment(
            rms, frame / sr, total,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
            pre=args.pre,
            post=args.post,
            threshold_ratio=args.threshold_ratio,
        )

    flac, ogg = export_segment(src, out_base, float(seg["start"]), float(seg["duration"]), args.fade_ms, args.ogg_quality)
    report = {
        "source": str(src),
        "source_duration": round(total, 3),
        "selected": seg,
        "outputs": {"flac": str(flac), "ogg": str(ogg)},
        "note": "auto final-edit candidate; still requires listening QA before production-ready label",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
