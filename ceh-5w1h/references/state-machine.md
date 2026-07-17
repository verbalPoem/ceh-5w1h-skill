# CEH-5W1H Cluster-First Controller

## States

```text
S0_READ_RECORD
  -> S1_EVIDENCE_UNITS
  -> S2_CLUSTER_DISCOVERY
  -> S3_EVENT_SELECTION
  -> S4_PER_EVENT_5W1H
  -> S5_NODE_DEDUP
  -> S6_RELATION_BUILD
  -> S7_EXTRACTOR_VALIDATION
  -> S8_INDEPENDENT_CRITIC
  -> S9_REPAIR_AND_REVALIDATE
  -> S_END
```

Failed checks return to the state that introduced the error. Retry a record at most twice, then place it in the review queue.

## S0_READ_RECORD

- Read one record only.
- Preserve the exact source string and character positions.
- Do not carry actors, clusters, roles, or missing fields from another record.
- Detect whether the input contains independent briefs pasted together.

## S1_EVIDENCE_UNITS

- Create non-overlapping evidence units `S1...Sn`.
- Prefer complete sentences.
- Allow a headline or punctuation-free complete clause as one evidence unit.
- Preserve half-open offsets.
- Do not create overlapping sliding windows.

## S2_CLUSTER_DISCOVERY

Generate candidate clusters before extracting 5W1H.

For each candidate, write an internal topic and event chain. Apply `cluster-policy.md`:

```text
coherent relation or shared central event -> same cluster
entity/topic similarity only              -> split or reject relation
independent brief                         -> separate cluster
```

Do not use paragraph boundaries as the only decision rule.

## S3_EVENT_SELECTION

Inside each cluster:

1. Identify candidate predicates.
2. Merge paraphrases, repeated facts, and numerical elaborations.
3. Reject weak details.
4. Select exactly one central event.
5. Keep only relation-critical supporting events.

Build each event skeleton:

```text
actor/source -> predicate -> object/target/result
```

An event must have a distinct predicate, useful fact, and evidence. Freeze its predicate before role extraction.

## S4_PER_EVENT_5W1H

Process one accepted event at a time.

1. Build its evidence corridor from referenced `S*` units.
2. Resolve only local, explicit coreference.
3. Ask WHO, WHAT, WHEN, WHERE, WHY, and HOW against this event's frozen predicate.
4. Reject answers belonging to another event.
5. Minimize spans while preserving complete answers.
6. Classify WHY/HOW by proposition direction, not lexical cues.
7. Compute offsets only after final span selection.

Use `Missing` for unsupported roles.

## S5_NODE_DEDUP

Build record-local `N*` nodes after all events have candidates.

Deduplicate by:

```text
Node_Type + normalized referent/text
```

- Collapse aliases, titles, pronouns, and repeated mentions.
- Reuse a node ID across hyperedges when role and referent are the same.
- Keep distinct entities that share a country or organization.
- Reject clause-length WHO nodes.
- Keep the clearest explicit mention as the canonical span.

## S6_RELATION_BUILD

Add directed event relations only after events are stable.

Use the controlled vocabulary in `relation-vocabulary.md`. Require:

- valid source and target events;
- at least one supporting `S*` ID;
- a relation stronger than topic similarity.

Do not connect every event pair. A supporting event with no useful relation should be merged, removed, or moved to another cluster.

## S7_EXTRACTOR_VALIDATION

Before review, check:

- all offsets;
- unique `S*`, `N*`, `EC*`, `E*`, `HE*`, and relation IDs;
- exactly one central event per cluster;
- node types match hyperedge role keys;
- per-event caps and `Missing`;
- no duplicate event propositions;
- no unsupported relations.

Run:

```text
python scripts/validate_ceh_cluster_output.py candidate.json
```

Structural success does not make the annotation final.

## S8_INDEPENDENT_CRITIC

Follow `reviewer-protocol.md`.

When sub-agents are available, start a fresh critic with:

- raw `Text`;
- candidate JSON;
- `schema.md`;
- `cluster-policy.md`;
- `role-coverage.md`;
- `semantic-role-reasoning.md`;
- the critic checklist.

Do not give it the extractor's hidden reasoning or intended answer.

The critic must return:

```text
PASS
or
REVISE with machine-actionable issues
or
NEEDS_HUMAN_REVIEW
```

## S9_REPAIR_AND_REVALIDATE

- Apply only corrections supported by the source.
- Recompute affected offsets and references.
- Re-run structural validation.
- Re-run the independent critic after a cluster split/merge, central-event change, event deletion/addition, or WHY/HOW reassignment.
- Run the deterministic risk linter last.

```text
python scripts/validate_ceh_cluster_semantic_output.py final.json --report risk-report.json
```

The risk linter cannot verify semantics. Unresolved semantic disagreement sets `Review.Status` to `needs_human_review`.

## Batch Transition

```text
one record
  -> S0...S9
  -> passed/revised or review queue
  -> clear record memory
  -> next record
```

Send one record per extraction call and one candidate per critic call. Reset extraction context after at most 100 completed records.
