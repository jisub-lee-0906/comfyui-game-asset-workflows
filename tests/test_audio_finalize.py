import argparse
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from unittest import mock

from audio_bgm_with_sfx.scripts import finalize_audio

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "audio_bgm_with_sfx" / "scripts" / "finalize_audio.py"


def run_cli(*arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def make_wave(
    path: Path,
    segments: list[tuple[float, float]],
    rate: int = 44100,
    frequency: float = 440.0,
) -> None:
    samples = bytearray()
    phase = 0
    for duration, amplitude in segments:
        for _ in range(round(duration * rate)):
            value = round(amplitude * 32767 * math.sin(2 * math.pi * frequency * phase / rate))
            samples.extend(struct.pack("<h", value))
            phase += 1
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(samples)


def make_transient_wave(path: Path, rate: int = 44100) -> None:
    frame_count = rate * 6
    samples = [round(4000 * math.sin(2 * math.pi * 997 * frame / rate)) for frame in range(frame_count)]
    burst_start = frame_count // 2
    samples[burst_start : burst_start + 256] = [
        32700 if frame % 8 < 4 else -32700 for frame in range(256)
    ]
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))


def decode_mono_pcm(path: Path, rate: int = 48000) -> list[int]:
    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            str(rate),
            "-",
        ],
        capture_output=True,
        check=True,
    )
    return [sample[0] for sample in struct.iter_unpack("<h", result.stdout)]


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def measure_loudness(path: Path) -> dict[str, float]:
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-20:TP=-2:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    blocks = re.findall(r'\{\s*"input_i".*?\}', result.stderr, flags=re.DOTALL)
    if not blocks:
        raise AssertionError(f"ffmpeg did not emit loudnorm JSON: {result.stderr}")
    measurement = json.loads(blocks[-1])
    return {
        "integrated_lufs": float(measurement["input_i"]),
        "true_peak_dbtp": float(measurement["input_tp"]),
    }


FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


