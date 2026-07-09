---
name: ceh-5w1h
description: Record-first Clustered Event Hypergraph for 5W1H Extraction. Use when asked to extract auditable 5W1H tags without fragmentation, keep each source text beside its tags, select one root event per record, deduplicate repeated role spans, build event-centric knowledge hypergraphs, model event-to-event relations, draw 5W1H diagrams, compare extraction stability, or produce structured data for knowledge hypergraph construction from news, military, policy, incident, technical, or report text.
---

# CEH-5W1H

## Overview

Use this skill to extract **record-first Clustered Event Hypergraphs for 5W1H**.

Keep each source `Text` beside its extracted `Tags` so humans can audit offsets immediately. Treat 5W1H as the internal structure of one root event per record, not as a global node dump.

Core idea:

```text
Record Text -> Root Event -> Deduplicated 5W1H Tags -> Event Hyperedge -> Optional Global Index
```

Default output is valid JSON unless the user asks for a diagram or explanation.

## Resource Loading

Always read:

- `references/schema.md` before producing JSON.
- `references/state-machine.md` before processing multi-record or noisy input.
- `references/role-coverage.md` before selecting 5W1H tags.
- `references/deduplication.md` before producing tags.
- `references/algorithm-playbook.md` when the task needs higher-quality extraction, paper-style method explanation, or a noisy multi-event document.
- `references/quality-checks.md` before final output.

Read as needed:

- `references/relation-vocabulary.md` only when producing optional event-to-event relations or global index output.
- `references/diagram-guide.md` when the user asks to draw or explain the structure.

## Default Workflow

1. Process one record or one source text at a time.
2. Select exactly one `Root_Event` unless the user explicitly asks for `full_detail` or `global_index`.
3. Extract 5W1H spans as inline `Tags` beside the same `Text`.
4. Deduplicate tags inside the record before output.
5. Enforce default caps: WHO <= 5, WHAT <= 2, WHEN/WHERE <= 1 each, WHY/HOW <= 2 each, total tags <= 12.
6. Project tag indexes into one `Event_Hyperedge`.
7. Validate offsets, duplicate tags, missing roles, and role caps.
8. Produce optional `ceh-5w1h-v1` global index only when explicitly requested.

## Output Contract

Use `schema_version: "ceh-record-v2"` by default.

```json
{
  "schema_version": "ceh-record-v2",
  "records": [
    {
      "Id": "sample id",
      "Text": "source text",
      "Root_Event": {
        "Event_Id": "E1",
        "Event_Text": "center event summary",
        "Trigger": {
          "Tag_Text": "trigger",
          "Tag_Start": 0,
          "Tag_End": 0
        }
      },
      "Tags": [],
      "Missing": [],
      "Event_Hyperedge": {
        "event": "E1",
        "who": [],
        "what": [],
        "when": [],
        "where": [],
        "why": [],
        "how": []
      }
    }
  ]
}
```

The important distinction:

- `Text` and `Tags` live in the same record for easy comparison.
- `Tags` use FLARES-style fields: `Tag_Text`, `Tag_Start`, `Tag_End`, `5W1H_Label`, `Reliability_Label`.
- `Event_Hyperedge` connects the root event to tag indexes, not to a huge global `nodes` object.
- `ceh-5w1h-v1` global index is optional and must be requested with `global_index=true`.

## Event Cluster Rule

Create an event cluster only in optional global-index mode or diagram explanations.

Do not create a cluster for every paragraph automatically. In default record-first mode, the record itself is the audit unit and has one root event.

Good cluster examples:

- A disclosure event plus several inventory-status events.
- A concern event plus its background plan and demonstration event.
- An exhibition event plus capability/configuration/supporting events.
- A construction announcement plus deployment sites and capability effects.

## Root Event Selection

Choose the root event with a transparent centrality rule:

```text
root_score =
  source_position
  + predicate_salience
  + relation_degree
  + evidence_density
  + cluster_explanation_power
  - side_detail_penalty
```

Prefer events that explain the cluster, organize related details, and can be read as the main claim or essential content. Do not choose a capability detail, quantity, quote, or background sentence as root if it only supports another event.

## Coarse-to-Fine Extraction

For each record:

