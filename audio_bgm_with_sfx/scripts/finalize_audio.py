#!/usr/bin/env python3
"""Finalize generated audio candidates for Ren'Py."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Self


class AudioFinalizeError(ValueError):
    """Raised when an audio finalization request is invalid."""


class AudioToolError(RuntimeError):
    """Raised when ffmpeg or ffprobe cannot complete a request."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="role", required=True)
    for role in ("bgm", "sfx"):
        command = subparsers.add_parser(role)
        command.add_argument("--input", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--metadata", type=Path)
        command.add_argument("--silence-threshold-db", type=float, default=-45.0)
        command.add_argument("--min-silence-duration", type=float, default=0.25)
        command.add_argument("--target-peak-db", type=float, default=-2.0)
        command.add_argument("--max-input-duration", type=float, default=600.0)
        command.add_argument("--overwrite", action="store_true")
        if role == "bgm":
            command.add_argument("--preview", type=Path)
            command.add_argument("--crossfade", type=float, default=1.0)
            command.add_argument("--target-lufs", type=float, default=-20.0)
        else:
            command.add_argument("--fade-out", type=float, default=0.05)
    return parser


def validate_settings(args: argparse.Namespace) -> None:
    ranges = {
        "silence_threshold_db": (-120.0, 0.0),
        "min_silence_duration": (0.0, 60.0),
        "max_input_duration": (0.0, 3600.0),
    }
    if args.role == "bgm":
        ranges.update(
            {
                "crossfade": (0.0, 60.0),
                "target_lufs": (-70.1, -4.9),
                "target_peak_db": (-9.1, 0.0),
            }
        )
    else:
        ranges.update({"fade_out": (0.0, 60.0), "target_peak_db": (-20.0, 0.0)})
    for name, (minimum, maximum) in ranges.items():
        value = getattr(args, name)
        if not math.isfinite(value) or not minimum < value < maximum:
            raise AudioFinalizeError(
                f"invalid setting --{name.replace('_', '-')}: "
                f"expected {minimum} < value < {maximum}"
            )


def destination_paths(args: argparse.Namespace) -> list[Path]:
    return [
        path
        for path in (args.output, getattr(args, "preview", None), args.metadata)
        if path is not None
    ]


def paths_alias(left: Path, right: Path) -> bool:
    try:
        if left.samefile(right):
            return True
    except (FileNotFoundError, OSError):
        pass

    try:
        parents_alias = left.parent.samefile(right.parent)
    except (FileNotFoundError, OSError):
        try:
            parents_alias = left.parent.resolve(strict=False) == right.parent.resolve(strict=False)
        except (OSError, RuntimeError):
            parents_alias = False
    return parents_alias and left.name.casefold() == right.name.casefold()


def validate_paths(args: argparse.Namespace) -> None:
    if not args.input.exists():
        raise AudioFinalizeError(f"input does not exist: {args.input}")
    if not args.input.is_file():
        raise AudioFinalizeError(f"input is not a regular file: {args.input}")
    if args.output.suffix.lower() != ".ogg":
        raise AudioFinalizeError("output must use the .ogg extension")
    if getattr(args, "preview", None) and args.preview.suffix.lower() != ".ogg":
        raise AudioFinalizeError("preview must use the .ogg extension")
    destinations = destination_paths(args)
    for path in destinations:
        if paths_alias(args.input, path):
            raise AudioFinalizeError(f"destination aliases input: {path}")
        if not path.parent.is_dir():
            raise AudioFinalizeError(f"destination parent is not a directory: {path.parent}")
        if (path.exists() or path.is_symlink()) and not path.is_file():
            raise AudioFinalizeError(f"destination is not a regular file: {path}")
    for index, path in enumerate(destinations):
        for other in destinations[index + 1 :]:
            if paths_alias(path, other):
                raise AudioFinalizeError(f"destination paths alias each other: {path} and {other}")
    if not args.overwrite:
        for path in destinations:
            if path.exists() or path.is_symlink():
                raise AudioFinalizeError(f"destination already exists: {path}")


def run_tool(argv: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise AudioToolError(f"unable to execute {argv[0]}: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        raise AudioToolError(f"{argv[0]} failed: {detail}")
    return result


def ffprobe_facts(path: Path) -> dict[str, Any]:
    result = run_tool(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            (
                "format=format_name,duration,size,bit_rate:"
                "stream=index,codec_type,codec_name,sample_rate,channels,channel_layout"
            ),
            "-of",
            "json",
            str(path),
        ]
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AudioToolError("ffprobe returned invalid JSON") from exc


def audio_duration(facts: dict[str, Any]) -> float:
    streams = [stream for stream in facts.get("streams", []) if stream.get("codec_type") == "audio"]
    if not streams:
        raise AudioFinalizeError("input has no audio stream")
    try:
        duration = float(facts["format"]["duration"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AudioFinalizeError("input duration is unavailable") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise AudioFinalizeError("input duration must be finite and positive")
    return duration


def detect_trim_bounds(
    source: Path, duration: float, threshold_db: float, minimum_duration: float, trim_leading: bool
) -> tuple[float, float]:
    result = run_tool(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(source),
            "-af",
            f"silencedetect=noise={threshold_db}dB:d={minimum_duration}",
            "-f",
            "null",
            "-",
        ]
    )
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.eE+-]+)", result.stderr)]
    ends = [float(value) for value in re.findall(r"silence_end: ([0-9.eE+-]+)", result.stderr)]
    start = 0.0
    if trim_leading and starts and starts[0] <= 0.01 and ends:
        start = min(duration, ends[0])
    end = duration
    if starts:
        last_start = starts[-1]
        unmatched = len(starts) > len(ends)
        reaches_end = bool(ends) and ends[-1] >= duration - 0.05
        if unmatched or reaches_end:
            end = max(start, min(duration, last_start))
    if end - start <= 0:
        raise AudioFinalizeError("silence trimming removed the entire input")
    return start, end


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@contextmanager
def source_snapshot(source_path: Path) -> Iterator[tuple[Path, str]]:
    descriptor, name = tempfile.mkstemp(
        prefix=".finalize-audio-source-", suffix=source_path.suffix
    )
    snapshot = Path(name)
    digest = hashlib.sha256()
    try:
        with source_path.open("rb") as source, os.fdopen(descriptor, "wb") as destination:
            descriptor = -1
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
                destination.write(block)
        snapshot.chmod(0o400)
        yield snapshot, digest.hexdigest()
    finally:
        try:
            if descriptor >= 0:
                os.close(descriptor)
        finally:
            try:
                snapshot.chmod(0o600)
                snapshot.unlink()
            except FileNotFoundError:
                pass


def best_effort_unlink(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


class TemporaryOutputTransaction:
    """Own sibling temporaries until they are committed or preserved for recovery."""

    def __init__(self, *, overwrite: bool) -> None:
        self.overwrite = overwrite
        self.pairs: list[tuple[Path, Path]] = []
        self._temporary_paths: list[Path] = []
        self._preserved_paths: set[Path] = set()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _exc_type: object, _exc: object, _traceback: object) -> None:
        for path in reversed(self._temporary_paths):
            if path not in self._preserved_paths:
                best_effort_unlink(path)

    def temporary(self, destination: Path) -> Path:
        descriptor, name = tempfile.mkstemp(
            prefix=f".{destination.stem}.",
            suffix=f".tmp{destination.suffix}",
            dir=destination.parent,
        )
        path = Path(name)
        self._temporary_paths.append(path)
        try:
            os.close(descriptor)
        except OSError:
            try:
                raise
            finally:
                best_effort_unlink(path)
        return path

    def output(self, destination: Path) -> Path:
        path = self.temporary(destination)
        self.pairs.append((path, destination))
        return path

    def preserve(self, path: Path) -> None:
        self._preserved_paths.add(path)

    def commit(self) -> None:
        atomic_commit(self.pairs, overwrite=self.overwrite)


def sfx_filter(start: float, end: float, fade_out: float) -> str:
    duration = end - start
    fade_start = max(0.0, duration - min(fade_out, duration))
    return (
        f"atrim=start={start:.9f}:end={end:.9f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={fade_start:.9f}:d={min(fade_out, duration):.9f}"
    )


def measure_max_volume(source: Path, audio_filter: str) -> float:
    result = run_tool(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(source),
            "-af",
            f"{audio_filter},volumedetect",
            "-f",
            "null",
            "-",
        ]
    )
    match = re.search(r"max_volume: (-?inf|[0-9.+-]+) dB", result.stderr)
    if not match or match.group(1) == "-inf":
        raise AudioFinalizeError("SFX contains no measurable signal after trimming")
    return float(match.group(1))


def encode_sfx(
    args: argparse.Namespace,
    source: Path,
    start: float,
    end: float,
    output: Path,
    peak_headroom_db: float = 0.0,
) -> None:
    base_filter = (
        f"{sfx_filter(start, end, args.fade_out)},"
        "aformat=sample_rates=48000:channel_layouts=stereo"
    )
    measured_peak = measure_max_volume(source, base_filter)
    encode_peak_db = args.target_peak_db - peak_headroom_db
    gain = encode_peak_db - measured_peak
    limit = 10 ** (encode_peak_db / 20)
    run_tool(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-y",
            "-i",
            str(source),
            "-af",
            f"{base_filter},volume={gain:.6f}dB,alimiter=limit={limit:.9f}:level=false",
            "-vn",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "libvorbis",
            "-q:a",
            "5",
            str(output),
        ]
    )


