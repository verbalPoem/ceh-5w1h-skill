# CEH-5W1H Quality Gates

Passing syntax or offsets is not evidence of semantic accuracy. Release requires four gates.

## Gate A: Cluster And Event Semantics

- Cluster discovery happened before role extraction.
- Independent briefs are in separate clusters.
- Every cluster has exactly one central event.
- Supporting events have distinct predicates and useful controlled relations.
- Repeated claims, quantities, specifications, and aliases are not separate events.
- The central event organizes the cluster rather than merely appearing first.

Failure here returns to cluster/event selection. Do not try to repair bad decomposition by adding more nodes.

## Gate B: Per-Event 5W1H Semantics

For every event:

- all roles attach to its frozen predicate;
- WHO nodes are minimal entities, not clauses;
- WHAT contains the event action/state and required object/result;
- WHEN and WHERE belong to this event;
- WHY is a supported explanatory proposition with direction `C -> E`;
- HOW is a supported means/procedure proposition with direction `C -> E`;
- consequences, topic similarity, and neighboring-event details are rejected;
- aliases and repeated mentions are collapsed;
- `Missing` is preferred over a weak answer.

Cue words are neither necessary nor sufficient for WHY/HOW.

## Gate C: Independent Agent Review

Follow `reviewer-protocol.md`.

- The critic receives raw text and candidate output, not hidden extractor reasoning.
- It checks clusters before events, and events before roles.
- Valid corrections are applied.
- Major semantic corrections are re-reviewed.
- The record's `Review` object accurately states `independent_agent` or `self_critic_fallback`.
- Fallback review remains `needs_human_review`.

An extractor's own second pass is useful but is not an independent review.

## Gate D: Deterministic Validation

Run:

```text
python scripts/validate_ceh_cluster_output.py output.json
python scripts/validate_ceh_cluster_semantic_output.py output.json --report risk-report.json
```

The structural validator checks:

- schema and required fields;
- exact sentence, node, and trigger offsets;
- unique IDs and valid references;
- node types and hyperedge role groups;
- per-event caps and exact `Missing`;
- relation endpoints and evidence IDs;
- review metadata.

The risk linter flags:

- unusually dense clusters or events;
- duplicate event summaries or identical hyperedges;
- supporting events with no relation;
- long or clause-like WHO nodes;
- suspicious WHAT, WHEN, WHERE, WHY, and HOW spans;
- attribution-shell triggers and other known boundary risks.

Neither script understands causality or method.

## Batch Drift Checks

- One source record per extraction call.
- One candidate record per critic call.
- No state carried across records.
- Context reset after at most 100 completed records.
- Failed records retried independently.
- Unresolved records kept in a review queue.
- Mean clusters, events, nodes, WHO count, and WHY/HOW fill rates monitored over time.

Drift warnings:

- nearly every sentence becomes an event;
- most clusters hit the hard event cap;
- the same actor is recreated as multiple nodes;
- most events have non-empty WHY/HOW despite sparse source evidence;
- later batches contain longer WHO/WHAT spans than earlier batches;
- independent critic revisions rise sharply.

## Known Release-Blocking Failures

- direct extraction to one root event skipped cluster discovery;
- one paragraph was treated as one cluster without semantic testing;
- numerical procurement or inventory details became many events;
- one event borrowed another event's time, place, cause, or method;
- repeated aliases created separate nodes;
- WHO contains predicates or full clauses;
- WHY/HOW came from marker matching;
- event relations express only topic similarity;
- the risk linter was described as a semantic Agent;
- fallback self-review was labeled independent;
- valid JSON was called high quality without gold evaluation.

Measured quality still requires comparison against a manually annotated, independently reviewed Chinese gold sample. The gates prevent known failures; they do not guarantee perfect extraction.
