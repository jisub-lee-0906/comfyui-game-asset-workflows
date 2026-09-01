#!/usr/bin/env python3
"""Inspect and download pinned workflow-pack dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

CHUNK_SIZE = 8 * 1024 * 1024


class DependencyError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected_size: int, expected_sha256: str, *, fast: bool = False) -> dict[str, Any]:
    if not path.is_file():
        return {"status": "missing", "path": str(path)}
    size = path.stat().st_size
    if size != expected_size:
        return {"status": "size_mismatch", "path": str(path), "bytes": size}
    if fast:
        return {"status": "size_verified", "path": str(path), "bytes": size}
    digest = sha256_file(path)
    if digest.lower() != expected_sha256.lower():
        return {"status": "hash_mismatch", "path": str(path), "bytes": size, "sha256": digest}
    return {"status": "verified", "path": str(path), "bytes": size, "sha256": digest}


def download_file(url: str, destination: Path, expected_size: int, expected_sha256: str) -> dict[str, Any]:
    destination = Path(destination)
    existing = verify_file(destination, expected_size, expected_sha256)
    if existing["status"] == "verified":
        existing["status"] = "verified_existing"
        return existing

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    if partial.exists() and partial.stat().st_size >= expected_size:
        partial_state = verify_file(partial, expected_size, expected_sha256)
        if partial_state["status"] == "verified":
            os.replace(partial, destination)
            partial_state.update({"status": "recovered_complete_partial", "path": str(destination)})
            return partial_state
        partial.unlink()
    offset = partial.stat().st_size if partial.exists() else 0
    headers = {"User-Agent": "comfyui-game-asset-workflows/1"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            status = getattr(response, "status", None) or response.getcode()
            append = bool(offset and status == 206)
            if append:
                content_range = response.headers.get("Content-Range")
                if not content_range or not content_range.startswith(f"bytes {offset}-"):
                    partial.unlink(missing_ok=True)
                    return download_file(url, destination, expected_size, expected_sha256)
            if not append:
                offset = 0
            with partial.open("ab" if append else "wb") as stream:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    stream.write(chunk)
    except urllib.error.HTTPError as exc:
        exc.close()
        if exc.code == 416 and offset:
            partial.unlink(missing_ok=True)
            return download_file(url, destination, expected_size, expected_sha256)
        raise DependencyError(f"download failed for {url}: {exc}") from exc
    except (OSError, urllib.error.URLError) as exc:
        raise DependencyError(f"download failed for {url}: {exc}") from exc

    result = verify_file(partial, expected_size, expected_sha256)
    if result["status"] != "verified":
        raise DependencyError(f"download verification failed for {destination}: {result}")
    os.replace(partial, destination)
    result.update({"status": "downloaded", "path": str(destination)})
    return result


def _manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DependencyError(f"cannot load manifest {path}: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("model_files"), list):
        raise DependencyError("manifest must contain model_files")
    return value


def _safe_destination(root: Path, relative: str) -> Path:
    root = Path(root).resolve()
    destination = (root / relative).resolve()
    if not destination.is_relative_to(root):
        raise DependencyError(f"manifest destination escapes configured root: {relative}")
    return destination


def inspect_dependencies(
    manifest_path: Path, model_root: Path, repository_root: Path, *, fast: bool = False
) -> dict[str, Any]:
    manifest = _manifest(Path(manifest_path))
    model_root = Path(model_root)
    repository_root = Path(repository_root)
    models = []
    for item in manifest["model_files"]:
        result = verify_file(
            _safe_destination(model_root, item["destination"]), item["bytes"], item["sha256"], fast=fast
        )
        result["id"] = item["id"]
        result["required"] = item.get("required", True)
        models.append(result)
    taxonomy_item = manifest.get("taxonomy")
    taxonomy = None
    if taxonomy_item:
        taxonomy = verify_file(
            _safe_destination(repository_root, taxonomy_item["destination"]),
            taxonomy_item["bytes"],
            taxonomy_item["sha256"],
            fast=fast,
        )
        taxonomy["id"] = taxonomy_item.get("id", "taxonomy")
    valid = {"verified", "size_verified"}
    ok = all((not item["required"]) or item["status"] in valid for item in models)
    if taxonomy and taxonomy["status"] not in valid:
        ok = False
    return {"ok": ok, "models": models, "taxonomy": taxonomy}


def download_manifest(
    manifest_path: Path,
    model_root: Path,
    repository_root: Path,
    *,
    include_models: bool,
    include_taxonomy: bool,
    selected_ids: set[str] | None = None,
) -> dict[str, Any]:
    manifest = _manifest(manifest_path)
    if selected_ids:
        known_ids = {item["id"] for item in manifest["model_files"]}
        unknown_ids = selected_ids - known_ids
        if unknown_ids:
            raise DependencyError(f"unknown dependency id(s): {', '.join(sorted(unknown_ids))}")
    results: list[dict[str, Any]] = []
    if include_models:
        for item in manifest["model_files"]:
            if selected_ids and item["id"] not in selected_ids:
                continue
            result = download_file(
                item["url"], _safe_destination(model_root, item["destination"]), item["bytes"], item["sha256"]
            )
            result["id"] = item["id"]
            results.append(result)
    taxonomy_result = None
    if include_taxonomy:
        item = manifest["taxonomy"]
        taxonomy_result = download_file(
            item["url"], _safe_destination(repository_root, item["destination"]), item["bytes"], item["sha256"]
        )
        taxonomy_result["id"] = item["id"]
    return {"models": results, "taxonomy": taxonomy_result}


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "dependencies/manifest.json")
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=root)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--fast", action="store_true", help="Check sizes without SHA-256")
    download = subparsers.add_parser("download")
    download.add_argument("--models", action="store_true")
    download.add_argument("--taxonomy", action="store_true")
    download.add_argument("--id", action="append", dest="ids")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            report = inspect_dependencies(
                args.manifest, args.model_root, args.repository_root, fast=args.fast
            )
        else:
            include_models = args.models or not args.taxonomy
            include_taxonomy = args.taxonomy or not args.models
            report = download_manifest(
                args.manifest,
                args.model_root,
                args.repository_root,
                include_models=include_models,
                include_taxonomy=include_taxonomy,
                selected_ids=set(args.ids) if args.ids else None,
            )
    except DependencyError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
