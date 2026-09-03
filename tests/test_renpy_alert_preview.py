import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from ui_system_alert_frame.scripts.make_renpy_alert_preview import render_alert_preview


class RenPyAlertPreviewTests(unittest.TestCase):
    def test_render_alert_preview_rejects_text_that_cannot_fit_panel_padding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)

            for output_name, panel_size in (("short.png", (720, 20)), ("narrow.png", (100, 240))):
                with (
                    self.subTest(panel_size=panel_size),
                    self.assertRaisesRegex(ValueError, "text does not fit inside panel padding"),
                ):
                    render_alert_preview(
                        frame,
                        background,
                        root / output_name,
                        message="alert",
                        panel_size=panel_size,
                    )

    def test_render_alert_preview_requires_explicit_font_for_non_ascii_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)

            with self.assertRaisesRegex(ValueError, "non-ASCII text requires an explicit font"):
                render_alert_preview(frame, background, root / "preview.png", message="경고 발생")

    def test_cli_overwrite_flag_replaces_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            output = root / "preview.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)
            output.write_bytes(b"existing output")

            completed = subprocess.run(
                [
                    sys.executable,
                    "ui_system_alert_frame/scripts/make_renpy_alert_preview.py",
                    str(frame),
                    str(background),
                    str(output),
                    "--message",
                    "alert",
                    "--overwrite",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            with Image.open(output) as image:
                self.assertEqual(image.size, (1920, 1080))

    def test_render_alert_preview_atomically_overwrites_existing_output_when_opted_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            output = root / "preview.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)
            output.write_bytes(b"existing output")

            def fail_after_partial_write(_image, destination, *args, **kwargs):
                Path(destination).write_bytes(b"partial output")
                raise OSError("simulated write failure")

            with (
                patch.object(Image.Image, "save", autospec=True, side_effect=fail_after_partial_write),
                self.assertRaisesRegex(OSError, "simulated write failure"),
            ):
                render_alert_preview(frame, background, output, message="alert", overwrite=True)

            self.assertEqual(output.read_bytes(), b"existing output")
            render_alert_preview(frame, background, output, message="alert", overwrite=True)
            with Image.open(output) as image:
                self.assertEqual(image.size, (1920, 1080))

    def test_render_alert_preview_refuses_hardlink_alias_of_input_even_with_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            output = root / "frame-alias.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)
            os.link(frame, output)

            with self.assertRaisesRegex(ValueError, "output must not overwrite an input image"):
                render_alert_preview(frame, background, output, message="alert", overwrite=True)

    def test_render_alert_preview_refuses_existing_output_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            output = root / "preview.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)
            output.write_bytes(b"existing output")

            with self.assertRaisesRegex(FileExistsError, "output already exists"):
                render_alert_preview(frame, background, output, message="alert")

            self.assertEqual(output.read_bytes(), b"existing output")

    def test_render_alert_preview_rejects_oversized_source_before_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            output = root / "preview.png"
            Image.new("1", (5000, 5000)).save(background)
            Image.new("RGB", (16, 9), "black").save(frame)

            with self.assertRaisesRegex(ValueError, "source image exceeds maximum pixel count"):
                render_alert_preview(frame, background, output, message="alert")

            self.assertFalse(output.exists())

    def test_render_alert_preview_wraps_long_text_without_covering_protected_box(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            output = root / "preview.png"
            Image.new("RGB", (1024, 576), (20, 40, 80)).save(background)
            Image.new("RGB", (1024, 576), (10, 0, 0)).save(frame)

            result = render_alert_preview(
                frame,
                background,
                output,
                message="Unknown data core was detected in classroom three",
                display_size=(1920, 1080),
                panel_size=(720, 240),
                margin=(48, 48),
                protected_box=(800, 40, 1250, 760),
            )

            with Image.open(output) as image:
                self.assertEqual(image.size, (1920, 1080))
                self.assertEqual(image.mode, "RGB")
            self.assertEqual(result["panel_box"], [48, 48, 768, 288])
            self.assertGreaterEqual(len(result["message_lines"]), 2)
            self.assertFalse(result["protected_box_intersection"])
            self.assertEqual(result["presentation_mode"], "top_left_nonmodal")

    def test_render_alert_preview_refuses_to_overwrite_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frame = root / "frame.png"
            background = root / "background.png"
            Image.new("RGB", (1024, 576), (10, 10, 10)).save(frame)
            Image.new("RGB", (1024, 576), (30, 30, 30)).save(background)
            with self.assertRaises(ValueError):
                render_alert_preview(
                    frame_path=frame,
                    background_path=background,
                    output_path=frame,
                    message="alert",
                )
            with self.assertRaises(ValueError):
                render_alert_preview(
                    frame_path=frame,
                    background_path=background,
                    output_path=background,
                    message="alert",
                )

    def test_render_alert_preview_rejects_invalid_geometry_and_empty_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            frame = root / "frame.png"
            Image.new("RGB", (16, 9), "blue").save(background)
            Image.new("RGB", (16, 9), "black").save(frame)

            with self.assertRaises(ValueError):
                render_alert_preview(frame, background, root / "out.png", message="")
            with self.assertRaises(ValueError):
                render_alert_preview(
                    frame,
                    background,
                    root / "out.png",
                    message="alert",
                    display_size=(640, 360),
                    panel_size=(700, 200),
                )
            with self.assertRaises(ValueError):
                render_alert_preview(
                    frame,
                    background,
                    root / "out.png",
                    message="alert",
                    display_size=(1920, 1080),
                    protected_box=(0, 0, 800, 400),
                )


if __name__ == "__main__":
    unittest.main()
