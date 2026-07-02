---
name: ceh-5w1h
description: Stability-controlled Clustered Event Hypergraph for 5W1H Extraction. Use when asked to extract 5W1H without fragmenting text, group related events into event clusters, build event-centric knowledge hypergraphs, model event-to-event relations, draw event cluster diagrams, compare multi-pass extraction stability, or produce structured data for knowledge hypergraph construction from news, military, policy, incident, technical, or report text.
---

# CEH-5W1H

## Overview

Use this skill to extract **Clustered Event Hypergraphs for 5W1H**.

Do not treat 5W1H as the final result. Treat 5W1H as the internal structure of an event. First group related events into event clusters, then extract each event as a 5W1H hyperedge, then connect events with relation hyperedges.

Core idea:

```text
Document -> Event Clusters -> Root Events -> Candidate Spans -> Skeletons -> 5W1H Event Hyperedges -> Event Relation Hyperedges -> Stability Check
```

Default output is valid JSON unless the user asks for a diagram or explanation.

## Resource Loading

Always read:

- `references/schema.md` before producing JSON.
- `references/relation-vocabulary.md` before assigning event-to-event relations.
- `references/state-machine.md` when input is long, noisy, or multi-event.
- `references/algorithm-playbook.md` when the task needs higher-quality extraction, paper-style method explanation, or a noisy multi-event document.
- `references/quality-checks.md` before final output.

Read as needed:

- `references/diagram-guide.md` when the user asks to draw or explain the structure.

## Default Workflow

1. Segment the input into topic-level event clusters, not sentence-level fragments.
2. Identify event candidates inside each cluster and score their centrality.
3. Pick a `root_event` for each cluster: the event that best represents the cluster's essential point.
4. Build a coarse event skeleton first: actor, predicate, object or state.
5. Refine the skeleton with 5W1H spans using role questions and exact source offsets.
6. Project each accepted event into one `event_hyperedge`.
7. Connect events using `relation_hyperedges` from the controlled relation vocabulary.
8. Validate coherence, evidence, missing roles, and optional multi-pass stability.

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

For each accepted event:

1. Create a coarse skeleton: `who -> predicate -> what`.
2. Add qualifiers: `when`, `where`, `why`, `how`, quantities, status, conditions.
3. Convert the enriched skeleton into an event hyperedge.
4. Keep rejected details as nodes only when they fill a role of an accepted event.

This prevents the model from turning every sentence into an event while preserving useful fine-grained information.

## Role Questioning

Extract 5W1H by asking role-specific questions against one event at a time:

```text
who: who is the actor, source, owner, participant, victim, or affected party?
what: what action, claim, status, system, object, or result is central?
when: when did/will it happen, or what is the validity/as-of time?
where: where did/will it happen, or what area/system/location is affected?
why: what cause, motivation, risk, purpose, or claimed reason is stated?
how: what method, mechanism, platform, capability, or procedure is stated?
```

Return exact source spans with `tag_start` and `tag_end`. If a role is not stated, use an empty list and list the role in `missing`.

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
- Do not create event relations without evidence.
- Do not attach 5W1H nodes directly to clusters; attach them to events through `event_hyperedges`.
- Do not draw an event relation diagram without also showing the relevant event's 5W1H roles.
- Do not use `reports`; use `discloses` for disclosure/reporting relations.
- Do not promote quantities, equipment features, or quotes to standalone events unless they are central claims or states.
- Do not fill 5W1H from world knowledge; use stated or directly implied evidence only.
- Keep `S*`, `N*`, `E*`, `HE*`, `RH*`, and `EC*` IDs stable and compact.
