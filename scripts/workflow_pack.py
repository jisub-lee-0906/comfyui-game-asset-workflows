#!/usr/bin/env python3
"""Validate, render, and safely promote ComfyUI workflow artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLACEHOLDER_RE = re.compile(r"TEMPLATE_[A-Za-z0-9_./-]+|\{[^{}\n]*[가-힣][^{}\n]*\}")
WORKFLOW_ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class ContractError(ValueError):
    """Raised when an operation violates the workflow-pack contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot load JSON {path}: {exc}") from exc


def _index(root: Path) -> dict[str, Any]:
    value = _load_json(root / "WORKFLOW_INDEX.json")
    if not isinstance(value, dict) or not isinstance(value.get("workflows"), list):
        raise ContractError("WORKFLOW_INDEX.json must contain a workflows list")
    return value


def _safe_repo_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{label} path must be a non-empty relative string")
    relative = Path(value)
    if relative.is_absolute():
        raise ContractError(f"{label} path escapes repository root: {value}")
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ContractError(f"{label} path escapes repository root: {value}")
    return candidate


def _require_safe_workflow_id(workflow_id: Any) -> str:
    if not isinstance(workflow_id, str) or not WORKFLOW_ID_RE.fullmatch(workflow_id):
        raise ContractError(f"unsafe workflow id: {workflow_id!r}")
    return workflow_id


def _workflow(index: dict[str, Any], workflow_id: str) -> dict[str, Any]:
    _require_safe_workflow_id(workflow_id)
    matches = [item for item in index["workflows"] if item.get("id") == workflow_id]
    if len(matches) != 1:
        raise ContractError(f"unknown or duplicate workflow id: {workflow_id}")
    return matches[0]


def _get_path(value: Any, dotted_path: str) -> Any:
    current = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ContractError(f"path does not exist: {dotted_path}")
        current = current[part]
    return current


def _set_path(value: Any, dotted_path: str, replacement: Any) -> None:
    parts = dotted_path.split(".")
    current = value
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current:
            raise ContractError(f"path does not exist: {dotted_path}")
        current = current[part]
    if not isinstance(current, dict) or parts[-1] not in current:
        raise ContractError(f"path does not exist: {dotted_path}")
    current[parts[-1]] = replacement


def discover_placeholders(graph: dict[str, Any]) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for node_id, node in graph.items():
        for name, value in node.get("inputs", {}).items():
            if not isinstance(value, str):
                continue
            for token in PLACEHOLDER_RE.findall(value):
                found.append(
                    {"node_id": node_id, "path": f"{node_id}.inputs.{name}", "token": token}
                )
    return found


