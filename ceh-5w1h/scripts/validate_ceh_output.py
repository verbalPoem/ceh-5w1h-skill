#!/usr/bin/env python3
"""Validate CEH-5W1H clustered event hypergraph JSON.

Usage:
  python validate_ceh_output.py output.json
  type output.json | python validate_ceh_output.py -
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "ceh-5w1h-v1"
NODE_GROUPS = ("who", "what", "when", "where", "why", "how")
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
REQUIRED_SENTENCE_KEYS = ("text", "tag_start", "tag_end")
REQUIRED_NODE_KEYS = ("node_type", "text", "entity_type", "tag_start", "tag_end", "evidence", "confidence")
REQUIRED_EVENT_KEYS = ("event_type", "summary", "trigger", "main", "event_hyperedge", "evidence", "confidence")
REQUIRED_EVENT_HE_KEYS = ("event", "nodes", "evidence", "missing", "confidence")
REQUIRED_RELATION_KEYS = ("relation_type", "source_events", "target_events", "evidence", "confidence")
REQUIRED_CLUSTER_KEYS = ("topic", "root_event", "events", "evidence", "confidence")


def fail(message: str) -> None:
    print(f"INVALID: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_dict(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{path} must be an object")
    return value


def require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{path} must be a list")
    return value


def load_json(arg: str) -> Any:
    if arg == "-":
        return json.load(sys.stdin)
    with Path(arg).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_id(value: str, pattern: str, path: str) -> None:
    if not re.fullmatch(pattern, value):
        fail(f"{path} has invalid id {value}")


def validate_refs(refs: Any, valid: set[str], path: str) -> None:
    for ref in require_list(refs, path):
        if ref not in valid:
            fail(f"{path} references unknown id {ref}")


def require_keys(obj: dict[str, Any], keys: tuple[str, ...], path: str) -> None:
    for key in keys:
        if key not in obj:
            fail(f"{path}.{key} is required")


def validate_offset(value: Any, path: str) -> None:
    if value is None:
        return
    if not isinstance(value, int) or value < 0:
        fail(f"{path} must be a non-negative integer or null")


def validate_span_object(obj: dict[str, Any], path: str) -> None:
    require_keys(obj, ("text", "tag_start", "tag_end"), path)
    if not isinstance(obj["text"], str):
        fail(f"{path}.text must be a string")
    validate_offset(obj["tag_start"], f"{path}.tag_start")
    validate_offset(obj["tag_end"], f"{path}.tag_end")
    start = obj["tag_start"]
    end = obj["tag_end"]
    if start is not None and end is not None and end < start:
        fail(f"{path}.tag_end must be >= tag_start")


def main() -> None:
    if len(sys.argv) != 2:
        fail("pass a JSON file path or '-' for stdin")

    data = require_dict(load_json(sys.argv[1]), "$")
    if data.get("schema_version") != SCHEMA_VERSION:
        fail(f"schema_version must be {SCHEMA_VERSION}")

    sentences = require_dict(data.get("sentences"), "sentences")
    nodes = require_dict(data.get("nodes"), "nodes")
    events = require_dict(data.get("events"), "events")
    event_hyperedges = require_dict(data.get("event_hyperedges"), "event_hyperedges")
    relation_hyperedges = require_dict(data.get("relation_hyperedges"), "relation_hyperedges")
    event_clusters = require_dict(data.get("event_clusters"), "event_clusters")

    sentence_ids = set(sentences)
    node_ids = set(nodes)
    event_ids = set(events)
    hyperedge_ids = set(event_hyperedges)

    for sid in sentence_ids:
        validate_id(sid, r"S[1-9][0-9]*", "sentences")
        sentence = require_dict(sentences[sid], f"sentences.{sid}")
        require_keys(sentence, REQUIRED_SENTENCE_KEYS, f"sentences.{sid}")
        validate_span_object(sentence, f"sentences.{sid}")
    for nid, node in nodes.items():
        validate_id(nid, r"N[1-9][0-9]*", "nodes")
        obj = require_dict(node, f"nodes.{nid}")
        require_keys(obj, REQUIRED_NODE_KEYS, f"nodes.{nid}")
        if obj.get("node_type") not in NODE_GROUPS:
            fail(f"nodes.{nid}.node_type must be a 5W1H group")
        validate_span_object(obj, f"nodes.{nid}")
        validate_refs(obj.get("evidence", []), sentence_ids, f"nodes.{nid}.evidence")

    for eid, event in events.items():
        validate_id(eid, r"E[1-9][0-9]*", "events")
        obj = require_dict(event, f"events.{eid}")
        require_keys(obj, REQUIRED_EVENT_KEYS, f"events.{eid}")
        if not isinstance(obj["summary"], str):
            fail(f"events.{eid}.summary must be a string")
        if not isinstance(obj["main"], bool):
            fail(f"events.{eid}.main must be a boolean")
        validate_span_object(require_dict(obj["trigger"], f"events.{eid}.trigger"), f"events.{eid}.trigger")
        he = obj.get("event_hyperedge")
        if he not in hyperedge_ids:
            fail(f"events.{eid}.event_hyperedge references unknown hyperedge {he}")
        validate_refs(obj.get("evidence", []), sentence_ids, f"events.{eid}.evidence")

    for hid, hyperedge in event_hyperedges.items():
        validate_id(hid, r"HE[1-9][0-9]*", "event_hyperedges")
        obj = require_dict(hyperedge, f"event_hyperedges.{hid}")
        require_keys(obj, REQUIRED_EVENT_HE_KEYS, f"event_hyperedges.{hid}")
        if obj.get("event") not in event_ids:
            fail(f"event_hyperedges.{hid}.event references unknown event")
        event = require_dict(events[obj["event"]], f"events.{obj['event']}")
        if event.get("event_hyperedge") != hid:
            fail(f"event_hyperedges.{hid}.event does not match events.{obj['event']}.event_hyperedge")
        groups = require_dict(obj.get("nodes"), f"event_hyperedges.{hid}.nodes")
        for group in NODE_GROUPS:
            if group not in groups:
                fail(f"event_hyperedges.{hid}.nodes.{group} is required")
            validate_refs(groups[group], node_ids, f"event_hyperedges.{hid}.nodes.{group}")
        validate_refs(obj.get("evidence", []), sentence_ids, f"event_hyperedges.{hid}.evidence")
        require_list(obj.get("missing", []), f"event_hyperedges.{hid}.missing")

    for rid, relation in relation_hyperedges.items():
        validate_id(rid, r"RH[1-9][0-9]*", "relation_hyperedges")
        obj = require_dict(relation, f"relation_hyperedges.{rid}")
        require_keys(obj, REQUIRED_RELATION_KEYS, f"relation_hyperedges.{rid}")
        if obj.get("relation_type") not in RELATIONS:
            fail(f"relation_hyperedges.{rid}.relation_type is not controlled")
        source_events = require_list(obj.get("source_events"), f"relation_hyperedges.{rid}.source_events")
        target_events = require_list(obj.get("target_events"), f"relation_hyperedges.{rid}.target_events")
        if not source_events:
            fail(f"relation_hyperedges.{rid}.source_events must not be empty")
        if not target_events:
            fail(f"relation_hyperedges.{rid}.target_events must not be empty")
        validate_refs(source_events, event_ids, f"relation_hyperedges.{rid}.source_events")
        validate_refs(target_events, event_ids, f"relation_hyperedges.{rid}.target_events")
        validate_refs(obj.get("evidence", []), sentence_ids, f"relation_hyperedges.{rid}.evidence")

    for cid, cluster in event_clusters.items():
        validate_id(cid, r"EC[1-9][0-9]*", "event_clusters")
        obj = require_dict(cluster, f"event_clusters.{cid}")
        require_keys(obj, REQUIRED_CLUSTER_KEYS, f"event_clusters.{cid}")
        if not isinstance(obj["topic"], str):
            fail(f"event_clusters.{cid}.topic must be a string")
        if obj.get("root_event") not in event_ids:
            fail(f"event_clusters.{cid}.root_event references unknown event")
        cluster_events = require_list(obj.get("events"), f"event_clusters.{cid}.events")
        if obj["root_event"] not in cluster_events:
            fail(f"event_clusters.{cid}.root_event must be listed in events")
        validate_refs(cluster_events, event_ids, f"event_clusters.{cid}.events")
        validate_refs(obj.get("evidence", []), sentence_ids, f"event_clusters.{cid}.evidence")

    print(
        "VALID: "
        f"{len(event_clusters)} cluster(s), "
        f"{len(events)} event(s), "
        f"{len(event_hyperedges)} event hyperedge(s), "
        f"{len(relation_hyperedges)} relation hyperedge(s)"
    )


if __name__ == "__main__":
    main()