class AudioFinalizeTemporaryLifecycleTests(unittest.TestCase):
    def make_bgm_args(self, root: Path) -> argparse.Namespace:
        source = root / "source.wav"
        source.write_bytes(b"immutable source")
        return finalize_audio.build_parser().parse_args(
            [
                "bgm",
                "--input",
                str(source),
                "--output",
                str(root / "loop.ogg"),
                "--preview",
                str(root / "preview.ogg"),
                "--metadata",
                str(root / "loop.json"),
            ]
        )

    @contextmanager
    def finalization_patches(self, root: Path) -> Iterator[None]:
        facts = {
            "streams": [{"codec_type": "audio"}],
            "format": {"duration": "4.0"},
        }

        def write_encoded(_args, _snapshot, _start, _end, temporary, _headroom):
            temporary.write_bytes(b"encoded loop")

        def write_preview(_loop, temporary):
            temporary.write_bytes(b"encoded preview")

        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(tempfile, "tempdir", str(root)))
            stack.enter_context(mock.patch.object(finalize_audio, "ffprobe_facts", return_value=facts))
            stack.enter_context(
                mock.patch.object(
                    finalize_audio, "detect_trim_bounds", return_value=(0.0, 4.0)
                )
            )
            stack.enter_context(
                mock.patch.object(finalize_audio, "encode_bgm", side_effect=write_encoded)
            )
            stack.enter_context(
                mock.patch.object(
                    finalize_audio,
                    "measure_loudness",
                    return_value={"input_i": "-20.0", "input_tp": "-2.0"},
                )
            )
            stack.enter_context(
                mock.patch.object(finalize_audio, "encode_preview", side_effect=write_preview)
            )
            yield

    def assert_no_outputs_or_temps(self, root: Path) -> None:
        for name in ("loop.ogg", "preview.ogg", "loop.json"):
            self.assertFalse((root / name).exists())
        self.assertEqual(list(root.glob(".finalize-audio-source-*")), [])
        self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_output_temp_allocation_failure_leaves_no_temporary_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = self.make_bgm_args(root)
            real_mkstemp = tempfile.mkstemp

            def fail_output_allocation(*arguments, **keywords):
                if keywords.get("dir") is not None:
                    raise OSError("injected output allocation failure")
                return real_mkstemp(*arguments, **keywords)

            with (
                self.finalization_patches(root),
                mock.patch.object(
                    tempfile, "mkstemp", side_effect=fail_output_allocation
                ),
                self.assertRaisesRegex(OSError, "injected output allocation failure"),
            ):
                finalize_audio.finalize(args)

            self.assert_no_outputs_or_temps(root)

    def test_preview_temp_allocation_failure_cleans_allocated_output_temp(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = self.make_bgm_args(root)
            real_mkstemp = tempfile.mkstemp
            allocation_count = 0

            def fail_second_allocation(*arguments, **keywords):
                nonlocal allocation_count
                if keywords.get("dir") is not None:
                    allocation_count += 1
                    if allocation_count == 2:
                        raise OSError("injected preview allocation failure")
                return real_mkstemp(*arguments, **keywords)

            with (
                self.finalization_patches(root),
                mock.patch.object(
                    tempfile, "mkstemp", side_effect=fail_second_allocation
                ),
                self.assertRaisesRegex(OSError, "injected preview allocation failure"),
            ):
                finalize_audio.finalize(args)

            self.assert_no_outputs_or_temps(root)

    def test_metadata_temp_allocation_failure_cleans_all_earlier_output_temps(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = self.make_bgm_args(root)
            real_mkstemp = tempfile.mkstemp
            allocation_count = 0

            def fail_third_allocation(*arguments, **keywords):
                nonlocal allocation_count
                if keywords.get("dir") is not None:
                    allocation_count += 1
                    if allocation_count == 3:
                        raise OSError("injected metadata allocation failure")
                return real_mkstemp(*arguments, **keywords)

            with (
                self.finalization_patches(root),
                mock.patch.object(
                    tempfile, "mkstemp", side_effect=fail_third_allocation
                ),
                self.assertRaisesRegex(OSError, "injected metadata allocation failure"),
            ):
                finalize_audio.finalize(args)

            self.assert_no_outputs_or_temps(root)

    def test_encoding_failure_cleans_every_allocated_output_temp(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = self.make_bgm_args(root)

            with (
                self.finalization_patches(root),
                mock.patch.object(
                    finalize_audio,
                    "encode_bgm",
                    side_effect=finalize_audio.AudioToolError("injected encoding failure"),
                ),
                self.assertRaisesRegex(finalize_audio.AudioToolError, "injected encoding failure"),
            ):
                finalize_audio.finalize(args)

            self.assert_no_outputs_or_temps(root)

    def test_owner_cleans_new_temp_if_descriptor_close_fails_for_every_destination_kind(self):
        cases = (
            ("output", "loop.ogg", True),
            ("preview", "preview.ogg", True),
            ("metadata", "loop.json", True),
            ("backup", "existing.ogg", False),
        )
        for label, destination_name, is_output in cases:
            with self.subTest(destination=label), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                destination = root / destination_name
                if label == "backup":
                    destination.write_bytes(b"existing")

                with (
                    mock.patch.object(
                        os, "close", side_effect=OSError("injected descriptor close failure")
                    ),
                    self.assertRaisesRegex(OSError, "injected descriptor close failure"),
                    finalize_audio.TemporaryOutputTransaction(overwrite=True) as transaction,
                ):
                    allocator = transaction.output if is_output else transaction.temporary
                    allocator(destination)

                self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_source_snapshot_setup_and_descriptor_close_failure_still_removes_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            source.write_bytes(b"source")

            with (
                mock.patch.object(tempfile, "tempdir", str(root)),
                mock.patch.object(
                    os, "fdopen", side_effect=OSError("injected snapshot setup failure")
                ),
                mock.patch.object(
                    os, "close", side_effect=OSError("injected snapshot close failure")
                ) as close,
                self.assertRaisesRegex(OSError, "injected snapshot close failure"),
                finalize_audio.source_snapshot(source),
            ):
                self.fail("snapshot setup unexpectedly succeeded")

            close.assert_called_once()
            self.assertEqual(list(root.glob(".finalize-audio-source-*")), [])

    def test_normal_owned_temp_allocation_is_closed_once_and_remains_usable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            destination = root / "result.ogg"
            real_close = os.close

            with (
                mock.patch.object(os, "close", side_effect=real_close) as close,
                finalize_audio.TemporaryOutputTransaction(overwrite=False) as transaction,
            ):
                temporary = transaction.output(destination)
                temporary.write_bytes(b"usable")
                self.assertEqual(temporary.read_bytes(), b"usable")
                close.assert_called_once()

            self.assertFalse(temporary.exists())
            self.assertFalse(destination.exists())


class AudioFinalizeValidationTests(unittest.TestCase):
    def test_peak_retry_is_bounded_uses_snapshot_and_fails_without_final_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            source.write_bytes(b"one immutable source read")
            args = finalize_audio.build_parser().parse_args(
                ["sfx", "--input", str(source), "--output", str(output)]
            )
            source_facts = {
                "streams": [{"codec_type": "audio"}],
                "format": {"duration": "1.0"},
            }
            encoded_sources = []

            def record_encode(_args, snapshot, _start, _end, temporary, _headroom):
                encoded_sources.append(snapshot)
                temporary.write_bytes(b"encoded attempt")

            with (
                mock.patch.object(tempfile, "tempdir", str(root)),
                mock.patch.object(finalize_audio, "ffprobe_facts", return_value=source_facts),
                mock.patch.object(finalize_audio, "detect_trim_bounds", return_value=(0.0, 1.0)),
                mock.patch.object(finalize_audio, "encode_sfx", side_effect=record_encode),
                mock.patch.object(
                    finalize_audio,
                    "measure_loudness",
                    return_value={"input_i": "-20.0", "input_tp": "0.0"},
                ),
                self.assertRaises(finalize_audio.AudioToolError) as raised,
            ):
                finalize_audio.finalize(args)

            self.assertIn("after 4 attempts", str(raised.exception))
            self.assertEqual(len(encoded_sources), 4)
            self.assertEqual(len(set(encoded_sources)), 1)
            self.assertNotEqual(encoded_sources[0], source)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".finalize-audio-source-*")), [])
            self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_snapshot_cleanup_failure_prevents_commit_and_cleans_generated_temps(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "loop.ogg"
            preview = root / "preview.ogg"
            metadata = root / "loop.json"
            source.write_bytes(b"source")
            args = finalize_audio.build_parser().parse_args(
                [
                    "bgm",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--preview",
                    str(preview),
                    "--metadata",
                    str(metadata),
                ]
            )
            facts = {
                "streams": [{"codec_type": "audio"}],
                "format": {"duration": "4.0"},
            }
            real_unlink = Path.unlink

            def write_encoded(_args, _snapshot, _start, _end, temporary, _headroom):
                temporary.write_bytes(b"encoded loop")

            def write_preview(_loop, temporary):
                temporary.write_bytes(b"encoded preview")

            def fail_snapshot_cleanup(path, missing_ok=False):
                if path.name.startswith(".finalize-audio-source-"):
                    raise OSError("injected snapshot cleanup failure")
                return real_unlink(path, missing_ok=missing_ok)

            with (
                mock.patch.object(tempfile, "tempdir", str(root)),
                mock.patch.object(finalize_audio, "ffprobe_facts", return_value=facts),
                mock.patch.object(finalize_audio, "detect_trim_bounds", return_value=(0.0, 4.0)),
                mock.patch.object(finalize_audio, "encode_bgm", side_effect=write_encoded),
                mock.patch.object(
                    finalize_audio,
                    "measure_loudness",
                    return_value={"input_i": "-20.0", "input_tp": "-2.0"},
                ),
                mock.patch.object(finalize_audio, "encode_preview", side_effect=write_preview),
                mock.patch.object(Path, "unlink", new=fail_snapshot_cleanup),
                self.assertRaisesRegex(OSError, "injected snapshot cleanup failure"),
            ):
                finalize_audio.finalize(args)

            self.assertFalse(output.exists())
            self.assertFalse(preview.exists())
            self.assertFalse(metadata.exists())
            self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_atomic_no_clobber_reports_partial_path_when_rollback_cleanup_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_temp = root / "new-first"
            second_temp = root / "new-second"
            first = root / "first.ogg"
            second = root / "second.json"
            first_temp.write_bytes(b"new-first")
            second_temp.write_bytes(b"new-second")
            real_link = os.link
            real_unlink = Path.unlink

            def fail_second_link(source, destination):
                if Path(source) == second_temp:
                    raise OSError("injected second link failure")
                return real_link(source, destination)

            def fail_first_rollback(path, missing_ok=False):
                if path == first:
                    raise OSError("injected first rollback failure")
                return real_unlink(path, missing_ok=missing_ok)

            with (
                mock.patch.object(os, "link", side_effect=fail_second_link),
                mock.patch.object(Path, "unlink", new=fail_first_rollback),
                self.assertRaises(finalize_audio.AudioToolError) as raised,
            ):
                finalize_audio.atomic_commit(
                    [(first_temp, first), (second_temp, second)], overwrite=False
                )

            self.assertIn("rollback failed", str(raised.exception))
            self.assertIn(str(first), str(raised.exception))
            self.assertEqual(first.read_bytes(), b"new-first")
            self.assertFalse(second.exists())

    def test_atomic_overwrite_rolls_back_multiple_outputs_without_partial_finals(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            temporaries = [root / f"new-{index}" for index in range(3)]
            destinations = [root / f"final-{index}" for index in range(3)]
            for index, temporary in enumerate(temporaries):
                temporary.write_bytes(f"new-{index}".encode())
            destinations[0].write_bytes(b"old-0")
            destinations[2].write_bytes(b"old-2")
            real_replace = os.replace

            def fail_third_install(source, destination):
                if Path(source) == temporaries[2] and Path(destination) == destinations[2]:
                    raise OSError("injected third install failure")
                return real_replace(source, destination)

            with (
                mock.patch.object(os, "replace", side_effect=fail_third_install),
                self.assertRaises(finalize_audio.AudioToolError),
            ):
                finalize_audio.atomic_commit(
                    list(zip(temporaries, destinations, strict=True)), overwrite=True
                )

            self.assertEqual(destinations[0].read_bytes(), b"old-0")
            self.assertFalse(destinations[1].exists())
            self.assertEqual(destinations[2].read_bytes(), b"old-2")
            self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_atomic_overwrite_reports_recovery_backup_when_rollback_restore_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_temp = root / "new-first.ogg"
            second_temp = root / "new-second.json"
            first = root / "first.ogg"
            second = root / "second.json"
            first_temp.write_bytes(b"new-first")
            second_temp.write_bytes(b"new-second")
            first.write_bytes(b"old-first")
            second.write_bytes(b"old-second")
            real_replace = os.replace
            recovery_backups = []

            def fail_second_install_and_first_restore(source, destination):
                source = Path(source)
                destination = Path(destination)
                if source == second_temp and destination == second:
                    raise OSError("injected second install failure")
                if source.name.startswith(".first.") and destination == first:
                    recovery_backups.append(source)
                    raise OSError("injected first restore failure")
                return real_replace(source, destination)

            with (
                mock.patch.object(
                    os, "replace", side_effect=fail_second_install_and_first_restore
                ),
                self.assertRaises(finalize_audio.AudioToolError) as raised,
            ):
                finalize_audio.atomic_commit(
                    [(first_temp, first), (second_temp, second)], overwrite=True
                )

            self.assertIn("rollback failed", str(raised.exception))
            self.assertEqual(len(recovery_backups), 1)
            self.assertIn(str(recovery_backups[0]), str(raised.exception))
            self.assertEqual(recovery_backups[0].read_bytes(), b"old-first")
            self.assertEqual(second.read_bytes(), b"old-second")
            self.assertFalse(first.exists())

    def test_atomic_overwrite_cleanup_failure_does_not_report_committed_outputs_failed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_temp = root / "new-first.ogg"
            second_temp = root / "new-second.json"
            first = root / "first.ogg"
            second = root / "second.json"
            first_temp.write_bytes(b"new-first")
            second_temp.write_bytes(b"new-second")
            first.write_bytes(b"old-first")
            second.write_bytes(b"old-second")
            real_unlink = Path.unlink

            def fail_backup_cleanup(path, missing_ok=False):
                if missing_ok and path.name.startswith((".first.", ".second.")):
                    raise OSError("injected backup cleanup failure")
                return real_unlink(path, missing_ok=missing_ok)

            with mock.patch.object(Path, "unlink", new=fail_backup_cleanup):
                finalize_audio.atomic_commit(
                    [(first_temp, first), (second_temp, second)], overwrite=True
                )

            self.assertEqual(first.read_bytes(), b"new-first")
            self.assertEqual(second.read_bytes(), b"new-second")
            backup_bytes = sorted(path.read_bytes() for path in root.glob(".*.tmp*"))
            self.assertEqual(backup_bytes, [b"old-first", b"old-second"])

    def test_cli_rejects_missing_input_before_running_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run_cli(
                "sfx",
                "--input",
                str(Path(temp) / "missing.wav"),
                "--output",
                str(Path(temp) / "result.ogg"),
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("input does not exist", result.stderr)

    def test_cli_rejects_input_that_is_not_a_regular_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = run_cli(
                "sfx", "--input", str(root), "--output", str(root / "result.ogg")
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("input is not a regular file", result.stderr)

    def test_cli_rejects_non_ogg_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            source.write_bytes(b"fixture")
            result = run_cli(
                "sfx", "--input", str(source), "--output", str(root / "result.mp3")
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("output must use the .ogg extension", result.stderr)

    def test_cli_rejects_non_finite_or_out_of_range_settings(self):
        cases = (
            ("sfx", "--silence-threshold-db", "nan"),
            ("sfx", "--silence-threshold-db", "1"),
            ("sfx", "--min-silence-duration", "0"),
            ("bgm", "--crossfade", "inf"),
            ("sfx", "--fade-out", "-0.1"),
            ("bgm", "--target-lufs", "0"),
            ("bgm", "--target-lufs", "-4"),
            ("bgm", "--target-peak-db", "-10"),
            ("sfx", "--target-peak-db", "-200"),
            ("sfx", "--max-input-duration", "0"),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            source.write_bytes(b"fixture")
            for role, option, value in cases:
                with self.subTest(option=option, value=value):
                    result = run_cli(
                        role,
                        "--input",
                        str(source),
                        "--output",
                        str(root / "result.ogg"),
                        option,
                        value,
                    )
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("invalid setting", result.stderr)

    def test_cli_defaults_to_no_clobber(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            source.write_bytes(b"fixture")
            output.write_bytes(b"keep")

            result = run_cli("sfx", "--input", str(source), "--output", str(output))

            self.assertEqual(result.returncode, 2)
            self.assertIn("destination already exists", result.stderr)
            self.assertEqual(output.read_bytes(), b"keep")

    def test_cli_rejects_same_symlink_and_hardlink_input_output_aliases(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.ogg"
            source.write_bytes(b"fixture")
            aliases = [source]
            symlink = root / "symlink.ogg"
            symlink.symlink_to(source)
            aliases.append(symlink)
            hardlink = root / "hardlink.ogg"
            hardlink.hardlink_to(source)
            aliases.append(hardlink)

            for alias in aliases:
                with self.subTest(alias=alias.name):
                    result = run_cli(
                        "sfx",
                        "--input",
                        str(source),
                        "--output",
                        str(alias),
                        "--overwrite",
                    )
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("aliases input", result.stderr)

            self.assertEqual(source.read_bytes(), b"fixture")

    def test_validation_rejects_case_only_input_and_nonexistent_destination_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "Source.ogg"
            source.write_bytes(b"fixture")
            args = finalize_audio.build_parser().parse_args(
                [
                    "sfx",
                    "--input",
                    str(source),
                    "--output",
                    str(root / "source.ogg"),
                    "--overwrite",
                ]
            )

            with self.assertRaisesRegex(finalize_audio.AudioFinalizeError, "aliases input"):
                finalize_audio.validate_paths(args)

    def test_validation_rejects_case_only_nonexistent_destinations_in_overwrite_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            source.write_bytes(b"fixture")
            args = finalize_audio.build_parser().parse_args(
                [
                    "sfx",
                    "--input",
                    str(source),
                    "--output",
                    str(root / "Result.ogg"),
                    "--metadata",
                    str(root / "result.ogg"),
                    "--overwrite",
                ]
            )

            with self.assertRaisesRegex(
                finalize_audio.AudioFinalizeError, "destination paths alias each other"
            ):
                finalize_audio.validate_paths(args)

    def test_validation_rejects_case_only_existing_input_destination_aliases(self):
        cases = (
            ("output", "sfx", "--output"),
            ("preview", "bgm", "--preview"),
            ("metadata", "sfx", "--metadata"),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for label, role, aliased_option in cases:
                with self.subTest(destination=label):
                    case_root = root / label
                    case_root.mkdir()
                    source = case_root / "Source.ogg"
                    output = case_root / "final.ogg"
                    aliased_destination = case_root / "source.ogg"
                    source.write_bytes(b"source")
                    output.write_bytes(b"output")
                    aliased_destination.write_bytes(b"destination")
                    arguments = [
                        role,
                        "--input",
                        str(source),
                        "--output",
                        str(aliased_destination if aliased_option == "--output" else output),
                        "--overwrite",
                    ]
                    if aliased_option != "--output":
                        arguments.extend([aliased_option, str(aliased_destination)])
                    args = finalize_audio.build_parser().parse_args(arguments)

                    self.assertFalse(source.samefile(aliased_destination))
                    with self.assertRaisesRegex(
                        finalize_audio.AudioFinalizeError, "aliases input"
                    ):
                        finalize_audio.validate_paths(args)

    def test_validation_rejects_case_only_existing_destination_pairings_in_overwrite_mode(
        self,
    ):
        cases = (
            ("output-preview", "Result.ogg", "result.ogg", "details.json"),
            ("output-metadata", "Result.ogg", "preview.ogg", "result.ogg"),
            ("preview-metadata", "final.ogg", "Result.ogg", "result.ogg"),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for label, output_name, preview_name, metadata_name in cases:
                with self.subTest(pairing=label):
                    case_root = root / label
                    case_root.mkdir()
                    source = case_root / "source.wav"
                    output = case_root / output_name
                    preview = case_root / preview_name
                    metadata = case_root / metadata_name
                    for path in (source, output, preview, metadata):
                        path.write_bytes(path.name.encode())
                    args = finalize_audio.build_parser().parse_args(
                        [
                            "bgm",
                            "--input",
                            str(source),
                            "--output",
                            str(output),
                            "--preview",
                            str(preview),
                            "--metadata",
                            str(metadata),
                            "--overwrite",
                        ]
                    )

                    first_name, second_name = label.split("-")
                    first = getattr(args, first_name)
                    second = getattr(args, second_name)
                    self.assertFalse(first.samefile(second))
                    with self.assertRaisesRegex(
                        finalize_audio.AudioFinalizeError, "destination paths alias each other"
                    ):
                        finalize_audio.validate_paths(args)

    def test_validation_accepts_distinct_existing_names_in_same_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "final.ogg"
            preview = root / "preview.ogg"
            metadata = root / "final.json"
            for path in (source, output, preview, metadata):
                path.write_bytes(path.name.encode())
            args = finalize_audio.build_parser().parse_args(
                [
                    "bgm",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--preview",
                    str(preview),
                    "--metadata",
                    str(metadata),
                    "--overwrite",
                ]
            )

            finalize_audio.validate_paths(args)

    def test_atomic_no_clobber_commit_rejects_destination_created_after_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            temporary = root / ".result.tmp.ogg"
            destination = root / "result.ogg"
            temporary.write_bytes(b"new")
            destination.write_bytes(b"keep")

            with self.assertRaises(finalize_audio.AudioToolError):
                finalize_audio.atomic_commit(
                    [(temporary, destination)], overwrite=False
                )

            self.assertEqual(destination.read_bytes(), b"keep")
            self.assertEqual(temporary.read_bytes(), b"new")


@unittest.skipUnless(FFMPEG_AVAILABLE, "ffmpeg and ffprobe are required for integration tests")
class AudioFinalizeIntegrationTests(unittest.TestCase):
    def test_bgm_enforces_post_encode_true_peak_ceiling_and_keeps_target_loudness(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "loop.ogg"
            make_transient_wave(source)

            result = run_cli(
                "bgm",
                "--input",
                str(source),
                "--output",
                str(output),
                "--crossfade",
                "0.5",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            measured = measure_loudness(output)
            self.assertLessEqual(measured["true_peak_dbtp"], -2.0)
            self.assertAlmostEqual(measured["integrated_lufs"], -20.0, delta=0.5)

    def test_sfx_enforces_post_encode_true_peak_ceiling_on_high_frequency_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            make_wave(source, [(0.8, 0.95), (0.3, 0.0)], frequency=16000.0)

            result = run_cli("sfx", "--input", str(source), "--output", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            measured = measure_loudness(output)
            self.assertLessEqual(measured["true_peak_dbtp"], -2.0)

    def test_processing_and_source_hash_use_one_snapshot_if_original_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            metadata = root / "result.json"
            make_wave(source, [(0.7, 0.2), (0.3, 0.0)])
            original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            args = finalize_audio.build_parser().parse_args(
                [
                    "sfx",
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--metadata",
                    str(metadata),
                ]
            )
            real_ffprobe = finalize_audio.ffprobe_facts
            probed_paths = []

            def replace_original_after_first_probe(path):
                facts = real_ffprobe(path)
                probed_paths.append(path)
                if len(probed_paths) == 1:
                    source.write_bytes(b"replacement that is not the source audio")
                return facts

            with (
                mock.patch.object(finalize_audio, "ffprobe_facts", side_effect=replace_original_after_first_probe),
                mock.patch.object(tempfile, "tempdir", str(root)),
            ):
                finalize_audio.finalize(args)

            report = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertNotEqual(probed_paths[0], source)
            self.assertEqual(report["source"]["path"], str(source))
            self.assertEqual(report["source"]["sha256"], original_hash)
            self.assertTrue(output.is_file())
            self.assertEqual(list(root.glob(".finalize-audio-source-*")), [])

    def test_bgm_starts_with_circular_crossfade_seam(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "loop.ogg"
            make_wave(source, [(0.2, 0.1), (1.6, 0.02), (0.2, 0.4)])

            result = run_cli(
                "bgm",
                "--input",
                str(source),
                "--output",
                str(output),
                "--crossfade",
                "0.2",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            pcm = decode_mono_pcm(output)

            def rms(samples: list[int]) -> float:
                return math.sqrt(sum(value * value for value in samples) / len(samples))

            seam_rms = rms(pcm[:2400])
            middle_rms = rms(pcm[12000:14400])
            self.assertGreater(seam_rms, middle_rms * 4)

    def test_bgm_hits_target_loudness_and_records_measured_output_qa(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "loop.ogg"
            metadata = root / "loop.json"
            make_wave(
                source,
                [
                    (0.3, 0.0),
                    (3.0, 0.01),
                    (1.0, 0.4),
                    (3.0, 0.02),
                    (1.0, 0.3),
                    (0.4, 0.0),
                ],
            )

            result = run_cli(
                "bgm",
                "--input",
                str(source),
                "--output",
                str(output),
                "--metadata",
                str(metadata),
                "--crossfade",
                "0.5",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            measured = measure_loudness(output)
            self.assertAlmostEqual(measured["integrated_lufs"], -20.0, delta=0.2)
            report = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(report["output"]["qa"], measured)

    def test_sfx_trims_dead_tail_fades_normalizes_and_writes_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            metadata = root / "result.json"
            make_wave(source, [(0.1, 0.0), (0.5, 0.15), (0.5, 0.0)])
            source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

            result = run_cli(
                "sfx",
                "--input",
                str(source),
                "--output",
                str(output),
                "--metadata",
                str(metadata),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            facts = probe(output)
            stream = facts["streams"][0]
            self.assertEqual(stream["codec_name"], "vorbis")
            self.assertEqual(stream["sample_rate"], "48000")
            self.assertEqual(stream["channels"], 2)
            self.assertLess(float(facts["format"]["duration"]), 0.75)
            measured = measure_loudness(output)
            pcm = decode_mono_pcm(output)
            peak_db = 20 * math.log10(max(abs(value) for value in pcm) / 32768)
            before_fade = pcm[-2880:-2400]
            fade_tail = pcm[-480:]
            before_rms = math.sqrt(sum(value * value for value in before_fade) / len(before_fade))
            tail_rms = math.sqrt(sum(value * value for value in fade_tail) / len(fade_tail))
            self.assertAlmostEqual(peak_db, -2.0, delta=1.2)
            self.assertLess(tail_rms, before_rms * 0.4)
            report = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(report["role"], "sfx")
            self.assertEqual(report["output"]["qa"], measured)
            self.assertIn("true_peak_dbtp", report["output"]["qa"])
            self.assertEqual(report["source"]["sha256"], source_hash)
            self.assertEqual(
                report["output"]["sha256"], hashlib.sha256(output.read_bytes()).hexdigest()
            )
            self.assertAlmostEqual(report["trim"]["start_seconds"], 0.0, delta=0.02)
            self.assertAlmostEqual(report["trim"]["end_seconds"], 0.6, delta=0.04)
            self.assertAlmostEqual(report["settings"]["fade_out_seconds"], 0.05)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), source_hash)

    def test_failure_preserves_existing_destinations_and_cleans_sibling_temps(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            metadata = root / "metadata"
            make_wave(source, [(0.5, 0.2), (0.4, 0.0)])
            output.write_bytes(b"keep-output")
            metadata.mkdir()

            result = run_cli(
                "sfx",
                "--input",
                str(source),
                "--output",
                str(output),
                "--metadata",
                str(metadata),
                "--overwrite",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b"keep-output")
            self.assertTrue(metadata.is_dir())
            self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_ffmpeg_failure_preserves_output_and_removes_allocated_temp(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            fake_bin = root / "bin"
            fake_bin.mkdir()
            make_wave(source, [(0.5, 0.2), (0.4, 0.0)])
            output.write_bytes(b"keep-output")
            (fake_bin / "ffprobe").symlink_to(str(shutil.which("ffprobe")))
            counter = root / "ffmpeg-count"
            fake_ffmpeg = fake_bin / "ffmpeg"
            fake_ffmpeg.write_text(
                "#!/bin/sh\n"
                f"if [ -r '{counter}' ]; then IFS= read -r count < '{counter}'; else count=0; fi\n"
                "count=$((count + 1))\n"
                f"printf %s \"$count\" > '{counter}'\n"
                f"if [ \"$count\" -eq 1 ]; then exec '{shutil.which('ffmpeg')}' \"$@\"; fi\n"
                "exit 9\n",
                encoding="utf-8",
            )
            fake_ffmpeg.chmod(0o755)
            environment = dict(os.environ)
            environment["PATH"] = str(fake_bin)

            result = run_cli(
                "sfx",
                "--input",
                str(source),
                "--output",
                str(output),
                "--overwrite",
                env=environment,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("ffmpeg failed", result.stderr)
            self.assertEqual(output.read_bytes(), b"keep-output")
            self.assertEqual(list(root.glob(".*.tmp*")), [])

    def test_cli_rejects_input_longer_than_configured_maximum(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "result.ogg"
            make_wave(source, [(0.8, 0.2)])

            result = run_cli(
                "sfx",
                "--input",
                str(source),
                "--output",
                str(output),
                "--max-input-duration",
                "0.5",
            )

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("exceeds maximum", result.stderr)
            self.assertFalse(output.exists())

    def test_bgm_trims_crossfades_to_48k_stereo_and_builds_two_loop_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.wav"
            output = root / "loop.ogg"
            preview = root / "preview.ogg"
            metadata = root / "loop.json"
            make_wave(source, [(0.3, 0.0), (2.4, 0.12), (0.4, 0.0)])

            result = run_cli(
                "bgm",
                "--input",
                str(source),
                "--output",
                str(output),
                "--preview",
                str(preview),
                "--metadata",
                str(metadata),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output_facts = probe(output)
            preview_facts = probe(preview)
            stream = output_facts["streams"][0]
            self.assertEqual(stream["codec_name"], "vorbis")
            self.assertEqual(stream["sample_rate"], "48000")
            self.assertEqual(stream["channels"], 2)
            loop_duration = float(output_facts["format"]["duration"])
            preview_duration = float(preview_facts["format"]["duration"])
            self.assertLess(loop_duration, 2.0)
            self.assertAlmostEqual(preview_duration, loop_duration * 2, delta=0.12)
            report = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(report["role"], "bgm")
            self.assertAlmostEqual(report["trim"]["start_seconds"], 0.3, delta=0.04)
            self.assertAlmostEqual(report["trim"]["end_seconds"], 2.7, delta=0.05)
            self.assertAlmostEqual(report["settings"]["crossfade_seconds"], 1.0)
            self.assertAlmostEqual(report["settings"]["target_lufs"], -20.0)
            self.assertEqual(
                report["preview"]["sha256"], hashlib.sha256(preview.read_bytes()).hexdigest()
            )
            self.assertEqual(report["preview"]["ffprobe"]["streams"][0]["channels"], 2)


if __name__ == "__main__":
    unittest.main()
