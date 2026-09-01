import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "dependencies/manifest.json"


class DependencyManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_has_unique_pinned_model_files(self):
        models = self.manifest["model_files"]
        ids = [item["id"] for item in models]
        destinations = [item["destination"] for item in models]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(destinations), len(set(destinations)))
        for item in models:
            self.assertRegex(item["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(item["bytes"], 0)
            self.assertTrue(item["url"].startswith("https://"))
            self.assertTrue(item["workflows"])
            self.assertIn(item["required"], (True, False))

    def test_custom_nodes_are_commit_pinned_and_map_required_classes(self):
        custom_nodes = self.manifest["custom_nodes"]
        covered = set()
        for item in custom_nodes:
            self.assertRegex(item["commit"], r"^[0-9a-f]{40}$")
            self.assertTrue(item["repository"].startswith("https://github.com/"))
            covered.update(item["classes"])
        self.assertTrue(
            {"AILab_MaskEnhancer", "BiRefNetRMBG", "UltralyticsDetectorProvider"}.issubset(covered)
        )

    def test_manifest_covers_every_model_file_referenced_by_graphs(self):
        manifest_names = {Path(item["destination"]).name for item in self.manifest["model_files"]}
        index = json.loads((ROOT / "WORKFLOW_INDEX.json").read_text(encoding="utf-8"))
        referenced = set()
        model_keys = {"ckpt_name", "control_net_name", "lora_name", "model_name", "clip_name", "vae_name"}
        for workflow in index["workflows"]:
            graph = json.loads((ROOT / workflow["api"]).read_text(encoding="utf-8"))
            for node in graph.values():
                for key, value in node.get("inputs", {}).items():
                    if key in model_keys and isinstance(value, str) and Path(value).suffix in {".safetensors", ".pt", ".pth"}:
                        referenced.add(Path(value).name)
        self.assertEqual(referenced, manifest_names)

    def test_external_tools_and_taxonomy_are_pinned(self):
        self.assertIn("ffmpeg", self.manifest["external_tools"])
        taxonomy = self.manifest["taxonomy"]
        self.assertRegex(taxonomy["sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue(taxonomy["url"].startswith("https://"))
        self.assertEqual(taxonomy["destination"], "danbooru-taxonomy.release.sqlite")


if __name__ == "__main__":
    unittest.main()
