import hashlib
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from typing import ClassVar
from unittest import mock

from scripts.manage_dependencies import (
    DependencyError,
    download_file,
    download_manifest,
    inspect_dependencies,
)


class DependencyManagerTests(unittest.TestCase):
    def test_download_file_verifies_size_and_sha256(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source.bin"
            source.write_bytes(b"model-data")
            destination = temp / "models/model.bin"
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            result = download_file(source.as_uri(), destination, len(source.read_bytes()), digest)
            self.assertEqual(destination.read_bytes(), source.read_bytes())
            self.assertEqual(result["status"], "downloaded")
            self.assertEqual(result["sha256"], digest)

    def test_download_file_restarts_complete_but_invalid_partial(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            destination = temp / "model.bin"
            partial = temp / "model.bin.part"
            partial.write_bytes(b"bad-data!!")
            expected = b"model-data"
            digest = hashlib.sha256(expected).hexdigest()

            class Response(io.BytesIO):
                status = 200

                def __enter__(self):
                    return self

                def __exit__(self, *_args):
                    self.close()

                def getcode(self):
                    return self.status

            def open_without_range(request, timeout):
                self.assertIsNone(request.get_header("Range"))
                self.assertEqual(timeout, 120)
                return Response(expected)

            with mock.patch("scripts.manage_dependencies.urllib.request.urlopen", side_effect=open_without_range):
                result = download_file("https://example.invalid/model", destination, len(expected), digest)

            self.assertEqual(result["status"], "downloaded")
            self.assertEqual(destination.read_bytes(), expected)

    def test_download_file_restarts_when_server_returns_wrong_content_range(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            destination = temp / "model.bin"
            partial = temp / "model.bin.part"
            partial.write_bytes(b"model")
            expected = b"model-data"
            digest = hashlib.sha256(expected).hexdigest()

            class Response(io.BytesIO):
                def __init__(self, payload, status, content_range=None):
                    super().__init__(payload)
                    self.status = status
                    self.headers = {"Content-Range": content_range} if content_range else {}

                def __enter__(self):
                    return self

                def __exit__(self, *_args):
                    self.close()

                def getcode(self):
                    return self.status

            calls = []

            def respond(request, timeout):
                calls.append(request.get_header("Range"))
                if len(calls) == 1:
                    return Response(b"ignored", 206, "bytes 0-6/10")
                return Response(expected, 200)

            with mock.patch("scripts.manage_dependencies.urllib.request.urlopen", side_effect=respond):
                result = download_file("https://example.invalid/model", destination, len(expected), digest)

            self.assertEqual(calls, ["bytes=5-", None])
            self.assertEqual(result["status"], "downloaded")
            self.assertEqual(destination.read_bytes(), expected)

    def test_download_file_restarts_after_range_not_satisfiable(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            destination = temp / "model.bin"
            partial = temp / "model.bin.part"
            partial.write_bytes(b"model")
            expected = b"model-data"
            digest = hashlib.sha256(expected).hexdigest()

            class Response(io.BytesIO):
                status = 200
                headers: ClassVar[dict[str, str]] = {}

                def __enter__(self):
                    return self

                def __exit__(self, *_args):
                    self.close()

                def getcode(self):
                    return self.status

            calls = []

            def respond(request, timeout):
                calls.append(request.get_header("Range"))
                if len(calls) == 1:
                    raise urllib.error.HTTPError(request.full_url, 416, "range", None, None)
                return Response(expected)

            with mock.patch("scripts.manage_dependencies.urllib.request.urlopen", side_effect=respond):
                result = download_file("https://example.invalid/model", destination, len(expected), digest)

            self.assertEqual(calls, ["bytes=5-", None])
            self.assertEqual(result["status"], "downloaded")

    def test_download_file_reuses_verified_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "source.bin"
            source.write_bytes(b"same-data")
            destination = temp / "model.bin"
            destination.write_bytes(source.read_bytes())
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            result = download_file(source.as_uri(), destination, source.stat().st_size, digest)
            self.assertEqual(result["status"], "verified_existing")

    def test_inspector_reports_missing_and_verified_files(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            models = temp / "models"
            models.mkdir()
            present = models / "checkpoints/present.bin"
            present.parent.mkdir(parents=True)
            present.write_bytes(b"present")
            manifest = {
                "model_files": [
                    {
                        "id": "present",
                        "destination": "checkpoints/present.bin",
                        "bytes": present.stat().st_size,
                        "sha256": hashlib.sha256(present.read_bytes()).hexdigest(),
                        "required": True,
                    },
                    {
                        "id": "missing",
                        "destination": "loras/missing.bin",
                        "bytes": 3,
                        "sha256": hashlib.sha256(b"abc").hexdigest(),
                        "required": True,
                    },
                ],
                "taxonomy": {
                    "destination": "taxonomy.sqlite",
                    "bytes": 1,
                    "sha256": hashlib.sha256(b"x").hexdigest(),
                },
            }
            manifest_path = temp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = inspect_dependencies(manifest_path, models, temp)
            self.assertFalse(report["ok"])
            statuses = {item["id"]: item["status"] for item in report["models"]}
            self.assertEqual(statuses, {"present": "verified", "missing": "missing"})
            self.assertEqual(report["taxonomy"]["status"], "missing")
    def test_download_manifest_rejects_unknown_selected_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            manifest = {
                "model_files": [
                    {
                        "id": "known",
                        "destination": "known.bin",
                        "url": (temp / "source.bin").as_uri(),
                        "bytes": 1,
                        "sha256": hashlib.sha256(b"x").hexdigest(),
                    }
                ]
            }
            manifest_path = temp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(DependencyError, "unknown dependency id"):
                download_manifest(
                    manifest_path,
                    temp / "models",
                    temp,
                    include_models=True,
                    include_taxonomy=False,
                    selected_ids={"typo"},
                )

    def test_inspector_rejects_manifest_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            manifest = {
                "model_files": [
                    {
                        "id": "escape",
                        "destination": "../escape.bin",
                        "bytes": 1,
                        "sha256": hashlib.sha256(b"x").hexdigest(),
                        "required": True,
                    }
                ]
            }
            manifest_path = temp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(DependencyError, "escapes"):
                inspect_dependencies(manifest_path, temp / "models", temp)


if __name__ == "__main__":
    unittest.main()
