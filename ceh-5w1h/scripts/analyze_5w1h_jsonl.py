#!/usr/bin/env python3
"""Audit exact-span 5W1H JSONL datasets without language-specific rules."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


LABELS = ("WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW")


def percentile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def read_jsonl(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        with path.open("r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError(f"{path}:{line_number}: record must be an object")
                records.append(item)
    return records


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    tag_counts: Counter[str] = Counter()
    presence_counts: Counter[str] = Counter()
    reliability_counts: dict[str, Counter[str]] = defaultdict(Counter)
    lengths: dict[str, list[int]] = defaultdict(list)
    per_record: dict[str, list[int]] = defaultdict(list)
    offset_mismatches = 0

    for record in records:
        text = record.get("Text", "")
        tags = record.get("Tags", [])
        if not isinstance(text, str) or not isinstance(tags, list):
            continue
        local: Counter[str] = Counter()
        for tag in tags:
            if not isinstance(tag, dict):
                continue
            label = tag.get("5W1H_Label")
            if label not in LABELS:
                continue
            span = tag.get("Tag_Text")
            start = tag.get("Tag_Start")
            end = tag.get("Tag_End")
            local[label] += 1
            tag_counts[label] += 1
            if isinstance(span, str):
                lengths[label].append(len(span))
            reliability_counts[label][str(tag.get("Reliability_Label", "<missing>"))] += 1
            if not (
                isinstance(span, str)
                and isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start <= end <= len(text)
                and text[start:end] == span
            ):
                offset_mismatches += 1
        for label in LABELS:
            per_record[label].append(local[label])
            if local[label]:
                presence_counts[label] += 1

    role_stats: dict[str, Any] = {}
    total_records = len(records)
    for label in LABELS:
        values = per_record[label]
        role_stats[label] = {
            "records_present": presence_counts[label],
            "record_presence_rate": round(presence_counts[label] / total_records, 4) if total_records else 0.0,
            "tags": tag_counts[label],
            "mean_tags_per_record": round(sum(values) / total_records, 4) if total_records else 0.0,
            "max_tags_per_record": max(values, default=0),
            "span_length_p50": percentile(lengths[label], 0.5),
            "span_length_p90": percentile(lengths[label], 0.9),
            "span_length_max": max(lengths[label], default=0),
            "reliability_counts": dict(sorted(reliability_counts[label].items())),
        }

    return {
        "records": total_records,
        "tags": sum(tag_counts.values()),
        "offset_mismatches": offset_mismatches,
        "roles": role_stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit language-independent 5W1H JSONL annotations")
    parser.add_argument("inputs", nargs="+", type=Path, help="one or more JSONL files")
    parser.add_argument("--report", type=Path, help="optional JSON report path")
    args = parser.parse_args()

    try:
        report = analyze(read_jsonl(args.inputs))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
