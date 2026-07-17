#!/usr/bin/env python3
"""Migrate legacy CEH evidence values out of Reliability_Label."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LEGACY_MAP = {
    "direct": "explicit",
    "inferred": "implicit",
    "converted": "converted",
}


def migrate(data: Any) -> int:
    if not isinstance(data, dict):
        return 0
    records = data.get("records")
    if not isinstance(records, list):
        return 0
    changed = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        tags = record.get("Tags")
        if not isinstance(tags, list):
            continue
        for tag in tags:
            if not isinstance(tag, dict) or "Evidence_Status" in tag:
                continue
            legacy = tag.get("Reliability_Label")
            if legacy not in LEGACY_MAP:
                continue
            tag["Evidence_Status"] = LEGACY_MAP[legacy]
            del tag["Reliability_Label"]
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate CEH direct/inferred/converted evidence fields")
    parser.add_argument("input", type=Path, help="input ceh-record-v2 JSON")
    parser.add_argument("output", nargs="?", type=Path, help="output path; omit only with --in-place")
    parser.add_argument("--in-place", action="store_true", help="replace the input file")
    args = parser.parse_args()

    if args.in_place and args.output:
        parser.error("do not provide output together with --in-place")
    if not args.in_place and not args.output:
        parser.error("provide output or use --in-place")

    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    changed = migrate(data)
    target = args.input if args.in_place else args.output
    assert target is not None
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MIGRATED: {changed} tag(s) -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