def parse_loudnorm_measurement(stderr: str) -> dict[str, str]:
    blocks = re.findall(r'\{\s*"input_i".*?\}', stderr, flags=re.DOTALL)
    if not blocks:
        raise AudioToolError("ffmpeg loudnorm measurement is missing")
    try:
        return json.loads(blocks[-1])
    except json.JSONDecodeError as exc:
        raise AudioToolError("ffmpeg loudnorm measurement is invalid JSON") from exc


def finite_measurement_value(measurement: dict[str, str], name: str) -> float:
    try:
        value = float(measurement[name])
    except (KeyError, TypeError, ValueError) as exc:
        raise AudioToolError(f"ffmpeg loudnorm measurement {name} is invalid") from exc
    if not math.isfinite(value):
        raise AudioFinalizeError(f"loudnorm measurement {name} is not finite")
    return value


def measure_loudness(
    source: Path, target_i: float, target_tp: float, *, filter_graph: str | None = None
) -> dict[str, str]:
    loudnorm = f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json"
    if filter_graph is None:
        filter_arguments = ["-af", loudnorm]
    else:
        filter_arguments = [
            "-filter_complex",
            f"{filter_graph};[loop]{loudnorm}[measure]",
            "-map",
            "[measure]",
        ]
    result = run_tool(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(source),
            *filter_arguments,
            "-f",
            "null",
            "-",
        ]
    )
    return parse_loudnorm_measurement(result.stderr)


