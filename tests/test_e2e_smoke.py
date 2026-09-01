import tempfile
import unittest
from pathlib import Path

from scripts.e2e_smoke import build_smoke_edits
from scripts.workflow_pack import render_workflow

ROOT = Path(__file__).resolve().parents[1]


class E2ESmokePlanTests(unittest.TestCase):
    def test_smoke_plan_covers_all_workflows_and_renders_without_placeholders(self):
        plan = build_smoke_edits("smoke-test", "smoke/source.png", "smoke/expression.png")
        self.assertEqual(
            set(plan),
            {
                "char_base",
                "char_expression",
                "char_alpha",
                "scene_background",
                "scene_event_cg",
                "scene_prop_cg",
                "ui_system_alert_frame",
                "audio_bgm_with_sfx",
            },
        )
        with tempfile.TemporaryDirectory() as temp:
            for workflow_id, edits in plan.items():
                result = render_workflow(ROOT, workflow_id, edits, Path(temp))
                self.assertEqual(result["unresolved_placeholders"], [], workflow_id)
                output_paths = [key for key in edits if key.endswith("filename_prefix")]
                self.assertEqual(len(output_paths), 1, workflow_id)
                self.assertIn("smoke-test", edits[output_paths[0]])


if __name__ == "__main__":
    unittest.main()
