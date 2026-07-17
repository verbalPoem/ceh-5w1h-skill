#!/usr/bin/env python3
"""Validate CEH record-first 5W1H output.

Usage:
  python validate_ceh_record_output.py output.json
  type output.json | python validate_ceh_record_output.py -
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ceh-record-v2"
LABELS = ("WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW")
ROLE_KEYS = tuple(label.lower() for label in LABELS)
ROLE_CAPS = {
    "WHO": 5,
    "WHAT": 2,
    "WHEN": 1,
    "WHERE": 1,
    "WHY": 2,
    "HOW": 2,
}
TOTAL_TAG_CAP = 12
EVIDENCE_STATUSES = {"explicit", "implicit", "converted"}
RELIABILITY_LABELS = {"reliable", "partially_reliable", "unreliable"}
LEGACY_EVIDENCE_LABELS = {"direct", "inferred", "converted"}


def normalize(text: str) -> str:
    """Normalize text for duplicate checks without changing output text."""
    value = re.sub(r"\s+", " ", text.casefold().strip())
    return re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)


def load_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def type_name(value: Any) -> str:
    return type(value).__name__


def require_dict(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object, got {type_name(value)}")
        return {}
    return value


def require_list(value: Any, path: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{path} must be a list, got {type_name(value)}")
        return []
    return value


def require_string(value: Any, path: str, errors: list[str]) -> str:
    if not isinstance(value, str):
        errors.append(f"{path} must be a string, got {type_name(value)}")
        return ""
    return value


def require_keys(obj: dict[str, Any], keys: tuple[str, ...], path: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{path}.{key} is required")


def validate_span(
    text: str,
    obj: dict[str, Any],
    path: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> None:
    require_keys(obj, ("Tag_Text", "Tag_Start", "Tag_End"), path, errors)
    tag_text = require_string(obj.get("Tag_Text"), f"{path}.Tag_Text", errors)
    start = obj.get("Tag_Start")
    end = obj.get("Tag_End")

    if tag_text == "" and allow_empty:
        if start not in (0, None) or end not in (0, None):
            errors.append(f"{path} empty trigger must use 0/null offsets")
        return

    if tag_text == "":
        errors.append(f"{path}.Tag_Text must not be empty")
        return

    if not isinstance(start, int) or not isinstance(end, int):
        errors.append(f"{path}.Tag_Start and Tag_End must be integers")
        return
    if start < 0 or end < start or end > len(text):
        errors.append(f"{path} offsets out of range: start={start}, end={end}, text_len={len(text)}")
        return
    actual = text[start:end]
    if actual != tag_text:
        errors.append(f"{path} span mismatch: expected {tag_text!r}, got Text[{start}:{end}]={actual!r}")


def validate_tags(
    record: dict[str, Any],
    record_path: str,
    errors: list[str],
    *,
    enforce_caps: bool,
    strict_missing: bool,
) -> int:
    text = record.get("Text", "")
    tags = require_list(record.get("Tags"), f"{record_path}.Tags", errors)
    seen: dict[tuple[str, str], int] = {}
    role_counts = {label: 0 for label in LABELS}

    for idx, raw_tag in enumerate(tags):
        tag_path = f"{record_path}.Tags[{idx}]"
        tag = require_dict(raw_tag, tag_path, errors)
        require_keys(
            tag,
            ("Tag_Text", "Tag_Start", "Tag_End", "5W1H_Label"),
            tag_path,
            errors,
        )
        label = tag.get("5W1H_Label")
        if label not in LABELS:
            errors.append(f"{tag_path}.5W1H_Label must be one of {', '.join(LABELS)}")
        else:
            role_counts[label] += 1
        evidence_status = tag.get("Evidence_Status")
        reliability_label = tag.get("Reliability_Label")
        uses_legacy_evidence = evidence_status is None and reliability_label in LEGACY_EVIDENCE_LABELS
        if evidence_status is None and not uses_legacy_evidence:
            errors.append(
                f"{tag_path}.Evidence_Status is required and must be one of "
                f"{', '.join(sorted(EVIDENCE_STATUSES))}"
            )
        elif evidence_status is not None and evidence_status not in EVIDENCE_STATUSES:
            errors.append(
                f"{tag_path}.Evidence_Status must be one of "
                f"{', '.join(sorted(EVIDENCE_STATUSES))}"
            )
        if reliability_label is not None and not uses_legacy_evidence and reliability_label not in RELIABILITY_LABELS:
            errors.append(
                f"{tag_path}.Reliability_Label must be one of "
                f"{', '.join(sorted(RELIABILITY_LABELS))}"
            )
        validate_span(text, tag, tag_path, errors)
        if isinstance(label, str) and isinstance(tag.get("Tag_Text"), str):
            key = (label, normalize(tag["Tag_Text"]))
            if key in seen:
                errors.append(f"{tag_path} duplicates {record_path}.Tags[{seen[key]}] by label+text")
            else:
                seen[key] = idx

    if enforce_caps:
        if len(tags) > TOTAL_TAG_CAP:
            errors.append(f"{record_path}.Tags has {len(tags)} tags; cap is {TOTAL_TAG_CAP}")
        for label, cap in ROLE_CAPS.items():
            if role_counts[label] > cap:
                errors.append(f"{record_path}.Tags has {role_counts[label]} {label} tags; cap is {cap}")

    missing = require_list(record.get("Missing"), f"{record_path}.Missing", errors)
    missing_set = set()
    for item in missing:
        if item not in LABELS:
            errors.append(f"{record_path}.Missing contains invalid label {item!r}")
        else:
            missing_set.add(item)
    if strict_missing:
        expected_missing = {label for label in LABELS if role_counts[label] == 0}
        if missing_set != expected_missing:
            errors.append(
                f"{record_path}.Missing must equal roles without tags: "
                f"expected {sorted(expected_missing)}, got {sorted(missing_set)}"
            )

    return len(tags)


def validate_hyperedge(record: dict[str, Any], record_path: str, errors: list[str]) -> None:
    tags = require_list(record.get("Tags"), f"{record_path}.Tags", errors)
    root_event = require_dict(record.get("Root_Event"), f"{record_path}.Root_Event", errors)
    hyperedge = require_dict(record.get("Event_Hyperedge"), f"{record_path}.Event_Hyperedge", errors)
    if hyperedge.get("event") != root_event.get("Event_Id"):
        errors.append(f"{record_path}.Event_Hyperedge.event must match Root_Event.Event_Id")

    referenced: set[int] = set()
    for role in ROLE_KEYS:
        indexes = require_list(hyperedge.get(role), f"{record_path}.Event_Hyperedge.{role}", errors)
        for index in indexes:
            if not isinstance(index, int):
                errors.append(f"{record_path}.Event_Hyperedge.{role} contains non-integer index {index!r}")
                continue
            if index < 0 or index >= len(tags):
                errors.append(f"{record_path}.Event_Hyperedge.{role} index {index} out of range")
                continue
            referenced.add(index)
            tag = require_dict(tags[index], f"{record_path}.Tags[{index}]", errors)
            expected_label = role.upper()
            if tag.get("5W1H_Label") != expected_label:
                errors.append(
                    f"{record_path}.Event_Hyperedge.{role}[{index}] points to "
                    f"{tag.get('5W1H_Label')}, expected {expected_label}"
                )

    for idx in range(len(tags)):
        if idx not in referenced:
            errors.append(f"{record_path}.Tags[{idx}] is not referenced by Event_Hyperedge")


def validate_record(
    record: Any,
    idx: int,
    errors: list[str],
    *,
    enforce_caps: bool,
    strict_missing: bool,
) -> int:
    record_path = f"records[{idx}]"
    obj = require_dict(record, record_path, errors)
    require_keys(obj, ("Id", "Text", "Root_Event", "Tags", "Missing", "Event_Hyperedge"), record_path, errors)
    require_string(obj.get("Id"), f"{record_path}.Id", errors)
    text = require_string(obj.get("Text"), f"{record_path}.Text", errors)

    root_event = require_dict(obj.get("Root_Event"), f"{record_path}.Root_Event", errors)
    require_keys(root_event, ("Event_Id", "Event_Text", "Trigger"), f"{record_path}.Root_Event", errors)
    require_string(root_event.get("Event_Id"), f"{record_path}.Root_Event.Event_Id", errors)
    require_string(root_event.get("Event_Text"), f"{record_path}.Root_Event.Event_Text", errors)
    trigger = require_dict(root_event.get("Trigger"), f"{record_path}.Root_Event.Trigger", errors)
    validate_span(text, trigger, f"{record_path}.Root_Event.Trigger", errors, allow_empty=True)

    tag_count = validate_tags(obj, record_path, errors, enforce_caps=enforce_caps, strict_missing=strict_missing)
    validate_hyperedge(obj, record_path, errors)
    return tag_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate CEH record-first 5W1H JSON.")
    parser.add_argument("json_path", help="JSON file path, or '-' for stdin")
    parser.add_argument("--no-caps", action="store_true", help="do not enforce default tag caps")
    parser.add_argument("--loose-missing", action="store_true", help="do not require Missing to exactly match absent roles")
    parser.add_argument("--max-errors", type=int, default=40, help="maximum errors to print")
    args = parser.parse_args()

    errors: list[str] = []
    data = require_dict(load_json(args.json_path), "$", errors)
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    records = require_list(data.get("records"), "records", errors)

    tag_count = 0
    for idx, record in enumerate(records):
        tag_count += validate_record(
            record,
            idx,
            errors,
            enforce_caps=not args.no_caps,
            strict_missing=not args.loose_missing,
        )

    if errors:
        print(f"INVALID: {len(errors)} error(s)", file=sys.stderr)
        for error in errors[: args.max_errors]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > args.max_errors:
            print(f"- ... {len(errors) - args.max_errors} more", file=sys.stderr)
        raise SystemExit(1)

    print(f"VALID: {len(records)} record(s), {tag_count} tag(s)")


if __name__ == "__main__":
    main()
