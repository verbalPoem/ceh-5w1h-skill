#!/usr/bin/env python3
"""Convert legacy global CEH JSON into record-first CEH v2 JSON.

Usage:
  python convert_ceh_global_to_record_view.py old_ceh.json new_record_v2.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LABELS = ("WHO", "WHAT", "WHEN", "WHERE", "WHY", "HOW")
ROLE_KEYS = tuple(label.lower() for label in LABELS)
ROLE_CAPS = {
    "WHO": 2,
    "WHAT": 2,
    "WHEN": 1,
    "WHERE": 1,
    "WHY": 1,
    "HOW": 1,
}
TOTAL_TAG_CAP = 8
ROLE_PRIORITY = {"WHO": 0, "WHAT": 1, "WHEN": 2, "WHERE": 3, "WHY": 4, "HOW": 5}
GENERIC_TERMS = {
    "系统",
    "导弹",
    "武器",
    "飞机",
    "潜艇",
    "平台",
    "项目",
    "计划",
    "目前",
    "公司",
    "海军",
    "空军",
    "陆军",
    "国军",
    "中心",
    "system",
    "missile",
    "weapon",
    "aircraft",
    "platform",
    "project",
    "plan",
    "currently",
    "company",
    "navy",
    "army",
    "air force",
}
METHOD_MARKERS = ("利用", "通过", "采用", "使用", "借助", "基于", "依托", "以")
METHOD_BOUNDARIES = ("展示", "演示", "部署", "完成", "提高", "击落", "拦截", "摧毁", "交付", "授予")
METHOD_SIGNALS = (
    "建模",
    "制导",
    "雷达",
    "传感器",
    "数据链",
    "通信",
    "火控",
    "自动",
    "计算机",
    "激光",
    "仿真",
    "测试",
    "升级",
    "modeling",
    "guidance",
    "radar",
    "sensor",
    "laser",
    "computer",
)
TRIGGER_FALLBACKS = (
    "公开",
    "宣布",
    "表示",
    "称",
    "报道",
    "透露",
    "展示",
    "演示",
    "部署",
    "完成",
    "交付",
    "授予",
    "签署",
    "采购",
    "升级",
    "削减",
    "进入",
    "死亡",
)


@dataclass
class Candidate:
    label: str
    text: str
    start: int
    end: int
    confidence: float
    source_id: str
    entity_type: str

    @property
    def norm(self) -> str:
        return normalize(self.text)

    @property
    def is_generic(self) -> bool:
        return self.norm in GENERIC_NORMS


def natural_id_key(value: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-Za-z_]+)([0-9]+)", value)
    if not match:
        return value, 0
    return match.group(1), int(match.group(2))


def normalize(text: str) -> str:
    value = re.sub(r"\s+", " ", text.casefold().strip())
    return re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", value)


GENERIC_NORMS = {normalize(item) for item in GENERIC_TERMS}


def has_method_signal(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in text for marker in METHOD_MARKERS) or any(signal in lowered for signal in METHOD_SIGNALS)


def overlap_ratio(a: Candidate, b: Candidate) -> float:
    overlap = max(0, min(a.end, b.end) - max(a.start, b.start))
    if overlap == 0:
        return 0.0
    return overlap / max(1, min(a.end - a.start, b.end - b.start))


def refine_how_span(record_text: str, start: int, end: int) -> tuple[int, int] | None:
    """Shrink noisy HOW spans to a method phrase when a marker is present."""
    segment = record_text[start:end]
    marker_positions = [(segment.find(marker), marker) for marker in METHOD_MARKERS if segment.find(marker) >= 0]
    if not marker_positions:
        return (start, end) if has_method_signal(segment) else None

    marker_pos, _marker = min(marker_positions, key=lambda item: item[0])
    tail = segment[marker_pos:]
    boundary_indexes = [tail.find(boundary) for boundary in METHOD_BOUNDARIES if tail.find(boundary) > 0]
    punctuation_indexes = [tail.find(punct) for punct in ("，", "。", "；", ";", ",", ".") if tail.find(punct) > 0]
    stop_candidates = boundary_indexes + punctuation_indexes
    stop = min(stop_candidates) if stop_candidates else len(tail)
    new_start = start + marker_pos
    new_end = new_start + stop
    if new_end <= new_start:
        return None
    return new_start, new_end


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object")
    return data


def sentence_text(sentences: dict[str, Any], sid: str) -> str:
    sentence = sentences.get(sid, {})
    if not isinstance(sentence, dict):
        return ""
    text = sentence.get("text", "")
    return text if isinstance(text, str) else ""


def ordered_unique_sentence_ids(ids: list[Any], sentences: dict[str, Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in sorted((sid for sid in ids if isinstance(sid, str)), key=natural_id_key):
        if item in seen or item not in sentences:
            continue
        seen.add(item)
        result.append(item)
    return result


def build_record_text(sentence_ids: list[str], sentences: dict[str, Any]) -> tuple[str, dict[str, int]]:
    pieces: list[str] = []
    offsets: dict[str, int] = {}
    cursor = 0
    for sid in sentence_ids:
        text = sentence_text(sentences, sid)
        if not text:
            continue
        if pieces:
            pieces.append(" ")
            cursor += 1
        offsets[sid] = cursor
        pieces.append(text)
        cursor += len(text)
    return "".join(pieces), offsets


def find_span(
    record_text: str,
    sentence_ids: list[str],
    sentence_offsets: dict[str, int],
    sentences: dict[str, Any],
    tag_text: str,
    start: Any,
    end: Any,
) -> tuple[int, int] | None:
    if not tag_text:
        return None
    if isinstance(start, int) and isinstance(end, int):
        if 0 <= start <= end <= len(record_text) and record_text[start:end] == tag_text:
            return start, end
        for sid in sentence_ids:
            sent = sentence_text(sentences, sid)
            base = sentence_offsets.get(sid)
            if base is None:
                continue
            if 0 <= start <= end <= len(sent) and sent[start:end] == tag_text:
                return base + start, base + end
    for sid in sentence_ids:
        sent = sentence_text(sentences, sid)
        base = sentence_offsets.get(sid)
        if base is None:
            continue
        pos = sent.find(tag_text)
        if pos >= 0:
            return base + pos, base + pos + len(tag_text)
    pos = record_text.find(tag_text)
    if pos >= 0:
        return pos, pos + len(tag_text)
    return None


def compact_event_text(summary: Any, fallback_text: str) -> str:
    if isinstance(summary, str):
        value = re.sub(r"\s+", " ", summary).strip()
        if 0 < len(value) <= 160:
            return value
    fallback = re.sub(r"\s+", " ", fallback_text).strip()
    if len(fallback) > 160:
        return fallback[:157] + "..."
    return fallback


def build_trigger(
    event: dict[str, Any],
    record_text: str,
    sentence_ids: list[str],
    sentence_offsets: dict[str, int],
    sentences: dict[str, Any],
) -> dict[str, Any]:
    raw_trigger = event.get("trigger", {})
    if not isinstance(raw_trigger, dict):
        raw_trigger = {}
    trigger_text = raw_trigger.get("text", "")
    if not isinstance(trigger_text, str):
        trigger_text = ""
    span = find_span(
        record_text,
        sentence_ids,
        sentence_offsets,
        sentences,
        trigger_text,
        raw_trigger.get("tag_start"),
        raw_trigger.get("tag_end"),
    )
    if span:
        return {"Tag_Text": trigger_text, "Tag_Start": span[0], "Tag_End": span[1]}
    for fallback in TRIGGER_FALLBACKS:
        pos = record_text.find(fallback)
        if pos >= 0:
            return {"Tag_Text": fallback, "Tag_Start": pos, "Tag_End": pos + len(fallback)}
    return {"Tag_Text": "", "Tag_Start": 0, "Tag_End": 0}


def collect_candidates(
    event: dict[str, Any],
    data: dict[str, Any],
    record_text: str,
    sentence_ids: list[str],
    sentence_offsets: dict[str, int],
) -> list[Candidate]:
    sentences = data.get("sentences", {})
    nodes = data.get("nodes", {})
    event_hyperedges = data.get("event_hyperedges", {})
    if not isinstance(sentences, dict) or not isinstance(nodes, dict) or not isinstance(event_hyperedges, dict):
        return []
    hyperedge_id = event.get("event_hyperedge")
    hyperedge = event_hyperedges.get(hyperedge_id, {})
    if not isinstance(hyperedge, dict):
        return []
    role_nodes = hyperedge.get("nodes", {})
    if not isinstance(role_nodes, dict):
        return []

    candidates: list[Candidate] = []
    for role in ROLE_KEYS:
        label = role.upper()
        raw_node_ids = role_nodes.get(role, [])
        if not isinstance(raw_node_ids, list):
            continue
        for node_id in raw_node_ids:
            node = nodes.get(node_id, {})
            if not isinstance(node, dict):
                continue
            tag_text = node.get("text", "")
            if not isinstance(tag_text, str):
                continue
            tag_text = tag_text.strip()
            if not tag_text:
                continue
            if len(normalize(tag_text)) <= 1:
                continue
            span = find_span(
                record_text,
                sentence_ids,
                sentence_offsets,
                sentences,
                tag_text,
                node.get("tag_start"),
                node.get("tag_end"),
            )
            if span is None:
                continue
            if label == "HOW":
                refined_span = refine_how_span(record_text, span[0], span[1])
                if refined_span is None:
                    continue
                span = refined_span
            confidence = node.get("confidence", 0.0)
            if not isinstance(confidence, (int, float)):
                confidence = 0.0
            entity_type = node.get("entity_type", "")
            candidates.append(
                Candidate(
                    label=label,
                    text=record_text[span[0] : span[1]],
                    start=span[0],
                    end=span[1],
                    confidence=float(confidence),
                    source_id=str(node_id),
                    entity_type=entity_type if isinstance(entity_type, str) else "",
                )
            )
    return candidates


def deduplicate_candidates(candidates: list[Candidate]) -> list[Candidate]:
    by_label_text: dict[tuple[str, str], Candidate] = {}
    for candidate in candidates:
        key = (candidate.label, candidate.norm)
        current = by_label_text.get(key)
        if current is None:
            by_label_text[key] = candidate
            continue
        replacement_score = (len(candidate.text), candidate.confidence, -candidate.start)
        current_score = (len(current.text), current.confidence, -current.start)
        if replacement_score > current_score:
            by_label_text[key] = candidate

    items = list(by_label_text.values())

    role_filtered: list[Candidate] = []
    for label in LABELS:
        role_items = [item for item in items if item.label == label]
        role_items.sort(key=lambda item: (-len(item.text), item.start, -item.confidence))
        kept: list[Candidate] = []
        for item in role_items:
            if item.is_generic and any(other.label == label and other.norm != item.norm for other in role_items):
                continue
            if any(item.norm and item.norm in other.norm and item.norm != other.norm for other in kept):
                continue
            kept.append(item)
        role_filtered.extend(kept)

    by_text: dict[str, Candidate] = {}
    for item in role_filtered:
        current = by_text.get(item.norm)
        if current is None:
            by_text[item.norm] = item
            continue
        item_key = (ROLE_PRIORITY[item.label], -len(item.text), item.start)
        current_key = (ROLE_PRIORITY[current.label], -len(current.text), current.start)
        if item_key < current_key:
            by_text[item.norm] = item

    values = list(by_text.values())
    who_norms = [item.norm for item in values if item.label == "WHO"]
    values = [
        item
        for item in values
        if not (
            item.label == "WHERE"
            and any(item.norm and (item.norm in who_norm or who_norm in item.norm) for who_norm in who_norms)
        )
    ]
    what_items = [item for item in values if item.label == "WHAT"]
    values = [
        item
        for item in values
        if not (
            item.label == "HOW"
            and not has_method_signal(item.text)
            and any(overlap_ratio(item, other) >= 0.5 for other in what_items)
        )
    ]

    capped: list[Candidate] = []
    for label in LABELS:
        role_items = [item for item in values if item.label == label]
        role_items.sort(key=lambda item: (item.is_generic, item.start, -len(item.text), -item.confidence))
        capped.extend(role_items[: ROLE_CAPS[label]])

    capped.sort(key=lambda item: (ROLE_PRIORITY[item.label], item.start, -len(item.text)))
    return capped[:TOTAL_TAG_CAP]


def make_record(cluster_id: str, cluster: dict[str, Any], data: dict[str, Any]) -> dict[str, Any] | None:
    sentences = data.get("sentences", {})
    events = data.get("events", {})
    event_hyperedges = data.get("event_hyperedges", {})
    if not isinstance(sentences, dict) or not isinstance(events, dict) or not isinstance(event_hyperedges, dict):
        return None
    root_event_id = cluster.get("root_event")
    if not isinstance(root_event_id, str):
        return None
    root_event = events.get(root_event_id, {})
    if not isinstance(root_event, dict):
        return None

    hyperedge = event_hyperedges.get(root_event.get("event_hyperedge"), {})
    evidence_pool: list[Any] = []
    for source in (cluster.get("evidence"), root_event.get("evidence"), hyperedge.get("evidence") if isinstance(hyperedge, dict) else None):
        if isinstance(source, list):
            evidence_pool.extend(source)
    sentence_ids = ordered_unique_sentence_ids(evidence_pool, sentences)
    if not sentence_ids:
        return None
    record_text, sentence_offsets = build_record_text(sentence_ids, sentences)
    if not record_text:
        return None

    trigger = build_trigger(root_event, record_text, sentence_ids, sentence_offsets, sentences)
    event_text = compact_event_text(root_event.get("summary"), sentence_text(sentences, sentence_ids[0]))
    candidates = deduplicate_candidates(collect_candidates(root_event, data, record_text, sentence_ids, sentence_offsets))

    tags: list[dict[str, Any]] = []
    hyperedge_indexes = {role: [] for role in ROLE_KEYS}
    for candidate in candidates:
        index = len(tags)
        tags.append(
            {
                "Tag_Text": candidate.text,
                "Tag_Start": candidate.start,
                "Tag_End": candidate.end,
                "5W1H_Label": candidate.label,
                "Reliability_Label": "converted",
            }
        )
        hyperedge_indexes[candidate.label.lower()].append(index)

    missing = [label for label in LABELS if not hyperedge_indexes[label.lower()]]
    return {
        "Id": cluster_id,
        "Text": record_text,
        "Root_Event": {
            "Event_Id": "E1",
            "Event_Text": event_text,
            "Trigger": trigger,
        },
        "Tags": tags,
        "Missing": missing,
        "Event_Hyperedge": {
            "event": "E1",
            **hyperedge_indexes,
        },
    }


def convert(data: dict[str, Any], *, limit: int | None = None) -> dict[str, Any]:
    clusters = data.get("event_clusters", {})
    if not isinstance(clusters, dict):
        raise ValueError("input JSON must contain event_clusters object")
    records: list[dict[str, Any]] = []
    for cluster_id in sorted(clusters, key=natural_id_key):
        cluster = clusters.get(cluster_id)
        if not isinstance(cluster, dict):
            continue
        record = make_record(cluster_id, cluster, data)
        if record is None:
            continue
        records.append(record)
        if limit is not None and len(records) >= limit:
            break
    return {"schema_version": "ceh-record-v2", "records": records}


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert legacy CEH global JSON to ceh-record-v2.")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--limit", type=int, default=None, help="convert only the first N records")
    parser.add_argument("--force", action="store_true", help="overwrite output_json if it exists")
    args = parser.parse_args()

    if args.output_json.exists() and not args.force:
        print(f"ERROR: output exists: {args.output_json}. Use --force to overwrite.", file=sys.stderr)
        raise SystemExit(2)

    data = load_json(args.input_json)
    output = convert(data, limit=args.limit)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    records = output["records"]
    tag_count = sum(len(record.get("Tags", [])) for record in records)
    max_tags = max((len(record.get("Tags", [])) for record in records), default=0)
    avg_tags = tag_count / len(records) if records else 0.0
    print(
        "CONVERTED: "
        f"{len(records)} record(s), {tag_count} tag(s), "
        f"avg_tags={avg_tags:.2f}, max_tags={max_tags}, "
        f"output={args.output_json}"
    )


if __name__ == "__main__":
    main()
