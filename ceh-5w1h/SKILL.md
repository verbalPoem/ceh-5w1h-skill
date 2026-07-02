---
name: ceh-5w1h
description: Clustered Event Hypergraph for 5W1H Extraction. Use when asked to extract 5W1H without fragmenting text, group related events into event clusters, build event-centric knowledge hypergraphs, model event-to-event relations, draw event cluster diagrams, or produce structured data for knowledge hypergraph construction from news, military, policy, incident, technical, or report text.
---

# CEH-5W1H

## Overview

Use this skill to extract **Clustered Event Hypergraphs for 5W1H**.

Do not treat 5W1H as the final result. Treat 5W1H as the internal structure of an event. First group related events into event clusters, then extract each event as a 5W1H hyperedge, then connect events with relation hyperedges.

Core idea:

```text
Document -> Event Clusters -> Events -> 5W1H Event Hyperedges -> Event Relation Hyperedges
```

Default output is valid JSON unless the user asks for a diagram or explanation.

## Resource Loading

Always read:

- `references/schema.md` before producing JSON.
- `references/relation-vocabulary.md` before assigning event-to-event relations.
- `references/state-machine.md` when input is long, noisy, or multi-event.
- `references/quality-checks.md` before final output.

Read as needed:

- `references/diagram-guide.md` when the user asks to draw or explain the structure.

## Default Workflow

1. Segment the input into topic-level event clusters, not sentence-level fragments.
2. Identify event candidates inside each cluster.
3. Pick a `root_event` for each cluster: the event that best represents the cluster's essential point.
4. Extract each accepted event's 5W1H nodes.
5. Project each accepted event into one `event_hyperedge`.
6. Connect events using `relation_hyperedges` from the controlled relation vocabulary.
7. Validate that clusters are coherent, event relations are useful, and 5W1H nodes are not scattered outside events.

## Output Contract

Use `schema_version: "ceh-5w1h-v1"`.

```json
{
  "schema_version": "ceh-5w1h-v1",
  "sentences": {},
  "nodes": {},
  "events": {},
  "event_hyperedges": {},
  "relation_hyperedges": {},
  "event_clusters": {}
}
```

The important distinction:

- `nodes`: indexed 5W1H nodes such as `N1`, `N2`.
- `events`: event frames such as `E1`, `E2`.
- `event_hyperedges`: one event connected to its 5W1H nodes.
- `relation_hyperedges`: event-to-event relations such as `discloses`, `motivates`, `background_of`.
- `event_clusters`: topic-level groups such as `EC1`, `EC2`.

## Event Cluster Rule

Create an event cluster when several events share the same issue, system, actor, report, operation, project, accident, or policy thread.

Do not create a cluster for every paragraph automatically. Create a cluster only when it helps preserve event coherence.

Good cluster examples:

- A disclosure event plus several inventory-status events.
- A concern event plus its background plan and demonstration event.
- An exhibition event plus capability/configuration/supporting events.
- A construction announcement plus deployment sites and capability effects.

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

When the user asks to "draw", "show the graph", "paint it", or "make it readable", output Mermaid first and keep JSON secondary or omit it if not requested.

In diagrams:

- Use `EC*` for event clusters.
- Use `E*` for events.
- Show only high-value 5W1H nodes for the root event unless the user asks for full detail.
- Use relation labels from the controlled vocabulary.

## Non-Negotiables

- Do not flatten a document into one global 5W1H table.
- Do not split every sentence into an event.
- Do not create event relations without evidence.
- Do not attach 5W1H nodes directly to clusters; attach them to events through `event_hyperedges`.
- Do not use `reports`; use `discloses` for disclosure/reporting relations.
- Keep `S*`, `N*`, `E*`, `HE*`, `RH*`, and `EC*` IDs stable and compact.
