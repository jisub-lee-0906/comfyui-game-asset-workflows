import hashlib
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from unittest import mock

from scripts.workflow_pack import (
    ContractError,
    promote_artifact,
    render_workflow,
    submit_runtime,
    validate_repository,
)

ROOT = Path(__file__).resolve().parents[1]


def render_scene_runtime(runtime_dir: Path) -> dict:
    return render_workflow(
        ROOT,
        "scene_background",
        {
            "3.inputs.text": "masterpiece, scenery, no_humans, classroom, sunset",
            "6.inputs.seed": 12345,
            "8.inputs.filename_prefix": "qa/submit_test",
        },
        runtime_dir,
    )


class FakeComfyHandler(BaseHTTPRequestHandler):
    output_record: ClassVar[dict[str, str]] = {"filename": "result.png", "subfolder": "qa", "type": "output"}
    submitted_prompt: ClassVar[dict | None] = None

    def log_message(self, format, *args):
        return

    def do_POST(self):
        if self.path != "/prompt":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length))
        if "prompt" not in payload:
            self.send_error(400)
            return
        type(self).submitted_prompt = payload["prompt"]
        body = json.dumps({"prompt_id": "prompt-1"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/history/prompt-1":
            self.send_error(404)
            return
        body = json.dumps(
            {
                "prompt-1": {
                    "status": {"status_str": "success", "completed": True},
                    "outputs": {"8": {"images": [self.output_record]}},
                }
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class PartialHistoryHandler(FakeComfyHandler):
    history_calls = 0
    artifact_path: Path | None = None

    def do_GET(self):
        if self.path != "/history/prompt-1":
            self.send_error(404)
            return
        type(self).history_calls += 1
        completed = type(self).history_calls >= 2
        if completed and type(self).artifact_path is not None:
            type(self).artifact_path.parent.mkdir(parents=True, exist_ok=True)
            type(self).artifact_path.write_bytes(b"finished")
        body = json.dumps(
            {
                "prompt-1": {
                    "status": {"status_str": "success" if completed else "running", "completed": completed},
                    "outputs": {"8": {"images": [self.output_record]}},
                }
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class WorkflowPackRuntimeTests(unittest.TestCase):
    def test_repository_validator_accepts_canonical_pack(self):
        report = validate_repository(ROOT)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["workflow_count"], 7)

    def test_repository_validator_rejects_index_paths_outside_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "pack"
            root.mkdir()
            outside = Path(temp) / "outside.json"
            outside.write_text(
                json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 1}}}),
                encoding="utf-8",
            )
            (root / "one.md").write_text("# one\n", encoding="utf-8")
            (root / "WORKFLOW_INDEX.json").write_text(
                json.dumps(
                    {
                        "workflows": [
                            {
                                "id": "one",
                                "order": 1,
                                "readme": "one.md",
                                "api": str(outside),
                                "primary_nodes": {},
                                "editable_fields": ["1.inputs.seed"],
                                "placeholders": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            lock_dir = root / "dependencies"
            lock_dir.mkdir()
            (lock_dir / "canonical_hashes.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "workflows": {"one": hashlib.sha256(outside.read_bytes()).hexdigest()},
                    }
                ),
                encoding="utf-8",
            )

            report = validate_repository(root)

            self.assertFalse(report["ok"])
            self.assertIn("api path escapes repository root", "\n".join(report["errors"]))

    def test_repository_validator_enforces_canonical_hash_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            graph_path = root / "one.json"
            graph_path.write_text(
                json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 1}}}),
                encoding="utf-8",
            )
            (root / "one.md").write_text("# one\n", encoding="utf-8")
            (root / "WORKFLOW_INDEX.json").write_text(
                json.dumps(
                    {
                        "workflows": [
                            {
                                "id": "one",
                                "order": 1,
                                "readme": "one.md",
                                "api": "one.json",
                                "primary_nodes": {},
                                "editable_fields": ["1.inputs.seed"],
                                "placeholders": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            lock_dir = root / "dependencies"
            lock_dir.mkdir()
            original_hash = hashlib.sha256(graph_path.read_bytes()).hexdigest()
            (lock_dir / "canonical_hashes.json").write_text(
                json.dumps({"schema_version": 1, "workflows": {"one": original_hash}}),
                encoding="utf-8",
            )
            graph_path.write_text(
                json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 2}}}),
                encoding="utf-8",
            )

            report = validate_repository(root)

            self.assertFalse(report["ok"])
            self.assertIn("canonical hash mismatch", "\n".join(report["errors"]))

    def test_render_rejects_unsafe_workflow_id_before_allocating_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "pack"
            root.mkdir()
            graph = {"1": {"class_type": "KSampler", "inputs": {"seed": 1}}}
            graph_path = root / "one.json"
            graph_path.write_text(json.dumps(graph), encoding="utf-8")
            (root / "one.md").write_text("# one\n", encoding="utf-8")
            unsafe_id = "../escaped"
            (root / "WORKFLOW_INDEX.json").write_text(
                json.dumps(
                    {
                        "workflows": [
                            {
                                "id": unsafe_id,
                                "order": 1,
                                "readme": "one.md",
                                "api": "one.json",
                                "primary_nodes": {},
                                "editable_fields": ["1.inputs.seed"],
                                "placeholders": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            lock_dir = root / "dependencies"
            lock_dir.mkdir()
            (lock_dir / "canonical_hashes.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "workflows": {unsafe_id: hashlib.sha256(graph_path.read_bytes()).hexdigest()},
                    }
                ),
                encoding="utf-8",
            )
            runtime_dir = root / "runtime"

            with self.assertRaisesRegex(ContractError, "unsafe workflow id"):
                render_workflow(root, unsafe_id, {"1.inputs.seed": 2}, runtime_dir)

            self.assertFalse((root / "escaped").exists())

    def test_render_rejects_canonical_file_that_differs_from_hash_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "pack"
            root.mkdir()
            graph_path = root / "one.json"
            graph_path.write_text(
                json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 1}}}),
                encoding="utf-8",
            )
            (root / "one.md").write_text("# one\n", encoding="utf-8")
            (root / "WORKFLOW_INDEX.json").write_text(
                json.dumps(
                    {
                        "workflows": [
                            {
                                "id": "one",
                                "order": 1,
                                "readme": "one.md",
                                "api": "one.json",
                                "primary_nodes": {},
                                "editable_fields": ["1.inputs.seed"],
                                "placeholders": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            lock_dir = root / "dependencies"
            lock_dir.mkdir()
            (lock_dir / "canonical_hashes.json").write_text(
                json.dumps({"schema_version": 1, "workflows": {"one": "0" * 64}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ContractError, "canonical hash mismatch"):
                render_workflow(root, "one", {"1.inputs.seed": 2}, root / "runtime")

    def test_concurrent_renders_allocate_distinct_runtime_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "pack"
            root.mkdir()
            graph_path = root / "one.json"
            graph_path.write_text(
                json.dumps({"1": {"class_type": "KSampler", "inputs": {"seed": 1}}}),
                encoding="utf-8",
            )
            (root / "one.md").write_text("# one\n", encoding="utf-8")
            (root / "WORKFLOW_INDEX.json").write_text(
                json.dumps(
                    {
                        "workflows": [
                            {
                                "id": "one",
                                "order": 1,
                                "readme": "one.md",
                                "api": "one.json",
                                "primary_nodes": {},
                                "editable_fields": ["1.inputs.seed"],
                                "placeholders": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            lock_dir = root / "dependencies"
            lock_dir.mkdir()
            (lock_dir / "canonical_hashes.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "workflows": {"one": hashlib.sha256(graph_path.read_bytes()).hexdigest()},
                    }
                ),
                encoding="utf-8",
            )
            runtime_dir = root / "runtime"
            class FixedDatetime:
                @staticmethod
                def now(_timezone):
                    return datetime(2026, 9, 2, 0, 0, tzinfo=timezone.utc)

            with mock.patch("scripts.workflow_pack.datetime", FixedDatetime), ThreadPoolExecutor(
                max_workers=2
            ) as executor:
                futures = [
                    executor.submit(render_workflow, root, "one", {"1.inputs.seed": seed}, runtime_dir)
                    for seed in (2, 3)
                ]
                results = [future.result() for future in futures]

            runtime_paths = {item["runtime_path"] for item in results}
            self.assertEqual(len(runtime_paths), 2)
            rendered_seeds = {
                json.loads(Path(path).read_text(encoding="utf-8"))["1"]["inputs"]["seed"]
                for path in runtime_paths
            }
            self.assertEqual(rendered_seeds, {2, 3})

    def test_render_rejects_field_outside_editable_contract(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(
            ContractError, "not editable"
        ):
            render_workflow(
                ROOT,
                "char_base",
                {"1.inputs.ckpt_name": "other.safetensors"},
                Path(temp),
            )

    def test_render_patches_copy_and_preserves_canonical_hash(self):
        canonical = ROOT / "scene_background/scene_background_workflow_api.json"
        before = hashlib.sha256(canonical.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            result = render_workflow(
                ROOT,
                "scene_background",
                {
                    "3.inputs.text": "masterpiece, scenery, no_humans, classroom, sunset",
                    "6.inputs.seed": 12345,
                    "8.inputs.filename_prefix": "qa/scene_background_12345",
                },
                Path(temp),
            )
            runtime = Path(result["runtime_path"])
            self.assertTrue(runtime.is_file())
            graph = json.loads(runtime.read_text(encoding="utf-8"))
            self.assertEqual(graph["6"]["inputs"]["seed"], 12345)
            self.assertEqual(before, hashlib.sha256(canonical.read_bytes()).hexdigest())
            self.assertEqual(result["canonical_sha256"], before)
            self.assertEqual(result["unresolved_placeholders"], [])

    def test_render_rejects_unresolved_placeholders(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(
            ContractError, "unresolved placeholders"
        ):
            render_workflow(ROOT, "scene_prop_cg", {}, Path(temp))

    def test_submit_rejects_runtime_tampered_after_metadata_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            rendered = render_workflow(
                ROOT,
                "scene_background",
                {
                    "3.inputs.text": "masterpiece, scenery, no_humans, classroom, sunset",
                    "6.inputs.seed": 12345,
                    "8.inputs.filename_prefix": "qa/tamper_test",
                },
                temp,
            )
            runtime = Path(rendered["runtime_path"])
            trusted_runtime_sha256 = rendered["runtime_sha256"]
            graph = json.loads(runtime.read_text(encoding="utf-8"))
            graph["6"]["inputs"]["seed"] = 99999
            runtime.write_text(json.dumps(graph), encoding="utf-8")
            metadata_path = runtime.with_suffix(".metadata.json")
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["edits"]["6.inputs.seed"] = 99999
            metadata["runtime_sha256"] = hashlib.sha256(runtime.read_bytes()).hexdigest()
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            with mock.patch("scripts.workflow_pack.urllib.request.urlopen") as urlopen, self.assertRaisesRegex(
                ContractError, "runtime SHA-256 differs from trusted render digest"
            ):
                submit_runtime(
                    runtime,
                    "http://127.0.0.1:8188",
                    temp / "output",
                    root=ROOT,
                    expected_runtime_sha256=trusted_runtime_sha256,
                )
            urlopen.assert_not_called()

    def test_submit_rejects_non_positive_timing_values_before_network_call(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Path(temp) / "runtime.json"
            runtime.write_text(
                json.dumps({"1": {"class_type": "SaveImage", "inputs": {}}}),
                encoding="utf-8",
            )
            cases = ((0, 1, "timeout"), (1, 0, "poll_interval"))
            with mock.patch("scripts.workflow_pack.urllib.request.urlopen") as urlopen:
                for timeout, poll_interval, field in cases:
                    with self.subTest(field=field), self.assertRaisesRegex(
                        ContractError, f"{field} must be positive"
                    ):
                        submit_runtime(
                            runtime,
                            "http://127.0.0.1:8188",
                            Path(temp) / "output",
                            root=ROOT,
                            expected_runtime_sha256="0" * 64,
                            timeout=timeout,
                            poll_interval=poll_interval,
                        )
                urlopen.assert_not_called()

    def test_submit_hashes_parses_and_posts_one_runtime_byte_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            rendered = render_workflow(
                ROOT,
                "scene_background",
                {
                    "3.inputs.text": "masterpiece, scenery, no_humans, classroom, sunset",
                    "6.inputs.seed": 12345,
                    "8.inputs.filename_prefix": "qa/snapshot_test",
                },
                temp,
            )
            runtime = Path(rendered["runtime_path"])
            output_root = temp / "output"
            artifact = output_root / "qa/result.png"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"png")
            original_read_bytes = Path.read_bytes
            runtime_reads = 0

            def read_and_replace(path):
                nonlocal runtime_reads
                data = original_read_bytes(path)
                if path.resolve() == runtime.resolve():
                    runtime_reads += 1
                    replacement = json.loads(data)
                    replacement["6"]["inputs"]["seed"] = 99999
                    runtime.write_text(json.dumps(replacement), encoding="utf-8")
                return data

            FakeComfyHandler.submitted_prompt = None
            server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfyHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with mock.patch.object(Path, "read_bytes", read_and_replace):
                    report = submit_runtime(
                        runtime,
                        f"http://127.0.0.1:{server.server_port}",
                        output_root,
                        root=ROOT,
                        expected_runtime_sha256=rendered["runtime_sha256"],
                        timeout=2,
                        poll_interval=0.01,
                    )
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
            self.assertEqual(runtime_reads, 1)
            self.assertEqual(report["runtime_sha256"], rendered["runtime_sha256"])
            submitted_prompt = FakeComfyHandler.submitted_prompt
            self.assertIsNotNone(submitted_prompt)
            assert submitted_prompt is not None
            self.assertEqual(submitted_prompt["6"]["inputs"]["seed"], 12345)
            self.assertEqual(json.loads(runtime.read_text(encoding="utf-8"))["6"]["inputs"]["seed"], 99999)

    def test_submit_waits_for_history_and_verifies_exact_output_file(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            rendered = render_scene_runtime(temp)
            runtime = Path(rendered["runtime_path"])
            output_root = temp / "output"
            artifact = output_root / "qa/result.png"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"png")
            server = ThreadingHTTPServer(("127.0.0.1", 0), FakeComfyHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                report = submit_runtime(
                    runtime,
                    f"http://127.0.0.1:{server.server_port}",
                    output_root,
                    root=ROOT,
                    expected_runtime_sha256=rendered["runtime_sha256"],
                    timeout=2,
                    poll_interval=0.01,
                )
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
            self.assertEqual(report["prompt_id"], "prompt-1")
            self.assertEqual(report["artifacts"][0]["path"], str(artifact.resolve()))
            self.assertEqual(report["artifacts"][0]["sha256"], hashlib.sha256(b"png").hexdigest())

    def test_submit_waits_for_explicit_completion_before_checking_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            rendered = render_scene_runtime(temp)
            runtime = Path(rendered["runtime_path"])
            output_root = temp / "output"
            artifact = output_root / "qa/result.png"
            PartialHistoryHandler.history_calls = 0
            PartialHistoryHandler.artifact_path = artifact
            server = ThreadingHTTPServer(("127.0.0.1", 0), PartialHistoryHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                report = submit_runtime(
                    runtime,
                    f"http://127.0.0.1:{server.server_port}",
                    output_root,
                    root=ROOT,
                    expected_runtime_sha256=rendered["runtime_sha256"],
                    timeout=2,
                    poll_interval=0.01,
                )
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
            self.assertGreaterEqual(PartialHistoryHandler.history_calls, 2)
            self.assertEqual(report["artifacts"][0]["sha256"], hashlib.sha256(b"finished").hexdigest())

    def test_promote_rejects_non_object_qa_json_with_contract_error(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            candidate = temp / "candidate.png"
            candidate.write_bytes(b"candidate")
            qa = temp / "qa.json"
            qa.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "QA document must be a JSON object"):
                promote_artifact(candidate, temp / "game/image.png", qa)

    def test_promote_requires_explicit_approved_qa(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            candidate = temp / "candidate.png"
            candidate.write_bytes(b"candidate")
            qa = temp / "qa.json"
            qa.write_text(json.dumps({"status": "candidate"}), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "approved"):
                promote_artifact(candidate, temp / "game/image.png", qa)

    def test_promote_preserves_existing_destination_when_copy_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            candidate = temp / "candidate.ogg"
            candidate.write_bytes(b"new-approved-audio")
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            qa = temp / "qa.json"
            qa.write_text(
                json.dumps({"status": "approved", "artifact_sha256": digest}),
                encoding="utf-8",
            )
            destination = temp / "game/audio.ogg"
            destination.parent.mkdir(parents=True)
            destination.write_bytes(b"existing-approved-audio")

            def interrupted_copy(_source, target):
                Path(target).write_bytes(b"partial")
                raise OSError("simulated interrupted copy")

            with mock.patch(
                "scripts.workflow_pack.shutil.copy2", side_effect=interrupted_copy
            ), self.assertRaises(OSError):
                promote_artifact(candidate, destination, qa)

            self.assertEqual(destination.read_bytes(), b"existing-approved-audio")

    def test_promote_copies_approved_artifact_and_verifies_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            candidate = temp / "candidate.ogg"
            candidate.write_bytes(b"approved-audio")
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            qa = temp / "qa.json"
            qa.write_text(
                json.dumps({"status": "approved", "artifact_sha256": digest}),
                encoding="utf-8",
            )
            destination = temp / "game/audio.ogg"
            report = promote_artifact(candidate, destination, qa)
            self.assertTrue(destination.is_file())
            self.assertEqual(destination.read_bytes(), candidate.read_bytes())
            self.assertEqual(report["sha256"], digest)


if __name__ == "__main__":
    unittest.main()
