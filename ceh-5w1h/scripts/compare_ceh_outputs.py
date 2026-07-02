#!/usr/bin/env python3
"""Compare multiple CEH-5W1H JSON outputs for extraction stability.

The script is intentionally lightweight: it compares normalized event summaries,
cluster topics, relation triples, and role-node text. It is a diagnostic helper,
not a replacement for human review.

Usage:
  python compare_ceh_outputs.py pass1.json pass2.json pass3.json
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROLE_NAMES = ("who", "what", "when", "where", "why", "how")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize(text: Any) -> str:
    if text is None:
        return ""
    lowered = str(text).casefold()
    return re.sub(r"\s+", " ", lowered).strip()


def load(path: str) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        fail(f"{path} does not contain a JSON object")
    return data


def collect_event_signatures(data: dict[str, Any]) -> set[str]:
    events = data.get("events", {})
    if not isinstance(events, dict):
        return set()
    signatures = set()
    for event in events.values():
        if isinstance(event, dict):
            summary = normalize(event.get("summary"))
            event_type = normalize(event.get("event_type"))
            if summary:
                signatures.add(f"{event_type}|{summary}")
    return signatures


def collect_cluster_topics(data: dict[str, Any]) -> set[str]:
    clusters = data.get("event_clusters", {})
    if not isinstance(clusters, dict):
        return set()
    return {
        normalize(cluster.get("topic"))
        for cluster in clusters.values()
        if isinstance(cluster, dict) and normalize(cluster.get("topic"))
    }


def collect_relation_signatures(data: dict[str, Any]) -> set[str]:
    events = data.get("events", {})
    relations = data.get("relation_hyperedges", {})
    if not isinstance(events, dict) or not isinstance(relations, dict):
        return set()
    event_labels = {
        event_id: normalize(event.get("summary"))
        for event_id, event in events.items()
        if isinstance(event, dict)
    }
    signatures = set()
    for relation in relations.values():
        if not isinstance(relation, dict):
            continue
        relation_type = normalize(relation.get("relation_type"))
        source_labels = [event_labels.get(eid, normalize(eid)) for eid in relation.get("source_events", [])]
        target_labels = [event_labels.get(eid, normalize(eid)) for eid in relation.get("target_events", [])]
        if relation_type and source_labels and target_labels:
            signatures.add(f"{relation_type}|{';'.join(source_labels)}->{';'.join(target_labels)}")
    return signatures


def collect_role_signatures(data: dict[str, Any]) -> set[str]:
    nodes = data.get("nodes", {})
    events = data.get("events", {})
    hyperedges = data.get("event_hyperedges", {})
    if not isinstance(nodes, dict) or not isinstance(events, dict) or not isinstance(hyperedges, dict):
        return set()

    event_labels = {
        event_id: normalize(event.get("summary"))
        for event_id, event in events.items()
        if isinstance(event, dict)
    }
    signatures = set()
    for hyperedge in hyperedges.values():
        if not isinstance(hyperedge, dict):
            continue
        event_label = event_labels.get(hyperedge.get("event"), normalize(hyperedge.get("event")))
        groups = hyperedge.get("nodes", {})
        if not isinstance(groups, dict):
            continue
        for role in ROLE_NAMES:
            for node_id in groups.get(role, []):
                node = nodes.get(node_id, {})
                if isinstance(node, dict):
                    node_text = normalize(node.get("text"))
                    if event_label and node_text:
                        signatures.add(f"{event_label}|{role}|{node_text}")
    return signatures


def classify(counter: Counter[str], total: int) -> tuple[list[str], list[str], list[str]]:
    stable_threshold = max(2, (total + 1) // 2)
    stable = sorted(item for item, count in counter.items() if count >= stable_threshold)
    unstable = sorted(item for item, count in counter.items() if 1 < count < stable_threshold)
    one_off = sorted(item for item, count in counter.items() if count == 1)
    return stable, unstable, one_off


def print_section(title: str, items: list[str], limit: int = 20) -> None:
    print(f"\n## {title} ({len(items)})")
    for item in items[:limit]:
        print(f"- {item}")
    if len(items) > limit:
        print(f"- ... {len(items) - limit} more")


def main() -> None:
    if len(sys.argv) < 3:
        fail("pass at least two CEH JSON files")

    paths = sys.argv[1:]
    outputs = [load(path) for path in paths]
    total = len(outputs)
    collectors = {
        "event": collect_event_signatures,
        "cluster": collect_cluster_topics,
        "relation": collect_relation_signatures,
        "role_node": collect_role_signatures,
    }

    print(f"Compared {total} CEH output files")
    for name, collector in collectors.items():
        counter: Counter[str] = Counter()
        per_file: dict[str, set[str]] = {}
        for path, output in zip(paths, outputs):
            signatures = collector(output)
            per_file[path] = signatures
            counter.update(signatures)
        stable, unstable, one_off = classify(counter, total)
        print_section(f"{name}: stable", stable)
        print_section(f"{name}: unstable", unstable)
        print_section(f"{name}: one-pass only", one_off)


if __name__ == "__main__":
    main()
