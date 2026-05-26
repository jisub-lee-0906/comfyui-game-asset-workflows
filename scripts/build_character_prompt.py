#!/usr/bin/env python3
"""Build workflow-specific ComfyUI prompt blocks from VN character metadata.

This script intentionally does not submit to ComfyUI. It only composes and
validates prompt text so agents do not hand-copy stale character tags.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

DEFAULT_PACK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = DEFAULT_PACK_ROOT / "danbooru_tag.csv"

POSITIVE_WRAPPER = [
    "masterpiece", "best_quality", "amazing_quality", "4k", "very_aesthetic",
    "high_resolution", "ultra-detailed", "absurdres", "newest", "scenery",
]
POSITIVE_TRAILER = ["BREAK", "depth of field", "volumetric lighting"]
NEGATIVE_DEFAULT = [
    "modern", "recent", "old", "oldest", "cartoon", "graphic", "text",
    "painting", "crayon", "graphite", "abstract", "glitch", "deformed",
    "mutated", "ugly", "disfigured", "long_body", "lowres", "bad_anatomy",
    "bad_hands", "missing_fingers", "extra_digits", "fewer_digits", "cropped",
    "very_displeasing", "(worst_quality, bad_quality:1.2)", "sketch",
    "jpeg_artifacts", "signature", "watermark", "username", "conjoined",
    "bad_ai-generated",
]
WRAPPER_ALLOWLIST = set(POSITIVE_WRAPPER + POSITIVE_TRAILER + NEGATIVE_DEFAULT)

CHARACTER_ALLOWED_WORKFLOWS = {"char_base", "char_expression", "scene_event_cg"}
CHAR_BASE_WRAPPER = [
    "masterpiece", "best_quality", "amazing_quality", "4k", "very_aesthetic",
    "high_resolution", "ultra-detailed", "absurdres", "newest", "1girl", "solo",
]


def load_valid_tags(csv_path: Path) -> set[str]:
    valid: set[str] = set()
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = (row.get("tag") or "").strip()
            if tag:
                valid.add(tag)
            for alias in (row.get("aliases") or "").split():
                alias = alias.strip()
                if alias:
                    valid.add(alias)
    return valid


def dedupe(seq: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in seq:
        item = str(item).strip()
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def validate_tokens(tokens: Iterable[str], valid_tags: set[str], *, field: str) -> list[str]:
    missing = []
    for token in tokens:
        if token in WRAPPER_ALLOWLIST or token in valid_tags:
            continue
        missing.append(token)
    if missing:
        raise SystemExit(f"Invalid {field} token(s): {', '.join(missing)}")
    return list(tokens)


def expression_tags(meta: dict, expression: str | None) -> list[str]:
    if not expression:
        return []
    expr = meta.get("expression_map", {}).get(expression)
    if expr is None:
        known = ", ".join(sorted(meta.get("expression_map", {}).keys()))
        raise SystemExit(f"Unknown expression '{expression}'. Known: {known}")
    return list(expr.get("prompt_tags", []))


def outfit_tags(meta: dict, outfit: str | None) -> tuple[list[str], list[str]]:
    if not outfit:
        outfits = meta.get("outfits", {})
        if len(outfits) == 1:
            outfit = next(iter(outfits.keys()))
        else:
            raise SystemExit("--outfit is required when metadata has multiple/no outfits")
    data = meta.get("outfits", {}).get(outfit)
    if data is None:
        known = ", ".join(sorted(meta.get("outfits", {}).keys()))
        raise SystemExit(f"Unknown outfit '{outfit}'. Known: {known}")
    return list(data.get("positive", [])), list(data.get("negative", []))


def build_prompt(meta: dict, workflow: str, outfit: str | None, expression: str | None, scene_tags: list[str]) -> dict:
    if workflow not in CHARACTER_ALLOWED_WORKFLOWS:
        raise SystemExit(f"Unsupported character workflow '{workflow}'. Use one of: {', '.join(sorted(CHARACTER_ALLOWED_WORKFLOWS))}")

    identity_pos = list(meta.get("identity_anchor", {}).get("positive", []))
    identity_neg = list(meta.get("identity_anchor", {}).get("negative", []))
    outfit_pos, outfit_neg = outfit_tags(meta, outfit)
    expr = expression_tags(meta, expression)
    framing = list(meta.get("framing_defaults", {}).get(workflow, []))
    staging = list(meta.get("staging_defaults", {}).get(workflow, []))

    notes: list[str] = []
    if workflow == "scene_event_cg":
        positive = dedupe(POSITIVE_WRAPPER + identity_pos + outfit_pos + framing + staging + expr + scene_tags + POSITIVE_TRAILER)
        negative = dedupe(NEGATIVE_DEFAULT + identity_neg + outfit_neg)
        notes.append("scene_event_cg: identity + outfit + upper_body framing are fixed; vary expression/scene/seed first; minor outfit drift accepted.")
    elif workflow == "char_base":
        positive = dedupe(CHAR_BASE_WRAPPER + identity_pos + outfit_pos + framing + staging + expr + scene_tags)
        negative = dedupe(NEGATIVE_DEFAULT + identity_neg + outfit_neg)
        notes.append("char_base: same-seed source/outfit route; keep identity/framing tags and seed fixed, vary outfit block + filename_prefix first.")
    else:  # char_expression
        positive = dedupe(expr)
        negative = []
        notes.append("char_expression: face-local expression tags only; do not add outfit/background/camera/body tags here.")
        if scene_tags:
            raise SystemExit("char_expression forbids --scene-tags; use only --expression face-local tags.")

    return {
        "character_id": meta.get("character_id"),
        "workflow": workflow,
        "outfit": outfit,
        "expression": expression,
        "positive_tokens": positive,
        "negative_tokens": negative,
        "positive_prompt": ", ".join(positive),
        "negative_prompt": ", ".join(negative),
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", required=True, type=Path, help="Path to *.asset.json")
    parser.add_argument("--workflow", required=True, choices=sorted(CHARACTER_ALLOWED_WORKFLOWS))
    parser.add_argument("--outfit", default=None)
    parser.add_argument("--expression", default=None)
    parser.add_argument("--scene-tags", nargs="*", default=[])
    parser.add_argument("--danbooru-csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of prompt text")
    args = parser.parse_args()

    meta = json.loads(args.character.read_text(encoding="utf-8"))
    valid = load_valid_tags(args.danbooru_csv)
    result = build_prompt(meta, args.workflow, args.outfit, args.expression, args.scene_tags)
    validate_tokens(result["positive_tokens"], valid, field="positive")
    validate_tokens(result["negative_tokens"], valid, field="negative")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Positive prompt:")
        print(result["positive_prompt"])
        print("\nNegative prompt:")
        print(result["negative_prompt"])
        print("\nNotes:")
        for note in result["notes"]:
            print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
