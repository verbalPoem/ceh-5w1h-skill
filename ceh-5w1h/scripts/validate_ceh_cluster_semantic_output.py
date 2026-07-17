#!/usr/bin/env python3
"""Risk-lint CEH cluster-first v3 output.

This script detects known structural and boundary risks. It does not verify
cluster meaning, causality, WHY, HOW, or event-relation semantics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from validate_ceh_semantic_output import validate as validate_flat_records


ROLES = ("who", "what", "when", "where", "why", "how")


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).casefold().strip())


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def flatten_for_node_lint(data: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for record in data.get("records", []):
        if not isinstance(record, dict):
            continue
        text = record.get("Text", "")
        node_by_id = {
            node.get("Node_Id"): node
            for node in record.get("Nodes", [])
            if isinstance(node, dict) and isinstance(node.get("Node_Id"), str)
        }
        for cluster in record.get("Event_Clusters", []):
            if not isinstance(cluster, dict):
                continue
            cluster_id = cluster.get("Cluster_Id", "EC?")
            for event in cluster.get("Events", []):
                if not isinstance(event, dict):
                    continue
                event_id = event.get("Event_Id", "E?")
                hyperedge = event.get("Event_Hyperedge", {})
                groups = hyperedge.get("Nodes", {}) if isinstance(hyperedge, dict) else {}
                tags: list[dict[str, Any]] = []
                role_indexes: dict[str, list[int]] = {role: [] for role in ROLES}
                if isinstance(groups, dict):
                    for role in ROLES:
                        refs = groups.get(role, [])
                        if not isinstance(refs, list):
                            continue
                        for node_id in refs:
                            node = node_by_id.get(node_id)
                            if not isinstance(node, dict):
                                continue
                            tag = {
                                "Tag_Text": node.get("Tag_Text"),
                                "Tag_Start": node.get("Tag_Start"),
                                "Tag_End": node.get("Tag_End"),
                                "5W1H_Label": role.upper(),
                                "Evidence_Status": node.get("Evidence_Status"),
                            }
                            if "Reliability_Label" in node:
                                tag["Reliability_Label"] = node["Reliability_Label"]
                            role_indexes[role].append(len(tags))
                            tags.append(tag)

                records.append(
                    {
                        "Id": f"{record.get('Id', 'record')}/{cluster_id}/{event_id}",
                        "Text": text,
                        "Root_Event": {
                            "Event_Id": event_id,
                            "Event_Text": event.get("Event_Text", ""),
                            "Trigger": event.get("Trigger", {}),
                        },
                        "Tags": tags,
                        "Missing": [role.upper() for role in event.get("Missing", [])],
                        "Event_Hyperedge": {
                            "event": event_id,
                            **role_indexes,
                        },
                    }
                )
    return {"schema_version": "ceh-record-v2", "records": records}


def cluster_risks(data: dict[str, Any], max_issues: int) -> tuple[list[dict[str, Any]], Counter[str]]:
    issues: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()

    def add(severity: str, code: str, record_id: str, message: str) -> None:
        counts[f"{severity}:{code}"] += 1
        if len(issues) < max_issues:
            issues.append(
                {
                    "severity": severity,
                    "code": code,
                    "record_id": record_id,
                    "message": message,
                }
            )

    records = data.get("records", [])
    if not isinstance(records, list):
        return issues, counts

    for record_index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        record_id = str(record.get("Id", f"record-{record_index}"))
        clusters = record.get("Event_Clusters", [])
        if not isinstance(clusters, list):
            continue
        if len(clusters) > 3:
            add(
                "warning",
                "CLUSTER_DENSE",
                record_id,
                f"record has {len(clusters)} clusters; review whether sentence-level splitting occurred",
            )

        review = record.get("Review", {})
        if isinstance(review, dict) and review.get("Mode") == "self_critic_fallback":
            add(
                "warning",
                "NO_INDEPENDENT_REVIEW",
                record_id,
                "record used self_critic_fallback and still requires human or independent-agent review",
            )

        for cluster in clusters:
            if not isinstance(cluster, dict):
                continue
            cluster_id = str(cluster.get("Cluster_Id", "EC?"))
            scoped_id = f"{record_id}/{cluster_id}"
            events = cluster.get("Events", [])
            relations = cluster.get("Relations", [])
            if not isinstance(events, list):
                continue
            if len(events) > 3:
                add(
                    "warning",
                    "EVENT_DENSE",
                    scoped_id,
                    f"cluster has {len(events)} events; each event needs a distinct predicate and relation",
                )
            if len(events) > 1 and (not isinstance(relations, list) or not relations):
                add(
                    "warning",
                    "RELATION_EMPTY",
                    scoped_id,
                    "multi-event cluster has no event relation",
                )

            summaries: dict[str, str] = {}
            signatures: dict[tuple[tuple[str, tuple[str, ...]], ...], str] = {}
            connected: set[str] = set()
            if isinstance(relations, list):
                for relation in relations:
                    if not isinstance(relation, dict):
                        continue
                    source = relation.get("Source_Event")
                    target = relation.get("Target_Event")
                    if isinstance(source, str):
                        connected.add(source)
                    if isinstance(target, str):
                        connected.add(target)

            for event in events:
                if not isinstance(event, dict):
                    continue
                event_id = str(event.get("Event_Id", "E?"))
                summary = normalize(event.get("Event_Text", ""))
                if summary in summaries and summary:
                    add(
                        "error",
                        "EVENT_DUPLICATE_SUMMARY",
                        scoped_id,
                        f"events {summaries[summary]} and {event_id} have duplicate summaries",
                    )
                summaries[summary] = event_id

                hyperedge = event.get("Event_Hyperedge", {})
                groups = hyperedge.get("Nodes", {}) if isinstance(hyperedge, dict) else {}
                if isinstance(groups, dict):
                    signature = tuple(
                        (role, tuple(sorted(str(item) for item in groups.get(role, []))))
                        for role in ROLES
                    )
                    if signature in signatures:
                        add(
                            "warning",
                            "EVENT_DUPLICATE_HYPEREDGE",
                            scoped_id,
                            f"events {signatures[signature]} and {event_id} use identical node sets",
                        )
                    signatures[signature] = event_id

                if event.get("Event_Level") == "supporting" and event_id not in connected:
                    add(
                        "warning",
                        "SUPPORTING_EVENT_UNCONNECTED",
                        scoped_id,
                        f"supporting event {event_id} has no event relation",
                    )

    return issues, counts


def merge_reports(
    base: dict[str, Any],
    extra_issues: list[dict[str, Any]],
    extra_counts: Counter[str],
    max_issues: int,
) -> dict[str, Any]:
    base_counts = Counter(base.get("summary", {}).get("issue_counts", {}))
    base_counts.update(extra_counts)
    errors = sum(value for key, value in base_counts.items() if key.startswith("error:"))
    warnings = sum(value for key, value in base_counts.items() if key.startswith("warning:"))
    status = "invalid" if errors else ("review" if warnings else "lint_clear")
    issues = list(base.get("issues", []))
    issues.extend(extra_issues)
    issues = issues[:max_issues]
    summary = dict(base.get("summary", {}))
    summary.update(
        {
            "errors": errors,
            "warnings": warnings,
            "issue_counts": dict(sorted(base_counts.items())),
            "issues_truncated": sum(base_counts.values()) > len(issues),
        }
    )
    return {
        "validator": "ceh-cluster-risk-lint-v3",
        "source": base.get("source"),
        "status": status,
        "semantic_roles_verified": False,
        "cluster_semantics_verified": False,
        "independent_agent_review_required": True,
        "summary": summary,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Risk-lint CEH cluster-first v3 JSON")
    parser.add_argument("input", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--max-issues", type=int, default=500)
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args()

    try:
        data = load_json(args.input)
        flattened = flatten_for_node_lint(data)
        base = validate_flat_records(flattened, str(args.input), max(1, args.max_issues))
        extra_issues, extra_counts = cluster_risks(data, max(1, args.max_issues))
        report = merge_reports(base, extra_issues, extra_counts, max(1, args.max_issues))
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
        f"{report['status'].upper()}: {summary.get('records', 0)} event view(s), "
        f"{summary.get('tags', 0)} node reference(s), "
        f"{summary['errors']} error(s), {summary['warnings']} warning(s)"
    )
    if report["status"] == "invalid":
        return 1
    if report["status"] == "review" and args.fail_on_warning:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
