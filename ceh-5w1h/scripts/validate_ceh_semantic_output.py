#!/usr/bin/env python3
"""Risk-lint CEH record-first output for common extraction failures.

This validator complements validate_ceh_record_output.py. It intentionally
flags suspicious output for review. It does not understand proposition meaning
and cannot certify WHY/HOW semantics; that requires a model or human critic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


LABELS = ("WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW")
ROLE_CAPS = {"WHO": 5, "WHAT": 2, "WHEN": 1, "WHERE": 1, "WHY": 2, "HOW": 2}
EVIDENCE_STATUSES = {"explicit", "implicit", "converted"}
RELIABILITY_LABELS = {"reliable", "partially_reliable", "unreliable"}
LEGACY_EVIDENCE_LABELS = {"direct", "inferred", "converted"}

ATTRIBUTION = ("表示", "称", "报道", "报道称", "透露", "宣布", "据悉", "消息称")
WHO_PREDICATES = (
    "宣布",
    "表示",
    "报道称",
    "报道",
    "透露",
    "将组建",
    "将构成",
    "将部署",
    "计划部署",
    "计划装备",
    "计划采购",
    "计划完成",
    "计划建设",
    "计划进行",
    "进行",
    "已完成",
    "完成了",
    "签署了",
    "授予了",
    "裁定",
    "批准",
    "要求",
    "利用",
    "采用",
    "通过",
    "导致",
    "造成",
    "继续",
    "开始",
    "实现",
    "访问了",
    "介绍了",
    "进行测试",
    "完成测试",
    "进行评估",
    "完成评估",
    "展出",
    "展示",
    "引进",
    "出售",
    "转让",
    "声称",
    "发射了",
    "采购了",
    "交付了",
    "建造了",
    "升级为",
    "定于",
    "难以",
)
ACTION_MARKERS = (
    "裁定",
    "批准",
    "要求",
    "驳回",
    "组建",
    "构成",
    "部署",
    "计划",
    "装备",
    "完成",
    "签署",
    "授予",
    "交付",
    "采购",
    "建设",
    "建造",
    "升级",
    "改造",
    "展出",
    "展示",
    "引进",
    "出售",
    "转让",
    "声称",
    "测试",
    "评估",
    "发射",
    "拦截",
    "拥有",
    "储备",
    "削减",
    "暂停",
    "危及",
    "削弱",
    "影响",
    "成立",
    "达成",
    "进入",
    "死亡",
    "死于",
    "推出",
    "禁止",
    "撤销",
    "发放",
)
SOURCE_PREFIXES = ("据", "根据", "报道称", "报道", "记者", "消息", "来自")
COREFERENCE_ONLY_WHO = {
    "其",
    "该国",
    "后者",
    "该系统",
    "该公司",
    "该机构",
    "该部门",
    "他",
    "她",
    "他们",
    "她们",
    "它",
    "它们",
}
TIME_RE = re.compile(
    r"(?:\d{4}年|\d{1,2}月|\d{1,2}[日号]|周[一二三四五六日天]|星期[一二三四五六日天]|"
    r"过去(?:的)?\d+年(?:中)?|\d+周年|近日|日前|今天|昨日|本月|本周|下月|明年|今年|"
    r"年内|年度|截至|迄今|目前|未来|此前)"
)
PUNCTUATION_RE = re.compile(r"[，。！？；!?;]")


def normalize(value: str) -> str:
    value = re.sub(r"\s+", " ", value.casefold().strip())
    return re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)


def starts_with_any(value: str, markers: tuple[str, ...]) -> bool:
    stripped = value.lstrip(" ，,：:；;、")
    return any(stripped.startswith(marker) for marker in markers)


def contains_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def validate(data: dict[str, Any], source: str, max_issues: int) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    total_tags = 0
    total_who = 0

    def add(severity: str, code: str, record_id: str, message: str, tag_index: int | None = None) -> None:
        counts[f"{severity}:{code}"] += 1
        if len(issues) < max_issues:
            item: dict[str, Any] = {
                "severity": severity,
                "code": code,
                "record_id": record_id,
                "message": message,
            }
            if tag_index is not None:
                item["tag_index"] = tag_index
            issues.append(item)

    if data.get("schema_version") != "ceh-record-v2":
        add("error", "SCHEMA_VERSION", "<document>", "schema_version must be ceh-record-v2")

    records = data.get("records")
    if not isinstance(records, list):
        add("error", "RECORDS_TYPE", "<document>", "records must be an array")
        records = []

    for record_pos, record in enumerate(records):
        if not isinstance(record, dict):
            add("error", "RECORD_TYPE", f"record-{record_pos}", "record must be an object")
            continue

        record_id = str(record.get("Id", f"record-{record_pos}"))
        text = record.get("Text")
        tags = record.get("Tags")
        root = record.get("Root_Event")
        missing = record.get("Missing")

        if not isinstance(text, str):
            add("error", "TEXT_TYPE", record_id, "Text must be a string")
            continue
        if not isinstance(tags, list):
            add("error", "TAGS_TYPE", record_id, "Tags must be an array")
            continue
        if not isinstance(root, dict):
            add("error", "ROOT_TYPE", record_id, "Root_Event must be an object")
            root = {}

        role_indexes: dict[str, list[int]] = {label: [] for label in LABELS}
        seen: set[tuple[str, str]] = set()
        total_tags += len(tags)

        for tag_index, tag in enumerate(tags):
            if not isinstance(tag, dict):
                add("error", "TAG_TYPE", record_id, "tag must be an object", tag_index)
                continue
            label = tag.get("5W1H_Label")
            span = tag.get("Tag_Text")
            start = tag.get("Tag_Start")
            end = tag.get("Tag_End")
            evidence_status = tag.get("Evidence_Status")
            reliability_label = tag.get("Reliability_Label")

            if label not in LABELS:
                add("error", "LABEL", record_id, f"invalid label: {label!r}", tag_index)
                continue
            if not isinstance(span, str) or not isinstance(start, int) or not isinstance(end, int):
                add("error", "TAG_FIELDS", record_id, "Tag_Text/Tag_Start/Tag_End have invalid types", tag_index)
                continue
            role_indexes[label].append(tag_index)
            role_counts[label] += 1
            if label == "WHO":
                total_who += 1

            uses_legacy_evidence = evidence_status is None and reliability_label in LEGACY_EVIDENCE_LABELS
            if evidence_status is None and not uses_legacy_evidence:
                add("error", "EVIDENCE_STATUS", record_id, "Evidence_Status is required", tag_index)
            elif evidence_status is not None and evidence_status not in EVIDENCE_STATUSES:
                add("error", "EVIDENCE_STATUS", record_id, f"invalid Evidence_Status: {evidence_status!r}", tag_index)
            if uses_legacy_evidence:
                add(
                    "warning",
                    "LEGACY_EVIDENCE_FIELD",
                    record_id,
                    "move direct/inferred/converted from Reliability_Label to Evidence_Status",
                    tag_index,
                )
            elif reliability_label is not None and reliability_label not in RELIABILITY_LABELS:
                add("error", "RELIABILITY", record_id, f"invalid Reliability_Label: {reliability_label!r}", tag_index)
            if start < 0 or end < start or end > len(text) or text[start:end] != span:
                add("error", "OFFSET", record_id, "Tag_Text does not match Text[Tag_Start:Tag_End]", tag_index)

            key = (label, normalize(span))
            if key in seen:
                add("error", "DUPLICATE", record_id, "duplicate normalized label/text pair", tag_index)
            seen.add(key)

            if label == "WHO":
                if PUNCTUATION_RE.search(span):
                    add("error", "WHO_CLAUSE_PUNCT", record_id, f"WHO contains clause punctuation: {span}", tag_index)
                if contains_any(span, WHO_PREDICATES):
                    add("error", "WHO_CLAUSE_PREDICATE", record_id, f"WHO contains an event predicate: {span}", tag_index)
                if len(span) > 30:
                    add("error", "WHO_TOO_LONG", record_id, f"WHO is longer than 30 characters: {span}", tag_index)
                elif len(span) > 20:
                    add("warning", "WHO_LONG", record_id, f"review long WHO boundary: {span}", tag_index)
                if span.count("的") >= 2:
                    add("warning", "WHO_GENITIVE_CHAIN", record_id, f"WHO contains a long genitive chain: {span}", tag_index)
                if starts_with_any(span, SOURCE_PREFIXES):
                    add("warning", "WHO_SOURCE_PREFIX", record_id, f"WHO starts with source context: {span}", tag_index)
                if normalize(span) in COREFERENCE_ONLY_WHO:
                    add(
                        "warning",
                        "WHO_COREFERENCE_ONLY",
                        record_id,
                        f"replace a pronoun/coreference-only WHO with its clearest exact antecedent: {span}",
                        tag_index,
                    )

            elif label == "WHAT":
                if len(span) > 100:
                    add("error", "WHAT_TOO_LONG", record_id, f"WHAT exceeds 100 characters: {span}", tag_index)
                elif len(span) > 64:
                    add("warning", "WHAT_LONG", record_id, f"review long WHAT boundary: {span}", tag_index)
                if not contains_any(span, ACTION_MARKERS) and len(span) > 8:
                    add("warning", "WHAT_NO_ACTION", record_id, f"WHAT has no clear central action marker: {span}", tag_index)
                if starts_with_any(span, SOURCE_PREFIXES) and contains_any(span, ATTRIBUTION):
                    add("warning", "WHAT_ATTRIBUTION_SHELL", record_id, f"remove reporting/source shell from WHAT: {span}", tag_index)

            elif label == "WHEN":
                if not TIME_RE.search(span):
                    add("warning", "WHEN_NOT_TEMPORAL", record_id, f"WHEN has no recognizable time expression: {span}", tag_index)

            elif label == "WHERE":
                if contains_any(span, WHO_PREDICATES) or PUNCTUATION_RE.search(span):
                    add("error", "WHERE_CLAUSE", record_id, f"WHERE contains an action/clause: {span}", tag_index)
                if len(span) > 24:
                    add("warning", "WHERE_LONG", record_id, f"review long WHERE boundary: {span}", tag_index)

            elif label == "WHY":
                if len(span) > 80:
                    add("warning", "WHY_LONG", record_id, f"review long WHY proposition boundary: {span}", tag_index)

            elif label == "HOW":
                if len(span) > 80:
                    add("warning", "HOW_LONG", record_id, f"review long HOW proposition boundary: {span}", tag_index)

        for label, indexes in role_indexes.items():
            if len(indexes) > ROLE_CAPS[label]:
                add("error", "ROLE_CAP", record_id, f"{label} count {len(indexes)} exceeds {ROLE_CAPS[label]}")
        if len(role_indexes["WHO"]) > 3:
            add("warning", "WHO_DENSE", record_id, f"WHO count {len(role_indexes['WHO'])} needs multi-party justification")
        if len(tags) > 12:
            add("error", "TOTAL_CAP", record_id, f"tag count {len(tags)} exceeds 12")
        elif len(tags) > 6:
            add("warning", "DENSE_RECORD", record_id, f"tag count {len(tags)} exceeds the typical range")

        who_tags = [tags[i] for i in role_indexes["WHO"] if isinstance(tags[i], dict)]
        for left_pos, left in enumerate(who_tags):
            for right in who_tags[left_pos + 1 :]:
                if not all(isinstance(item.get("Tag_Text"), str) for item in (left, right)):
                    continue
                l_text = normalize(left["Tag_Text"])
                r_text = normalize(right["Tag_Text"])
                l_start, l_end = left.get("Tag_Start"), left.get("Tag_End")
                r_start, r_end = right.get("Tag_Start"), right.get("Tag_End")
                overlaps = all(isinstance(x, int) for x in (l_start, l_end, r_start, r_end)) and max(l_start, r_start) < min(l_end, r_end)
                if overlaps and (l_text in r_text or r_text in l_text):
                    add("error", "WHO_NESTED_ALIAS", record_id, f"collapse nested WHO aliases: {left['Tag_Text']} / {right['Tag_Text']}")

        normalized_by_text: dict[str, list[str]] = {}
        for tag in tags:
            if isinstance(tag, dict) and isinstance(tag.get("Tag_Text"), str) and tag.get("5W1H_Label") in LABELS:
                normalized_by_text.setdefault(normalize(tag["Tag_Text"]), []).append(tag["5W1H_Label"])
        for value, value_labels in normalized_by_text.items():
            unique = set(value_labels)
            if len(unique) > 1 and unique != {"WHO", "WHERE"}:
                add("error", "CROSS_ROLE_DUPLICATE", record_id, f"same span assigned to multiple roles {sorted(unique)}: {value}")

        if isinstance(missing, list):
            expected_missing = {label for label, indexes in role_indexes.items() if not indexes}
            actual_missing = {str(label) for label in missing}
            if expected_missing != actual_missing:
                add("error", "MISSING_MISMATCH", record_id, f"Missing should be {sorted(expected_missing)}, got {sorted(actual_missing)}")

        trigger = root.get("Trigger") if isinstance(root, dict) else None
        if isinstance(trigger, dict):
            trig_text = trigger.get("Tag_Text")
            trig_start = trigger.get("Tag_Start")
            trig_end = trigger.get("Tag_End")
            if isinstance(trig_text, str) and trig_text:
                if not isinstance(trig_start, int) or not isinstance(trig_end, int) or text[trig_start:trig_end] != trig_text:
                    add("error", "TRIGGER_OFFSET", record_id, "root trigger offset mismatch")
                if trig_text in ATTRIBUTION:
                    event_text = str(root.get("Event_Text", ""))
                    if contains_any(event_text, ACTION_MARKERS):
                        add("warning", "ATTRIBUTION_TRIGGER", record_id, f"root trigger {trig_text!r} may hide a stronger embedded action")

    record_count = len(records)
    avg_who = round(total_who / record_count, 3) if record_count else 0.0
    avg_tags = round(total_tags / record_count, 3) if record_count else 0.0
    if record_count >= 20 and avg_who > 3.0:
        add("warning", "FILE_WHO_DENSITY", "<document>", f"average WHO count {avg_who} exceeds 3.0")
    if record_count >= 20 and avg_tags > 6.0:
        add("warning", "FILE_TAG_DENSITY", "<document>", f"average tag count {avg_tags} exceeds 6.0")

    errors = sum(value for key, value in counts.items() if key.startswith("error:"))
    warnings = sum(value for key, value in counts.items() if key.startswith("warning:"))
    status = "invalid" if errors else ("review" if warnings else "lint_clear")
    return {
        "validator": "ceh-risk-lint-v2",
        "source": source,
        "status": status,
        "semantic_roles_verified": False,
        "model_semantic_review_required": True,
        "summary": {
            "records": record_count,
            "tags": total_tags,
            "errors": errors,
            "warnings": warnings,
            "avg_tags_per_record": avg_tags,
            "avg_who_per_record": avg_who,
            "role_counts": dict(role_counts),
            "issue_counts": dict(sorted(counts.items())),
            "issues_truncated": sum(counts.values()) > len(issues),
        },
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic risk lint for ceh-record-v2 JSON")
    parser.add_argument("input", type=Path, help="ceh-record-v2 JSON file")
    parser.add_argument("--report", type=Path, help="optional JSON report path")
    parser.add_argument("--max-issues", type=int, default=500, help="maximum detailed issues to retain")
    parser.add_argument("--fail-on-warning", action="store_true", help="return non-zero for review status")
    args = parser.parse_args()

    try:
        data = load_json(args.input)
        report = validate(data, str(args.input), max(1, args.max_issues))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    summary = report["summary"]
    print(
        f"{report['status'].upper()}: {summary['records']} record(s), {summary['tags']} tag(s), "
        f"{summary['errors']} error(s), {summary['warnings']} warning(s)"
    )
    if report["status"] == "invalid":
        return 1
    if report["status"] == "review" and args.fail_on_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