def encode_bgm(
    args: argparse.Namespace,
    source: Path,
    start: float,
    end: float,
    output: Path,
    peak_headroom_db: float = 0.0,
) -> None:
    duration = end - start
    if args.crossfade * 2 >= duration:
        raise AudioFinalizeError(
            f"crossfade {args.crossfade:.3f}s must be less than half the trimmed duration "
            f"{duration:.3f}s"
        )
    middle_end = duration - args.crossfade
    loop_filter = (
        f"[0:a]atrim=start={start:.9f}:end={end:.9f},asetpts=PTS-STARTPTS,"
        "aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[head][middle][tail];"
        f"[head]atrim=start=0:end={args.crossfade:.9f},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d={args.crossfade:.9f}:curve=qsin[h];"
        f"[middle]atrim=start={args.crossfade:.9f}:end={middle_end:.9f},"
        "asetpts=PTS-STARTPTS[m];"
        f"[tail]atrim=start={middle_end:.9f}:end={duration:.9f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st=0:d={args.crossfade:.9f}:curve=qsin[t];"
        "[t][h]amix=inputs=2:duration=longest:normalize=0,asetpts=PTS-STARTPTS[seam];"
        "[seam][m]concat=n=2:v=0:a=1[loop]"
    )
    encode_peak_db = args.target_peak_db - peak_headroom_db
    measurement = measure_loudness(
        source, args.target_lufs, encode_peak_db, filter_graph=loop_filter
    )
    for name in ("input_i", "input_lra", "input_tp", "input_thresh", "target_offset"):
        finite_measurement_value(measurement, name)
    loudnorm = (
        f"loudnorm=I={args.target_lufs}:TP={encode_peak_db}:LRA=11:"
        f"measured_I={measurement['input_i']}:measured_LRA={measurement['input_lra']}:"
        f"measured_TP={measurement['input_tp']}:"
        f"measured_thresh={measurement['input_thresh']}:"
        f"offset={measurement['target_offset']}:linear=true:print_format=summary"
    )
    filter_graph = f"{loop_filter};[loop]{loudnorm}[out]"
    run_tool(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-y",
            "-i",
            str(source),
            "-filter_complex",
            filter_graph,
            "-map",
            "[out]",
            "-vn",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "libvorbis",
            "-q:a",
            "5",
            str(output),
        ]
    )


