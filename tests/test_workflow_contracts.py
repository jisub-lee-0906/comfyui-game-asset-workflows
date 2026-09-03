import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "WORKFLOW_INDEX.json"
PLACEHOLDER_RE = re.compile(r"TEMPLATE_[A-Za-z0-9_./-]+|\{[^{}\n]*[가-힣][^{}\n]*\}")


def load_index():
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def get_path_value(graph, dotted_path):
    parts = dotted_path.split(".")
    value = graph
    for part in parts:
        value = value[part]
    return value


def discover_placeholders(graph):
    found = set()
    for node_id, node in graph.items():
        for input_name, value in node.get("inputs", {}).items():
            if not isinstance(value, str):
                continue
            for token in PLACEHOLDER_RE.findall(value):
                found.add((node_id, f"{node_id}.inputs.{input_name}", token))
    return found


def assert_acyclic(testcase, edges, workflow_id):
    visiting = set()
    visited = set()

    def visit(node_id):
        testcase.assertNotIn(node_id, visiting, f"cycle in {workflow_id} at {node_id}")
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in edges[node_id]:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in edges:
        visit(node_id)


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load_index()

    def test_index_is_portable_and_has_no_machine_specific_roots(self):
        encoded = json.dumps(self.index, ensure_ascii=False)
        self.assertNotIn("E:\\\\workspace", encoded)
        self.assertNotIn("C:\\\\Users\\\\Desktop", encoded)
        self.assertNotIn("C:/Users/Desktop", encoded)
        self.assertEqual(self.index["paths"]["comfyui_url_env"], "COMFYUI_URL")
        self.assertEqual(self.index["paths"]["comfyui_input_env"], "COMFYUI_INPUT_DIR")
        self.assertEqual(self.index["paths"]["comfyui_output_env"], "COMFYUI_OUTPUT_DIR")

    def test_all_declared_files_and_editable_fields_exist(self):
        for workflow in self.index["workflows"]:
            with self.subTest(workflow=workflow["id"]):
                readme = ROOT / workflow["readme"]
                api = ROOT / workflow["api"]
                self.assertTrue(readme.is_file(), readme)
                self.assertTrue(api.is_file(), api)
                graph = json.loads(api.read_text(encoding="utf-8"))
                for path in workflow["editable_fields"]:
                    get_path_value(graph, path)
                for node_id in workflow["primary_nodes"].values():
                    self.assertIn(node_id, graph)

    def test_graph_references_are_valid_and_acyclic(self):
        for workflow in self.index["workflows"]:
            graph = json.loads((ROOT / workflow["api"]).read_text(encoding="utf-8"))
            edges = {node_id: set() for node_id in graph}
            for node_id, node in graph.items():
                for value in node.get("inputs", {}).values():
                    if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                        self.assertIn(value[0], graph, f"{workflow['id']} node {node_id}")
                        edges[node_id].add(value[0])
            assert_acyclic(self, edges, workflow["id"])

    def test_index_records_every_runtime_placeholder_exactly(self):
        for workflow in self.index["workflows"]:
            graph = json.loads((ROOT / workflow["api"]).read_text(encoding="utf-8"))
            actual = discover_placeholders(graph)
            declared = {
                (item["node_id"], item["path"], item["token"])
                for item in workflow["placeholders"]
            }
            self.assertEqual(declared, actual, workflow["id"])

    def test_alpha_workflow_uses_portrait_model_that_removes_full_background(self):
        graph = json.loads((ROOT / "char_alpha/char_alpha_workflow_api.json").read_text(encoding="utf-8"))
        self.assertEqual(graph["2"]["inputs"]["model"], "BiRefNet-portrait")

    def test_expression_template_has_no_nudity_default(self):
        graph = json.loads((ROOT / "char_expression/char_expression_workflow_api.json").read_text(encoding="utf-8"))
        prompt = graph["6"]["inputs"]["text"]
        readme = (ROOT / "char_expression/README.md").read_text(encoding="utf-8")
        self.assertNotRegex(prompt, r"(?:^|,\s*)nude(?:\s*,|$)")
        self.assertNotRegex(readme, r"(?:^|,\s*)nude(?:\s*,|$)")

    def test_char_base_defaults_to_validated_vn_cowboy_framing(self):
        graph = json.loads((ROOT / "char_base/char_base_workflow_api.json").read_text(encoding="utf-8"))
        positive = {tag.strip() for tag in graph["3"]["inputs"]["text"].split(",")}
        negative = {tag.strip() for tag in graph["4"]["inputs"]["text"].split(",")}

        self.assertEqual(graph["5"]["inputs"]["width"], 1024)
        self.assertEqual(graph["5"]["inputs"]["height"], 1280)
        self.assertTrue(
            {"(cowboy_shot:1.3)", "straight-on", "facing_viewer", "looking_at_viewer", "arms_at_sides"}
            <= positive
        )
        self.assertTrue({"full_body", "feet", "shoes", "profile", "three_quarter_view", "cropped_arms"} <= negative)
        self.assertTrue(
            {"front_view", "centered", "symmetrical_composition", "hands_visible", "relaxed_hands", "headroom"}
            .isdisjoint(positive | negative)
        )

    def test_scene_background_defaults_encode_renpy_staging_contract(self):
        graph = json.loads((ROOT / "scene_background/scene_background_workflow_api.json").read_text(encoding="utf-8"))
        workflow = next(item for item in self.index["workflows"] if item["id"] == "scene_background")
        defaults = workflow["fixed_defaults_observed"]
        positive = {tag.strip() for tag in graph["3"]["inputs"]["text"].split(",")}
        negative = {tag.strip() for tag in graph["4"]["inputs"]["text"].split(",")}

        self.assertEqual((graph["5"]["inputs"]["width"], graph["5"]["inputs"]["height"]), (1024, 576))
        self.assertTrue({"scenery", "no_humans", "wide_shot", "landscape", "depth_of_field"} <= positive)
        self.assertNotIn("volumetric_lighting", positive)
        self.assertTrue({"logo", "sign", "school_emblem"} <= negative)
        self.assertEqual(defaults["renpy_display_size"], "1920x1080")
        self.assertEqual(defaults["renpy_textbox_fraction"], 0.28)
        self.assertEqual(defaults["renpy_background_scale"], 1.875)

    def test_scene_event_defaults_encode_static_contract_for_rendered_visual_qa(self):
        graph = json.loads((ROOT / "scene_event_cg/scene_event_cg_workflow_api.json").read_text(encoding="utf-8"))
        workflow = next(item for item in self.index["workflows"] if item["id"] == "scene_event_cg")
        defaults = workflow["fixed_defaults_observed"]
        positive = {tag.strip() for tag in graph["9"]["inputs"]["text"].split(",")}
        negative = {tag.strip() for tag in graph["10"]["inputs"]["text"].split(",")}

        self.assertEqual((graph["11"]["inputs"]["width"], graph["11"]["inputs"]["height"]), (1024, 576))
        self.assertTrue(
            {
                "upper_body",
                "straight-on",
                "facing_viewer",
                "looking_at_viewer",
                "holding_crystal",
                "holding_gem",
                "own_hands_together",
                "hands_up",
                "arms_up",
            }
            <= positive
        )
        self.assertTrue({"full_body", "wide_shot", "cowboy_shot", "profile", "text", "logo", "sign"} <= negative)
        self.assertEqual(defaults["canonical_positive_prompt"], graph["9"]["inputs"]["text"])
        self.assertEqual(defaults["canonical_negative_prompt"], graph["10"]["inputs"]["text"])
        self.assertEqual(defaults["default_seed"], graph["12"]["inputs"]["seed"])
        self.assertEqual(defaults["renpy_display_size"], "1920x1080")
        self.assertEqual(defaults["renpy_textbox_fraction"], 0.28)
        self.assertEqual(defaults["renpy_background_scale"], 1.875)
        self.assertEqual(defaults["minimum_distinct_seeds_per_ab_variant"], 3)
        self.assertEqual(defaults["minimum_total_ab_rendered_candidates"], 6)
        self.assertEqual(defaults["critical_action_top_fraction"], 0.72)
        self.assertAlmostEqual(
            defaults["critical_action_top_fraction"],
            1 - defaults["renpy_textbox_fraction"],
        )
        self.assertTrue(defaults["rendered_visual_qa_required"])
        self.assertFalse(defaults["static_ci_establishes_visual_quality"])
        for name, preset in defaults["recommended_action_presets"].items():
            preset_tags = {tag.strip() for tag in preset.split(",")}
            self.assertTrue(preset_tags.isdisjoint(negative), name)
        experiments = defaults["optional_runtime_experiments"]
        self.assertTrue(experiments["runtime_only"])
        self.assertTrue(experiments["requires_negative_prompt_patch"])
        experiment_tags = {
            tag.strip()
            for preset in experiments["presets"].values()
            for tag in preset.split(",")
        }
        self.assertTrue({"cowboy_shot", "reaching"} <= experiment_tags)
        qa_script = (ROOT / defaults["renpy_qa_script"]).resolve()
        self.assertTrue(qa_script.is_relative_to(ROOT.resolve()))
        self.assertTrue(qa_script.is_file())

    def test_ui_alert_defaults_encode_textless_top_left_renpy_contract(self):
        graph = json.loads(
            (ROOT / "ui_system_alert_frame/ui_system_alert_frame_workflow_api.json").read_text(encoding="utf-8")
        )
        workflow = next(item for item in self.index["workflows"] if item["id"] == "ui_system_alert_frame")
        defaults = workflow["fixed_defaults_observed"]
        positive = {tag.strip() for tag in graph["3"]["inputs"]["text"].split(",")}
        negative = {tag.strip() for tag in graph["4"]["inputs"]["text"].split(",")}

        self.assertEqual((graph["5"]["inputs"]["width"], graph["5"]["inputs"]["height"]), (1024, 576))
        self.assertTrue(
            {"border", "outside_border", "corner", "red_border", "black_border", "gold_border", "no_humans"}
            <= positive
        )
        self.assertTrue(
            {"text", "fake_text", "logo", "label", "icon_(computing)", "emblem", "crest", "medallion"}
            <= negative
        )
        self.assertEqual(defaults["canonical_positive_prompt"], graph["3"]["inputs"]["text"])
        self.assertEqual(defaults["canonical_negative_prompt"], graph["4"]["inputs"]["text"])
        self.assertEqual(defaults["default_seed"], graph["6"]["inputs"]["seed"])
        self.assertEqual(defaults["cfg"], graph["6"]["inputs"]["cfg"])
        self.assertNotIn("placeholder", graph["8"]["inputs"]["filename_prefix"])
        self.assertEqual(defaults["renpy_display_size"], "1920x1080")
        self.assertEqual(defaults["renpy_presentation_mode"], "top_left_nonmodal")
        self.assertEqual(defaults["renpy_panel_size"], [720, 240])
        self.assertEqual(defaults["renpy_panel_margin"], [48, 48])
        self.assertEqual(defaults["minimum_prompt_ab_distinct_seeds"], 3)
        self.assertEqual(defaults["minimum_prompt_ab_total_renders"], 6)
        self.assertTrue(defaults["rendered_visual_qa_required"])
        preview_script = (ROOT / defaults["renpy_preview_script"]).resolve()
        self.assertTrue(preview_script.is_relative_to(ROOT.resolve()))
        self.assertTrue(preview_script.is_file())
        self.assertIn(defaults["renpy_preview_script"], workflow["companion_scripts"])
        template = (ROOT / "ui_system_alert_frame/templates/renpy_screen_snippet.rpy").read_text(encoding="utf-8")
        self.assertIn("modal False", template)
        self.assertIn("xpos 48", template)
        self.assertIn("ypos 48", template)
        self.assertIn("xysize (720, 240)", template)
        self.assertIn("alpha 0.96", template)
        self.assertIn("xmaximum 620", template)

    def test_scene_prop_defaults_encode_renpy_cut_in_contract(self):
        graph = json.loads((ROOT / "scene_prop_cg/scene_prop_cg_workflow_api.json").read_text(encoding="utf-8"))
        workflow = next(item for item in self.index["workflows"] if item["id"] == "scene_prop_cg")
        defaults = workflow["fixed_defaults_observed"]
        positive = {tag.strip() for tag in graph["3"]["inputs"]["text"].split(",")}
        negative = {tag.strip() for tag in graph["4"]["inputs"]["text"].split(",")}

        self.assertEqual((graph["5"]["inputs"]["width"], graph["5"]["inputs"]["height"]), (1024, 576))
        self.assertTrue({"no_humans", "still_life", "object_focus", "depth_of_field"} <= positive)
        self.assertTrue({"duplicate", "cropped", "out_of_frame", "fake_text", "logo", "label"} <= negative)
        self.assertEqual(defaults["renpy_display_size"], "1920x1080")
        self.assertEqual(defaults["renpy_textbox_fraction"], 0.28)
        self.assertEqual(defaults["minimum_seed_candidates"], 3)
        self.assertEqual(defaults["single_object_prompt_shape"], "object_first_compact")
        qa_script = (ROOT / defaults["renpy_qa_script"]).resolve()
        self.assertTrue(qa_script.is_relative_to(ROOT.resolve()))
        self.assertTrue(qa_script.is_file())

    def test_canonical_hash_lock_matches_workflows(self):
        lock = json.loads((ROOT / "dependencies/canonical_hashes.json").read_text(encoding="utf-8"))
        expected_ids = {item["id"] for item in self.index["workflows"]}
        self.assertEqual(set(lock["workflows"]), expected_ids)
        import hashlib

        for workflow in self.index["workflows"]:
            digest = hashlib.sha256((ROOT / workflow["api"]).read_bytes()).hexdigest()
            self.assertEqual(lock["workflows"][workflow["id"]], digest)

    def test_workflow_ids_and_orders_are_unique(self):
        workflows = self.index["workflows"]
        ids = [item["id"] for item in workflows]
        orders = [item["order"] for item in workflows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(orders), len(set(orders)))
        self.assertEqual(sorted(orders), list(range(1, len(workflows) + 1)))


if __name__ == "__main__":
    unittest.main()