1. Create a coarse skeleton: `who -> predicate -> what`.
2. Add directly connected participants, then qualifiers: `when`, `where`, `why`, `how`, quantities, status, conditions.
3. Convert the enriched skeleton into an event hyperedge.
4. Keep rejected details out of `Tags` unless they fill a capped role in the root event's causal, legal, operational, or opposition context.

This prevents the model from turning every sentence into an event while preserving useful fine-grained information.

## Role Questioning

Extract 5W1H by asking role-specific questions against one event at a time:

```text
who: who is the adjudicator/source/actor, regulated target, challenger, owner, participant, victim, affected party, monitoring group, or opposition group?
what: what action, claim, status, system, object, or result is central?
when: when did/will it happen, or what is the validity/as-of time?
where: where did/will it happen, or what forum, court, venue, area, system, or location is affected?
why: what cause, legal challenge, rejected rationale, motivation, risk, purpose, or claimed reason is stated?
how: what method, mechanism, order, required action, administrative measure, platform, capability, or procedure is stated?
```

Return exact source spans with `Tag_Start` and `Tag_End`. If a role is not stated, omit the tag and list the role in `Missing`.

## Deduplication And Caps

Before final output:

- Deduplicate by `5W1H_Label + normalize(Tag_Text)` inside each record.
- Prefer longer, more specific spans over generic substrings in the same role.
- Prefer an actor/source interpretation over `WHERE` when a country or organization performs the action, but allow the same span as both `WHO` and `WHERE` when it is explicitly a forum, court, meeting, base, site, or venue.
- Avoid standalone generic terms such as "system", "missile", "plan", or "currently" unless they are part of a more specific phrase.
- Enforce default caps: WHO <= 5, WHAT <= 2, WHEN/WHERE <= 1 each, WHY/HOW <= 2 each, total tags <= 12.
- Do not drop directly connected participants just because they are not the grammatical subject.

## Stability Mode

When the user asks for reliability, robustness, paper-style extraction, or high-confidence output, run or simulate multiple independent extraction passes:

- `stable`: event or node appears with the same meaning in most passes.
- `unstable`: event or node appears inconsistently, has conflicting boundaries, or changes role.
- `missed`: important evidence-backed event was absent from a pass.

Use `scripts/compare_ceh_outputs.py` to compare JSON outputs when multiple output files exist. Otherwise, perform the same check mentally before finalizing the JSON.

## Relation Vocabulary

Use these relation types by default:

```text
discloses
supports
motivates
causes
part_of
component_of
background_of
enables
contrasts_with
```

Do not invent relation names unless the user explicitly asks for an extension. If unsure, prefer `background_of` or omit the relation.

## Diagram Mode

When the user asks to "draw", "show the graph", "paint it", or "make it readable", do not let the diagram replace 5W1H extraction.

Output order:

1. A compact 5W1H table for every displayed root event.
2. Mermaid diagram showing event clusters, root events, and the six 5W1H role nodes for each displayed root event.
3. Optional relation hyperedges between events.

If the document contains many clusters, split diagrams into batches or show a compact overview plus per-cluster 5W1H diagrams. Do not omit 5W1H roles just to keep one diagram small.

In diagrams:

- Use `EC*` for event clusters.
- Use `E*` for events.
- Show six 5W1H role nodes for each displayed root event: `who`, `what`, `when`, `where`, `why`, `how`.
- Use `missing` when a 5W1H role is not stated.
- Use relation labels from the controlled vocabulary.
- Do not use generic `B*` background nodes as a replacement for event nodes or 5W1H nodes.

## Non-Negotiables

- Do not flatten a document into one global 5W1H table.
- Do not split every sentence into an event.
- Do not output a giant global `nodes` object unless the user asks for `global_index=true`.
- Do not process multiple records as one merged extraction unit.
- Do not over-compress `WHO` to only the grammatical subject; include central participants connected to the root event.
- Do not create event relations without evidence.
- Do not attach 5W1H nodes directly to clusters; attach them to events through `event_hyperedges`.
- Do not draw an event relation diagram without also showing the relevant event's 5W1H roles.
- Do not use `reports`; use `discloses` for disclosure/reporting relations.
- Do not promote quantities, equipment features, or quotes to standalone events unless they are central claims or states.
- Do not fill 5W1H from world knowledge; use stated or directly implied evidence only.
- Keep `S*`, `N*`, `E*`, `HE*`, `RH*`, and `EC*` IDs stable and compact.