def encode_preview(loop: Path, preview: Path) -> None:
    run_tool(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-y",
            "-stream_loop",
            "1",
            "-i",
            str(loop),
            "-map",
            "0:a:0",
            "-vn",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "libvorbis",
            "-q:a",
            "5",
            str(preview),
        ]
    )


def settings_metadata(args: argparse.Namespace) -> dict[str, float]:
    settings = {
        "silence_threshold_db": args.silence_threshold_db,
        "min_silence_duration_seconds": args.min_silence_duration,
        "target_peak_db": args.target_peak_db,
        "max_input_duration_seconds": args.max_input_duration,
    }
    if args.role == "sfx":
        settings["fade_out_seconds"] = args.fade_out
    else:
        settings["crossfade_seconds"] = args.crossfade
        settings["target_lufs"] = args.target_lufs
    return settings


def write_metadata_temp(
    args: argparse.Namespace,
    path: Path,
    source_facts: dict[str, Any],
    source_sha256: str,
    output_temp: Path,
    output_facts: dict[str, Any],
    start: float,
    end: float,
    preview_temp: Path | None = None,
    preview_facts: dict[str, Any] | None = None,
    output_qa: dict[str, float | None] | None = None,
) -> None:
    report = {
        "schema_version": 1,
        "role": args.role,
        "settings": settings_metadata(args),
        "trim": {
            "source_duration_seconds": audio_duration(source_facts),
            "start_seconds": start,
            "end_seconds": end,
            "trimmed_duration_seconds": end - start,
            "output_duration_seconds": audio_duration(output_facts),
        },
        "source": {
            "path": str(args.input),
            "sha256": source_sha256,
            "ffprobe": source_facts,
        },
        "output": {
            "path": str(args.output),
            "sha256": sha256_file(output_temp),
            "ffprobe": output_facts,
        },
    }
    if output_qa is not None:
        report["output"]["qa"] = output_qa
    if preview_temp is not None and preview_facts is not None:
        report["preview"] = {
            "path": str(args.preview),
            "sha256": sha256_file(preview_temp),
            "ffprobe": preview_facts,
        }
    path.write_text(
        json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def atomic_commit(pairs: list[tuple[Path, Path]], *, overwrite: bool) -> None:
    if not overwrite:
        installed_paths: list[Path] = []
        try:
            for temporary, destination in pairs:
                os.link(temporary, destination)
                installed_paths.append(destination)
        except OSError as exc:
            rollback_errors = []
            for destination in reversed(installed_paths):
                try:
                    destination.unlink(missing_ok=True)
                except OSError as rollback_exc:
                    rollback_errors.append(f"partial destination {destination}: {rollback_exc}")
            detail = f"unable to atomically install destinations: {exc}"
            if rollback_errors:
                detail += "; rollback failed: " + " | ".join(rollback_errors)
            raise AudioToolError(detail) from exc
        for temporary, _ in pairs:
            best_effort_unlink(temporary)
        return

    with TemporaryOutputTransaction(overwrite=True) as backup_paths:
        records: list[tuple[Path, Path | None, bool]] = []
        try:
            for temporary, destination in pairs:
                backup = None
                if destination.exists() or destination.is_symlink():
                    backup = backup_paths.temporary(destination)
                    backup.unlink()
                    os.replace(destination, backup)
                records.append((destination, backup, False))
                os.replace(temporary, destination)
                records[-1] = (destination, backup, True)
        except OSError as exc:
            rollback_errors = []
            for destination, backup, installed in reversed(records):
                removal_error = None
                if installed:
                    try:
                        destination.unlink(missing_ok=True)
                    except OSError as rollback_exc:
                        removal_error = rollback_exc
                try:
                    if backup is not None:
                        os.replace(backup, destination)
                    elif removal_error is not None:
                        raise removal_error
                except OSError as rollback_exc:
                    recovery = ""
                    if backup is not None and backup.exists():
                        backup_paths.preserve(backup)
                        recovery = f"; original backup retained at {backup}"
                    rollback_errors.append(f"{destination}: {rollback_exc}{recovery}")
            detail = f"unable to atomically install destinations: {exc}"
            if rollback_errors:
                detail += "; rollback failed: " + " | ".join(rollback_errors)
            raise AudioToolError(detail) from exc


def finalize(args: argparse.Namespace) -> None:
    with TemporaryOutputTransaction(overwrite=args.overwrite) as transaction:
        with source_snapshot(args.input) as (snapshot, source_sha256):
            source_facts = ffprobe_facts(snapshot)
            duration = audio_duration(source_facts)
            if duration > args.max_input_duration:
                raise AudioFinalizeError(
                    f"input duration {duration:.3f}s exceeds maximum {args.max_input_duration:.3f}s"
                )
            start, end = detect_trim_bounds(
                snapshot,
                duration,
                args.silence_threshold_db,
                args.min_silence_duration,
                trim_leading=args.role == "bgm",
            )
            output_temp = transaction.output(args.output)
            preview_temp = (
                transaction.output(args.preview) if getattr(args, "preview", None) else None
            )
            metadata_temp = transaction.output(args.metadata) if args.metadata else None
            if args.role == "sfx":
                peak_headroom_db = 0.0
                for attempt in range(1, 5):
                    encode_sfx(
                        args,
                        snapshot,
                        start,
                        end,
                        output_temp,
                        peak_headroom_db,
                    )
                    measurement = measure_loudness(output_temp, -20.0, args.target_peak_db)
                    measured_true_peak = finite_measurement_value(measurement, "input_tp")
                    if measured_true_peak <= args.target_peak_db:
                        break
                    peak_headroom_db += measured_true_peak - args.target_peak_db + 0.1
                else:
                    raise AudioToolError(
                        "encoded SFX true peak "
                        f"{measured_true_peak:.2f} dBTP exceeds ceiling "
                        f"{args.target_peak_db:.2f} dBTP after {attempt} attempts"
                    )
            else:
                peak_headroom_db = 0.0
                for attempt in range(1, 5):
                    encode_bgm(
                        args,
                        snapshot,
                        start,
                        end,
                        output_temp,
                        peak_headroom_db,
                    )
                    measurement = measure_loudness(
                        output_temp, args.target_lufs, args.target_peak_db
                    )
                    measured_true_peak = finite_measurement_value(measurement, "input_tp")
                    if measured_true_peak <= args.target_peak_db:
                        break
                    peak_headroom_db += measured_true_peak - args.target_peak_db + 0.1
                else:
                    raise AudioToolError(
                        "encoded BGM true peak "
                        f"{measured_true_peak:.2f} dBTP exceeds ceiling "
                        f"{args.target_peak_db:.2f} dBTP after {attempt} attempts"
                    )
            output_facts = ffprobe_facts(output_temp)
            try:
                integrated_lufs = float(measurement["input_i"])
            except (KeyError, TypeError, ValueError):
                integrated_lufs = None
            if integrated_lufs is not None and not math.isfinite(integrated_lufs):
                integrated_lufs = None
            output_qa = {
                "integrated_lufs": integrated_lufs,
                "true_peak_dbtp": measured_true_peak,
            }
            preview_facts = None
            if preview_temp:
                encode_preview(output_temp, preview_temp)
                preview_facts = ffprobe_facts(preview_temp)
            if metadata_temp:
                write_metadata_temp(
                    args,
                    metadata_temp,
                    source_facts,
                    source_sha256,
                    output_temp,
                    output_facts,
                    start,
                    end,
                    preview_temp,
                    preview_facts,
                    output_qa,
                )
        transaction.commit()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validate_paths(args)
    validate_settings(args)
    finalize(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AudioFinalizeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    except AudioToolError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