def _graph_cycle_errors(edges: dict[str, set[str]], workflow_id: str) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            errors.append(f"{workflow_id}: cycle detected at node {node_id}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for dependency in edges[node_id]:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in edges:
        visit(node_id)
    return errors


def validate_repository(root: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    errors: list[str] = []
    try:
        index = _index(root)
    except ContractError as exc:
        return {"ok": False, "workflow_count": 0, "errors": [str(exc)]}

    workflows = index["workflows"]
    ids = [item.get("id") for item in workflows]
    orders = [item.get("order") for item in workflows]
    locked_hashes: dict[str, str] = {}
    try:
        hash_lock = _load_json(root / "dependencies/canonical_hashes.json")
        if not isinstance(hash_lock, dict) or not isinstance(hash_lock.get("workflows"), dict):
            raise ContractError("canonical_hashes.json must contain a workflows object")
        locked_hashes = hash_lock["workflows"]
    except ContractError as exc:
        errors.append(str(exc))
    if set(locked_hashes) != set(ids):
        errors.append("canonical hash lock workflow ids differ from WORKFLOW_INDEX.json")
    if len(ids) != len(set(ids)):
        errors.append("workflow ids are not unique")
    for workflow_id in ids:
        try:
            _require_safe_workflow_id(workflow_id)
        except ContractError as exc:
            errors.append(str(exc))
    if sorted(orders) != list(range(1, len(workflows) + 1)):
        errors.append("workflow orders must be contiguous starting at 1")

    for workflow in workflows:
        workflow_id = workflow.get("id", "<missing>")
        resolved_paths: dict[str, Path] = {}
        for key in ("readme", "api"):
            try:
                candidate = _safe_repo_path(root, workflow.get(key), key)
            except ContractError as exc:
                errors.append(f"{workflow_id}: {exc}")
                continue
            resolved_paths[key] = candidate
            if not candidate.is_file():
                errors.append(f"{workflow_id}: missing {key}: {candidate}")
        api = resolved_paths.get("api")
        if api is None or not api.is_file():
            continue
        try:
            graph = _load_json(api)
        except ContractError as exc:
            errors.append(str(exc))
            continue
        if not isinstance(graph, dict):
            errors.append(f"{workflow_id}: graph must be a JSON object")
            continue
        actual_hash = sha256_file(api)
        if locked_hashes.get(workflow_id) != actual_hash:
            errors.append(f"{workflow_id}: canonical hash mismatch")
        for path in workflow.get("editable_fields", []):
            try:
                _get_path(graph, path)
            except ContractError as exc:
                errors.append(f"{workflow_id}: {exc}")
        for role, node_id in workflow.get("primary_nodes", {}).items():
            if node_id not in graph:
                errors.append(f"{workflow_id}: primary node {role}={node_id} is missing")

        edges: dict[str, set[str]] = {node_id: set() for node_id in graph}
        for node_id, node in graph.items():
            for value in node.get("inputs", {}).values():
                if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                    if value[0] not in graph:
                        errors.append(f"{workflow_id}: node {node_id} references missing {value[0]}")
                    else:
                        edges[node_id].add(value[0])
        errors.extend(_graph_cycle_errors(edges, workflow_id))

        declared = workflow.get("placeholders", [])
        actual = discover_placeholders(graph)
        normalize = lambda items: sorted(
            (item.get("node_id"), item.get("path"), item.get("token")) for item in items
        )
        if normalize(declared) != normalize(actual):
            errors.append(f"{workflow_id}: placeholder declaration differs from graph")

    return {"ok": not errors, "workflow_count": len(workflows), "errors": errors}


def render_workflow(
    root: Path | str,
    workflow_id: str,
    edits: dict[str, Any],
    runtime_dir: Path | str,
) -> dict[str, Any]:
    root = Path(root).resolve()
    runtime_dir = Path(runtime_dir).resolve()
    index = _index(root)
    workflow = _workflow(index, workflow_id)
    canonical = _safe_repo_path(root, workflow.get("api"), "api")
    hash_lock = _load_json(root / "dependencies/canonical_hashes.json")
    if not isinstance(hash_lock, dict) or not isinstance(hash_lock.get("workflows"), dict):
        raise ContractError("canonical_hashes.json must contain a workflows object")
    before_hash = sha256_file(canonical)
    if hash_lock["workflows"].get(workflow_id) != before_hash:
        raise ContractError(f"{workflow_id}: canonical hash mismatch")
    graph = _load_json(canonical)
    editable = set(workflow.get("editable_fields", []))
    for path, replacement in edits.items():
        if path not in editable:
            raise ContractError(f"field is not editable for {workflow_id}: {path}")
        _set_path(graph, path, replacement)
    unresolved = discover_placeholders(graph)
    if unresolved:
        details = ", ".join(f"{item['path']}={item['token']}" for item in unresolved)
        raise ContractError(f"unresolved placeholders: {details}")
    after_hash = sha256_file(canonical)
    if after_hash != before_hash:
        raise ContractError("canonical workflow changed during runtime rendering")

    runtime_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runtime_payload = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    counter = 0
    while True:
        suffix = "" if counter == 0 else f"_{counter}"
        destination = runtime_dir / f"{workflow_id}_{stamp}{suffix}.json"
        try:
            with destination.open("x", encoding="utf-8") as stream:
                stream.write(runtime_payload)
        except FileExistsError:
            counter += 1
            continue
        break
    runtime_hash = sha256_file(destination)
    metadata = {
        "workflow_id": workflow_id,
        "canonical_path": str(canonical),
        "canonical_sha256": before_hash,
        "runtime_path": str(destination),
        "runtime_sha256": runtime_hash,
        "edits": edits,
        "unresolved_placeholders": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    destination.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def submit_runtime(
    runtime_path: Path | str,
    comfyui_url: str,
    output_root: Path | str,
    *,
    root: Path | str,
    expected_runtime_sha256: str,
    timeout: float = 600,
    poll_interval: float = 1,
) -> dict[str, Any]:
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise ContractError("timeout must be positive")
    if (
        not isinstance(poll_interval, (int, float))
        or isinstance(poll_interval, bool)
        or poll_interval <= 0
    ):
        raise ContractError("poll_interval must be positive")
    runtime_path = Path(runtime_path).resolve()
    output_root = Path(output_root).resolve()
    if not isinstance(expected_runtime_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", expected_runtime_sha256
    ):
        raise ContractError("expected_runtime_sha256 must be a lowercase SHA-256 digest")
    try:
        runtime_bytes = runtime_path.read_bytes()
        graph = json.loads(runtime_bytes)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot load JSON {runtime_path}: {exc}") from exc
    runtime_hash = hashlib.sha256(runtime_bytes).hexdigest()
    if runtime_hash != expected_runtime_sha256:
        raise ContractError("runtime SHA-256 differs from trusted render digest")
    metadata_path = runtime_path.with_suffix(".metadata.json")
    metadata = _load_json(metadata_path)
    if not isinstance(metadata, dict):
        raise ContractError("runtime metadata must be a JSON object")
    recorded_path = metadata.get("runtime_path")
    if not isinstance(recorded_path, str) or Path(recorded_path).resolve() != runtime_path:
        raise ContractError("runtime path does not match metadata")
    recorded_hash = metadata.get("runtime_sha256")
    if not isinstance(recorded_hash, str) or runtime_hash != recorded_hash:
        raise ContractError("runtime SHA-256 does not match metadata")

    root = Path(root).resolve()
    workflow_id = metadata.get("workflow_id")
    if not isinstance(workflow_id, str):
        raise ContractError("runtime metadata workflow_id must be a string")
    workflow = _workflow(_index(root), workflow_id)
    canonical = _safe_repo_path(root, workflow.get("api"), "api")
    recorded_canonical = metadata.get("canonical_path")
    if not isinstance(recorded_canonical, str) or Path(recorded_canonical).resolve() != canonical:
        raise ContractError("canonical path does not match repository workflow index")
    canonical_hash = sha256_file(canonical)
    hash_lock = _load_json(root / "dependencies/canonical_hashes.json")
    if not isinstance(hash_lock, dict) or not isinstance(hash_lock.get("workflows"), dict):
        raise ContractError("canonical_hashes.json must contain a workflows object")
    if (
        metadata.get("canonical_sha256") != canonical_hash
        or hash_lock["workflows"].get(workflow_id) != canonical_hash
    ):
        raise ContractError(f"{workflow_id}: canonical hash mismatch")
    edits = metadata.get("edits")
    if not isinstance(edits, dict):
        raise ContractError("runtime metadata edits must be a JSON object")
    expected_graph = _load_json(canonical)
    editable = set(workflow.get("editable_fields", []))
    for path, replacement in edits.items():
        if path not in editable:
            raise ContractError(f"field is not editable for {workflow_id}: {path}")
        _set_path(expected_graph, path, replacement)

    if graph != expected_graph:
        raise ContractError("runtime payload does not match canonical workflow and recorded edits")
    unresolved = discover_placeholders(graph)
    if unresolved:
        raise ContractError("runtime payload contains unresolved placeholders")
    payload = json.dumps({"prompt": graph}).encode("utf-8")
    request = urllib.request.Request(
        comfyui_url.rstrip("/") + "/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=min(timeout, 30)) as response:
            submission = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ContractError(f"ComfyUI submission failed: {exc}") from exc
    prompt_id = submission.get("prompt_id")
    if not isinstance(prompt_id, str) or not prompt_id:
        raise ContractError(f"ComfyUI did not return prompt_id: {submission}")

    deadline = time.monotonic() + timeout
    record = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                comfyui_url.rstrip("/") + f"/history/{prompt_id}", timeout=min(poll_interval + 5, 30)
            ) as response:
                history = json.load(response)
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            if time.monotonic() + poll_interval >= deadline:
                raise ContractError(f"ComfyUI history lookup failed: {exc}") from exc
            time.sleep(poll_interval)
            continue
        candidate = history.get(prompt_id)
        if candidate:
            status = candidate.get("status", {})
            if status.get("status_str") == "error":
                raise ContractError(f"ComfyUI execution failed for {prompt_id}: {status}")
            if status.get("completed") is True:
                record = candidate
                break
        time.sleep(poll_interval)
    if record is None:
        raise ContractError(f"timed out waiting for ComfyUI prompt {prompt_id}")

    artifacts: list[dict[str, Any]] = []
    for node_id, output in record.get("outputs", {}).items():
        for values in output.values():
            if not isinstance(values, list):
                continue
            for item in values:
                if not isinstance(item, dict) or not item.get("filename"):
                    continue
                if item.get("type", "output") != "output":
                    continue
                relative = Path(item.get("subfolder", "")) / item["filename"]
                path = (output_root / relative).resolve()
                if not path.is_relative_to(output_root):
                    raise ContractError(f"history output escapes output root: {relative}")
                if not path.is_file():
                    raise ContractError(f"history output file does not exist: {path}")
                artifacts.append(
                    {
                        "node_id": node_id,
                        "path": str(path),
                        "bytes": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
    if not artifacts:
        raise ContractError(f"ComfyUI prompt {prompt_id} completed without verifiable output artifacts")
    return {
        "prompt_id": prompt_id,
        "runtime_path": str(runtime_path),
        "runtime_sha256": runtime_hash,
        "artifacts": artifacts,
    }


def promote_artifact(
    candidate: Path | str, destination: Path | str, qa_path: Path | str
) -> dict[str, Any]:
    candidate = Path(candidate).resolve()
    destination = Path(destination).resolve()
    qa_path = Path(qa_path).resolve()
    if not candidate.is_file():
        raise ContractError(f"candidate does not exist: {candidate}")
    qa = _load_json(qa_path)
    if not isinstance(qa, dict):
        raise ContractError("QA document must be a JSON object")
    if qa.get("status") != "approved":
        raise ContractError("QA status must be explicitly approved before promotion")
    digest = sha256_file(candidate)
    if qa.get("artifact_sha256") != digest:
        raise ContractError("QA artifact_sha256 does not match candidate")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        shutil.copy2(candidate, temporary_path)
        if sha256_file(temporary_path) != digest:
            raise ContractError("promoted artifact hash verification failed")
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return {"source": str(candidate), "destination": str(destination), "sha256": digest}


def _parse_edits(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    if not isinstance(value, dict):
        raise ContractError("edits file must be a JSON object mapping dotted paths to values")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    render = subparsers.add_parser("render")
    render.add_argument("workflow_id")
    render.add_argument("--edits", type=Path, required=True)
    render.add_argument(
        "--runtime-dir",
        type=Path,
        default=Path(os.environ.get("WORKFLOW_RUNTIME_DIR", ".runtime")),
    )
    submit = subparsers.add_parser("submit")
    submit.add_argument("runtime", type=Path)
    submit.add_argument(
        "--runtime-sha256",
        required=True,
        help="Exact runtime_sha256 returned by the trusted render step",
    )
    submit.add_argument(
        "--url", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
    )
    submit.add_argument(
        "--output-root",
        type=Path,
        default=os.environ.get("COMFYUI_OUTPUT_DIR"),
        required="COMFYUI_OUTPUT_DIR" not in os.environ,
    )
    submit.add_argument("--timeout", type=float, default=600)
    promote = subparsers.add_parser("promote")
    promote.add_argument("candidate", type=Path)
    promote.add_argument("destination", type=Path)
    promote.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            result = validate_repository(args.root)
        elif args.command == "render":
            result = render_workflow(args.root, args.workflow_id, _parse_edits(args.edits), args.runtime_dir)
        elif args.command == "submit":
            result = submit_runtime(
                args.runtime,
                args.url,
                args.output_root,
                root=args.root,
                expected_runtime_sha256=args.runtime_sha256,
                timeout=args.timeout,
            )
        else:
            result = promote_artifact(args.candidate, args.destination, args.qa)
    except ContractError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
