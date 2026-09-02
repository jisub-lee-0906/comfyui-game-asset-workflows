import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.make_renpy_background_preview import render_preview


class RenPyBackgroundPreviewTests(unittest.TestCase):
    def test_render_preview_creates_display_sized_rgb_artifact_with_textbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            output = root / "preview.png"
            Image.new("RGB", (1024, 576), (20, 40, 80)).save(background)

            result = render_preview(background, output, display_size=(1920, 1080), textbox_fraction=0.28)

            image = Image.open(output)
            self.assertEqual(image.size, (1920, 1080))
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(result["textbox_top"], 778)
            self.assertEqual(result["background_source_size"], [1024, 576])
            self.assertEqual(result["display_size"], [1920, 1080])
            self.assertTrue(result["renpy_scale_exact"])
            self.assertNotEqual(image.getpixel((960, 1000)), (20, 40, 80))

    def test_render_preview_centers_alpha_character_above_bottom_edge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            character = root / "character.png"
            output = root / "preview.png"
            Image.new("RGB", (160, 90), (0, 0, 0)).save(background)
            sprite = Image.new("RGBA", (40, 80), (0, 0, 0, 0))
            for x in range(10, 30):
                for y in range(5, 80):
                    sprite.putpixel((x, y), (255, 0, 0, 255))
            sprite.save(character)

            result = render_preview(
                background,
                output,
                character_path=character,
                display_size=(160, 90),
                character_height_fraction=0.90,
            )

            image = Image.open(output)
            self.assertIsNotNone(result["character_box"])
            left, top, right, bottom = result["character_box"]
            self.assertEqual((left + right) // 2, 80)
            self.assertEqual(bottom, 90)
            self.assertLess(top, bottom)
            self.assertGreater(image.getpixel((80, 40))[0], 200)

    def test_render_preview_rejects_invalid_contract_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            background = root / "background.png"
            Image.new("RGB", (16, 9), "black").save(background)
            for fraction in (0, 1, -0.1, 1.1):
                with self.subTest(textbox_fraction=fraction), self.assertRaises(ValueError):
                    render_preview(background, root / "out.png", textbox_fraction=fraction)
            with self.assertRaises(ValueError):
                render_preview(background, root / "out.png", display_size=(0, 1080))


if __name__ == "__main__":
    unittest.main()
