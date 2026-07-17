#!/usr/bin/env python3
"""Validate the structural contract of CEH cluster-first v3 output."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ceh-cluster-v3"
ROLES = ("who", "what", "when", "where", "why", "how")
ROLE_CAPS = {"who": 5, "what": 2, "when": 1, "where": 1, "why": 2, "how": 2}
EVENT_LEVELS = {"central", "supporting"}
EVIDENCE_STATUSES = {"explicit", "implicit", "converted"}
RELIABILITY_LABELS = {"reliable", "partially_reliable", "unreliable"}
RELATIONS = {
    "discloses",
    "supports",
    "motivates",
    "causes",
    "part_of",
    "component_of",
    "background_of",
    "enables",
    "contrasts_with",
}
REVIEW_MODES = {"independent_agent", "self_critic_fallback"}
REVIEW_STATUSES = {"passed", "revised", "needs_human_review"}
ID_PATTERNS = {
    "Sentence_Id": re.compile(r"^S[1-9][0-9]*$"),
    "Node_Id": re.compile(r"^N[1-9][0-9]*$"),
    "Cluster_Id": re.compile(r"^EC[1-9][0-9]*$"),
    "Event_Id": re.compile(r"^E[1-9][0-9]*$"),
    "Hyperedge_Id": re.compile(r"^HE[1-9][0-9]*$"),
    "Relation_Id": re.compile(r"^(?:R|CR)[1-9][0-9]*$"),
}


def normalize(value: str) -> str:
    value = re.sub(r"\s+", " ", value.casefold().strip())
    return re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)


def load_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def require_dict(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def require_list(value: Any, path: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return []
    return value


def require_string(value: Any, path: str, errors: list[str], *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        errors.append(f"{path} must be a string")
        return ""
    if not allow_empty and not value.strip():
        errors.append(f"{path} must not be empty")
    return value


def validate_id(value: Any, field: str, path: str, errors: list[str]) -> str:
    text = require_string(value, path, errors)
    pattern = ID_PATTERNS[field]
    if text and not pattern.fullmatch(text):
        errors.append(f"{path} has invalid {field} format: {text!r}")
    return text


def validate_span(
    text: str,
    obj: dict[str, Any],
    path: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> tuple[int, int]:
    span = obj.get("Tag_Text")
    start = obj.get("Tag_Start")
    end = obj.get("Tag_End")
    if not isinstance(span, str):
        errors.append(f"{path}.Tag_Text must be a string")
        return 0, 0
    if not isinstance(start, int) or isinstance(start, bool):
        errors.append(f"{path}.Tag_Start must be an integer")
        return 0, 0
    if not isinstance(end, int) or isinstance(end, bool):
        errors.append(f"{path}.Tag_End must be an integer")
        return 0, 0
    if not allow_empty and not span:
        errors.append(f"{path}.Tag_Text must not be empty")
    if start < 0 or end < start or end > len(text):
        errors.append(f"{path} has out-of-range offsets [{start}, {end})")
        return start, end
    if text[start:end] != span:
        errors.append(
            f"{path} offset mismatch: Text[{start}:{end}]={text[start:end]!r}, Tag_Text={span!r}"
        )
    return start, end


def validate_string_list(value: Any, path: str, errors: list[str]) -> list[str]:
    items = require_list(value, path, errors)
    result: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, str) or not item:
            errors.append(f"{path}[{index}] must be a non-empty string")
            continue
        result.append(item)
    if len(result) != len(set(result)):
        errors.append(f"{path} contains duplicate values")
    return result


def span_is_covered(start: int, end: int, evidence_spans: list[tuple[int, int]]) -> bool:
    return any(sent_start <= start and end <= sent_end for sent_start, sent_end in evidence_spans)


def node_is_evidenced(
    text: str,
    node: dict[str, Any],
    start: int,
    end: int,
    evidence_spans: list[tuple[int, int]],
) -> bool:
    if span_is_covered(start, end, evidence_spans):
        return True
    tag_text = node.get("Tag_Text")
    if not isinstance(tag_text, str) or not tag_text:
        return False
    return any(tag_text in text[sent_start:sent_end] for sent_start, sent_end in evidence_spans)


def validate_record(record: Any, index: int, errors: list[str]) -> tuple[int, int, int]:
    path = f"records[{index}]"
    obj = require_dict(record, path, errors)
    require_string(obj.get("Id"), f"{path}.Id", errors)
    text = require_string(obj.get("Text"), f"{path}.Text", errors, allow_empty=True)

    sentence_by_id: dict[str, dict[str, Any]] = {}
    sentence_spans: dict[str, tuple[int, int]] = {}
    ordered_sentence_spans: list[tuple[int, int, str]] = []
    for sent_index, raw_sentence in enumerate(require_list(obj.get("Sentences"), f"{path}.Sentences", errors)):
        sent_path = f"{path}.Sentences[{sent_index}]"
        sentence = require_dict(raw_sentence, sent_path, errors)
        sentence_id = validate_id(sentence.get("Sentence_Id"), "Sentence_Id", f"{sent_path}.Sentence_Id", errors)
        if sentence_id in sentence_by_id:
            errors.append(f"{sent_path}.Sentence_Id duplicates {sentence_id!r}")
        start, end = validate_span(text, sentence, sent_path, errors)
        if sentence_id:
            sentence_by_id[sentence_id] = sentence
            sentence_spans[sentence_id] = (start, end)
            ordered_sentence_spans.append((start, end, sentence_id))

    for left, right in zip(
        sorted(ordered_sentence_spans),
        sorted(ordered_sentence_spans)[1:],
    ):
        if right[0] < left[1]:
            errors.append(f"{path}.Sentences overlap: {left[2]} and {right[2]}")

    node_by_id: dict[str, dict[str, Any]] = {}
    node_spans: dict[str, tuple[int, int]] = {}
    seen_nodes: set[tuple[str, str]] = set()
    for node_index, raw_node in enumerate(require_list(obj.get("Nodes"), f"{path}.Nodes", errors)):
        node_path = f"{path}.Nodes[{node_index}]"
        node = require_dict(raw_node, node_path, errors)
        node_id = validate_id(node.get("Node_Id"), "Node_Id", f"{node_path}.Node_Id", errors)
        if node_id in node_by_id:
            errors.append(f"{node_path}.Node_Id duplicates {node_id!r}")
        node_type = node.get("Node_Type")
        if node_type not in ROLES:
            errors.append(f"{node_path}.Node_Type must be one of {ROLES}, got {node_type!r}")
        start, end = validate_span(text, node, node_path, errors)
        evidence_status = node.get("Evidence_Status")
        if evidence_status not in EVIDENCE_STATUSES:
            errors.append(
                f"{node_path}.Evidence_Status must be one of {sorted(EVIDENCE_STATUSES)}, "
                f"got {evidence_status!r}"
            )
        reliability = node.get("Reliability_Label")
        if reliability is not None and reliability not in RELIABILITY_LABELS:
            errors.append(
                f"{node_path}.Reliability_Label must be one of {sorted(RELIABILITY_LABELS)}, "
                f"got {reliability!r}"
            )
        span_text = node.get("Tag_Text")
        if isinstance(node_type, str) and isinstance(span_text, str):
            key = (node_type, normalize(span_text))
            if key in seen_nodes:
                errors.append(f"{node_path} duplicates normalized node {key!r}")
            seen_nodes.add(key)
        if node_id:
            node_by_id[node_id] = node
            node_spans[node_id] = (start, end)

    cluster_ids: set[str] = set()
    event_ids: set[str] = set()
    hyperedge_ids: set[str] = set()
    relation_ids: set[str] = set()
    used_node_ids: set[str] = set()
    clusters = require_list(obj.get("Event_Clusters"), f"{path}.Event_Clusters", errors)
    if not clusters:
        errors.append(f"{path}.Event_Clusters must contain at least one cluster")

    pending_relations: list[tuple[dict[str, Any], str, set[str]]] = []
    for cluster_index, raw_cluster in enumerate(clusters):
        cluster_path = f"{path}.Event_Clusters[{cluster_index}]"
        cluster = require_dict(raw_cluster, cluster_path, errors)
        cluster_id = validate_id(
            cluster.get("Cluster_Id"), "Cluster_Id", f"{cluster_path}.Cluster_Id", errors
        )
        if cluster_id in cluster_ids:
            errors.append(f"{cluster_path}.Cluster_Id duplicates {cluster_id!r}")
        cluster_ids.add(cluster_id)
        require_string(cluster.get("Topic"), f"{cluster_path}.Topic", errors)
        central_event = validate_id(
            cluster.get("Central_Event"), "Event_Id", f"{cluster_path}.Central_Event", errors
        )
        events = require_list(cluster.get("Events"), f"{cluster_path}.Events", errors)
        if not events:
            errors.append(f"{cluster_path}.Events must contain at least one event")
        if len(events) > 5:
            errors.append(f"{cluster_path}.Events exceeds hard maximum 5")

        local_event_ids: set[str] = set()
        central_count = 0
        for event_index, raw_event in enumerate(events):
            event_path = f"{cluster_path}.Events[{event_index}]"
            event = require_dict(raw_event, event_path, errors)
            event_id = validate_id(event.get("Event_Id"), "Event_Id", f"{event_path}.Event_Id", errors)
            if event_id in event_ids:
                errors.append(f"{event_path}.Event_Id duplicates record-local {event_id!r}")
            event_ids.add(event_id)
            local_event_ids.add(event_id)
            level = event.get("Event_Level")
            if level not in EVENT_LEVELS:
                errors.append(f"{event_path}.Event_Level must be one of {sorted(EVENT_LEVELS)}")
            if level == "central":
                central_count += 1
            if event_id == central_event and level != "central":
                errors.append(f"{event_path} is Central_Event but Event_Level is not 'central'")
            if event_id != central_event and level == "central":
                errors.append(f"{event_path} is marked central but is not Central_Event")
            require_string(event.get("Event_Text"), f"{event_path}.Event_Text", errors)
            trigger = require_dict(event.get("Trigger"), f"{event_path}.Trigger", errors)
            trigger_start, trigger_end = validate_span(text, trigger, f"{event_path}.Trigger", errors)

            evidence_ids = validate_string_list(event.get("Evidence"), f"{event_path}.Evidence", errors)
            if not evidence_ids:
                errors.append(f"{event_path}.Evidence must contain at least one Sentence_Id")
            bad_evidence = [sentence_id for sentence_id in evidence_ids if sentence_id not in sentence_by_id]
            if bad_evidence:
                errors.append(f"{event_path}.Evidence references unknown sentences {bad_evidence}")
            evidence_spans = [sentence_spans[sid] for sid in evidence_ids if sid in sentence_spans]
            if evidence_spans and not span_is_covered(trigger_start, trigger_end, evidence_spans):
                errors.append(f"{event_path}.Trigger is outside its Evidence sentences")

            missing = validate_string_list(event.get("Missing"), f"{event_path}.Missing", errors)
            unknown_missing = sorted(set(missing) - set(ROLES))
            if unknown_missing:
                errors.append(f"{event_path}.Missing has invalid roles {unknown_missing}")

            hyperedge = require_dict(event.get("Event_Hyperedge"), f"{event_path}.Event_Hyperedge", errors)
            hyperedge_id = validate_id(
                hyperedge.get("Hyperedge_Id"),
                "Hyperedge_Id",
                f"{event_path}.Event_Hyperedge.Hyperedge_Id",
                errors,
            )
            if hyperedge_id in hyperedge_ids:
                errors.append(f"{event_path}.Event_Hyperedge.Hyperedge_Id duplicates {hyperedge_id!r}")
            hyperedge_ids.add(hyperedge_id)
            if hyperedge.get("Event") != event_id:
                errors.append(f"{event_path}.Event_Hyperedge.Event must equal {event_id!r}")
            groups = require_dict(
                hyperedge.get("Nodes"), f"{event_path}.Event_Hyperedge.Nodes", errors
            )
            if set(groups) != set(ROLES):
                errors.append(
                    f"{event_path}.Event_Hyperedge.Nodes must contain exactly {list(ROLES)}"
                )

            expected_missing: set[str] = set()
            total_nodes = 0
            for role in ROLES:
                refs = validate_string_list(
                    groups.get(role), f"{event_path}.Event_Hyperedge.Nodes.{role}", errors
                )
                total_nodes += len(refs)
                if len(refs) > ROLE_CAPS[role]:
                    errors.append(
                        f"{event_path}.Event_Hyperedge.Nodes.{role} count {len(refs)} "
                        f"exceeds {ROLE_CAPS[role]}"
                    )
                if not refs:
                    expected_missing.add(role)
                for node_id in refs:
                    node = node_by_id.get(node_id)
                    if node is None:
                        errors.append(
                            f"{event_path}.Event_Hyperedge.Nodes.{role} references unknown {node_id!r}"
                        )
                        continue
                    used_node_ids.add(node_id)
                    if node.get("Node_Type") != role:
                        errors.append(
                            f"{event_path}.Event_Hyperedge.Nodes.{role} references {node_id!r} "
                            f"with Node_Type {node.get('Node_Type')!r}"
                        )
                    if evidence_spans:
                        node_start, node_end = node_spans[node_id]
                        if not node_is_evidenced(
                            text,
                            node,
                            node_start,
                            node_end,
                            evidence_spans,
                        ):
                            errors.append(
                                f"{event_path} node {node_id!r} has no canonical or repeated exact "
                                "mention in its Evidence sentences"
                            )
            if total_nodes > 12:
                errors.append(f"{event_path} references {total_nodes} nodes, exceeding hard maximum 12")
            if not groups.get("what"):
                errors.append(f"{event_path} must contain at least one what node")
            if set(missing) != expected_missing:
                errors.append(
                    f"{event_path}.Missing should be {sorted(expected_missing)}, got {sorted(set(missing))}"
                )

        if central_event not in local_event_ids:
            errors.append(f"{cluster_path}.Central_Event {central_event!r} is not in Events")
        if central_count != 1:
            errors.append(f"{cluster_path} must have exactly one central event, found {central_count}")
        pending_relations.append((cluster, cluster_path, local_event_ids))

    for cluster, cluster_path, local_event_ids in pending_relations:
        relations = require_list(cluster.get("Relations"), f"{cluster_path}.Relations", errors)
        for relation_index, raw_relation in enumerate(relations):
            relation_path = f"{cluster_path}.Relations[{relation_index}]"
            relation = require_dict(raw_relation, relation_path, errors)
            relation_id = validate_id(
                relation.get("Relation_Id"), "Relation_Id", f"{relation_path}.Relation_Id", errors
            )
            if relation_id in relation_ids:
                errors.append(f"{relation_path}.Relation_Id duplicates {relation_id!r}")
            relation_ids.add(relation_id)
            source = relation.get("Source_Event")
            target = relation.get("Target_Event")
            if source not in local_event_ids:
                errors.append(f"{relation_path}.Source_Event references unknown local event {source!r}")
            if target not in local_event_ids:
                errors.append(f"{relation_path}.Target_Event references unknown local event {target!r}")
            if source == target:
                errors.append(f"{relation_path} must not be a self relation")
            if relation.get("Relation") not in RELATIONS:
                errors.append(
                    f"{relation_path}.Relation must be one of {sorted(RELATIONS)}, "
                    f"got {relation.get('Relation')!r}"
                )
            evidence_ids = validate_string_list(
                relation.get("Evidence"), f"{relation_path}.Evidence", errors
            )
            if not evidence_ids:
                errors.append(f"{relation_path}.Evidence must contain at least one Sentence_Id")
            bad_evidence = [sentence_id for sentence_id in evidence_ids if sentence_id not in sentence_by_id]
            if bad_evidence:
                errors.append(f"{relation_path}.Evidence references unknown sentences {bad_evidence}")

    cross_relations = require_list(
        obj.get("Cross_Cluster_Relations"), f"{path}.Cross_Cluster_Relations", errors
    )
    for relation_index, raw_relation in enumerate(cross_relations):
        relation_path = f"{path}.Cross_Cluster_Relations[{relation_index}]"
        relation = require_dict(raw_relation, relation_path, errors)
        relation_id = validate_id(
            relation.get("Relation_Id"), "Relation_Id", f"{relation_path}.Relation_Id", errors
        )
        if relation_id in relation_ids:
            errors.append(f"{relation_path}.Relation_Id duplicates {relation_id!r}")
        relation_ids.add(relation_id)
        source = relation.get("Source_Cluster")
        target = relation.get("Target_Cluster")
        if source not in cluster_ids:
            errors.append(f"{relation_path}.Source_Cluster references unknown cluster {source!r}")
        if target not in cluster_ids:
            errors.append(f"{relation_path}.Target_Cluster references unknown cluster {target!r}")
        if source == target:
            errors.append(f"{relation_path} must not be a self relation")
        if relation.get("Relation") not in RELATIONS:
            errors.append(
                f"{relation_path}.Relation must be one of {sorted(RELATIONS)}, "
                f"got {relation.get('Relation')!r}"
            )
        evidence_ids = validate_string_list(
            relation.get("Evidence"), f"{relation_path}.Evidence", errors
        )
        if not evidence_ids:
            errors.append(f"{relation_path}.Evidence must contain at least one Sentence_Id")
        bad_evidence = [sentence_id for sentence_id in evidence_ids if sentence_id not in sentence_by_id]
        if bad_evidence:
            errors.append(f"{relation_path}.Evidence references unknown sentences {bad_evidence}")

    dangling_nodes = sorted(set(node_by_id) - used_node_ids)
    if dangling_nodes:
        errors.append(f"{path}.Nodes contains unreferenced nodes {dangling_nodes}")

    review = require_dict(obj.get("Review"), f"{path}.Review", errors)
    mode = review.get("Mode")
    status = review.get("Status")
    if mode not in REVIEW_MODES:
        errors.append(f"{path}.Review.Mode must be one of {sorted(REVIEW_MODES)}")
    if status not in REVIEW_STATUSES:
        errors.append(f"{path}.Review.Status must be one of {sorted(REVIEW_STATUSES)}")
    require_string(review.get("Reviewer"), f"{path}.Review.Reviewer", errors)
    issues = require_list(review.get("Issues_Found"), f"{path}.Review.Issues_Found", errors)
    for issue_index, issue in enumerate(issues):
        issue_path = f"{path}.Review.Issues_Found[{issue_index}]"
        issue_obj = require_dict(issue, issue_path, errors)
        require_string(issue_obj.get("Code"), f"{issue_path}.Code", errors)
        require_string(issue_obj.get("Message"), f"{issue_path}.Message", errors)
    changes = require_list(review.get("Changes_Made"), f"{path}.Review.Changes_Made", errors)
    for change_index, change in enumerate(changes):
        require_string(change, f"{path}.Review.Changes_Made[{change_index}]", errors)
    if mode == "self_critic_fallback" and status != "needs_human_review":
        errors.append(
            f"{path}.Review.Status must be 'needs_human_review' for self_critic_fallback"
        )
    if status == "revised" and not changes:
        errors.append(f"{path}.Review.Changes_Made must not be empty when Status is 'revised'")

    return len(clusters), len(event_ids), len(node_by_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CEH cluster-first v3 JSON")
    parser.add_argument("json_path", help="JSON file path, or '-' for stdin")
    parser.add_argument("--max-errors", type=int, default=60)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        data = require_dict(load_json(args.json_path), "$", errors)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    records = require_list(data.get("records"), "records", errors)
    cluster_count = 0
    event_count = 0
    node_count = 0
    for index, record in enumerate(records):
        clusters, events, nodes = validate_record(record, index, errors)
        cluster_count += clusters
        event_count += events
        node_count += nodes

    if errors:
        print(f"INVALID: {len(errors)} error(s)", file=sys.stderr)
        for error in errors[: max(1, args.max_errors)]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > args.max_errors:
            print(f"- ... {len(errors) - args.max_errors} more", file=sys.stderr)
        return 1

    print(
        f"VALID: {len(records)} record(s), {cluster_count} cluster(s), "
        f"{event_count} event(s), {node_count} node(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
