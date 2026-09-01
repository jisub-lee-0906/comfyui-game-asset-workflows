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
