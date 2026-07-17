---
name: ceh-5w1h
description: Cluster-first Chinese 5W1H extraction and Clustered Event Hypergraph construction. Use for news, military, policy, incident, technical, or report text when Codex must first discover coherent event clusters, identify a small set of related events inside each cluster, extract exact-span WHO/WHAT/WHEN/WHERE/WHY/HOW nodes for every accepted event, connect events with controlled relations, deduplicate aliases, validate offsets and semantics, and require an independent critic-agent review before release.
---

# CEH-5W1H

## Purpose

Build a readable, auditable event hypergraph without shredding the text:

```text
Text
  -> Event Clusters
  -> Central + Supporting Events
  -> Per-Event 5W1H Nodes
  -> Event Hyperedges + Event Relations
  -> Independent Critic
  -> Repair + Deterministic Validation
```

Default to precision over coverage. A missing role or rejected side event is better than a plausible but weak node.

## Required References

Read these before extraction:

- `references/schema.md`
- `references/cluster-policy.md`
- `references/state-machine.md`
- `references/role-coverage.md`
- `references/semantic-role-reasoning.md`
- `references/deduplication.md`
- `references/reviewer-protocol.md`
- `references/quality-checks.md`

Read as needed:

- `references/chinese-calibration-cases.md` for Chinese boundary examples.
- `references/cross-lingual-calibration.md` and `references/gold-calibration.md` for dataset work.
- `references/algorithm-playbook.md` for method explanations or difficult records.
- `references/relation-vocabulary.md` before adding event relations.
- `references/reliability.md` only when reliability labels are requested.
- `references/diagram-guide.md` when drawing the graph.

## Strict Default Workflow

1. Process exactly one source record at a time.
2. Segment the record into exact-offset evidence sentences `S1...Sn`.
3. Discover coherent event clusters before selecting events. Do not equate a paragraph or sentence with a cluster.
4. For each cluster, select exactly one central event and only relation-critical supporting events.
5. Require every accepted event to have a distinct predicate, an independently useful fact, and direct evidence.
6. Extract 5W1H separately for every accepted event. Freeze that event's predicate and reject roles belonging only to neighboring events.
7. Store exact spans as record-local nodes `N1...Nn`; reuse the same node ID when the same referent and role is shared by multiple events.
8. Connect each event and its 5W1H nodes with one event hyperedge.
9. Add only evidence-backed event relations from the controlled vocabulary.
10. Run an independent critic Agent, apply its valid corrections, then run structural and risk validators.

Do not expose scratch reasoning. Return JSON, a compact table, or a diagram as requested.

## Cluster And Event Guardrails

Typical defaults:

```text
clusters per record: 1-3
events per cluster:  1 central + 0-2 supporting
hard event maximum:  5 per cluster
```

Exceed the typical range only when distinct predicates and explicit relations make the extra structure necessary.

Do not promote these to standalone events:

- repeated mentions or paraphrases of the same fact;
- numerical breakdowns, specifications, or ranked lists that only qualify one state;
- a quote or reporting shell when a stronger embedded event exists;
- a consequence, capability, or background fact with no useful relation to the cluster's central event.

Do retain a supporting event when removing it would erase a distinct causal, motivational, implementation, opposition, disclosure, or contrast relation.

## Per-Event Role Tests

For each event `E`, ask all six questions against the frozen predicate of `E`:

- `who`: minimal actors, targets, affected parties, challengers, monitors, or implementers.
- `what`: compact central action or state plus its required object or result.
- `when`: the time, deadline, or as-of time belonging to `E`.
- `where`: the physical or institutional setting, platform, affected area, or deployment site of `E`.
- `why`: a cause, motivation, purpose, justification, enabling condition, challenge, or risk that explains `E`.
- `how`: a means, manner, instrument, mechanism, procedure, ordered step, or implementation that realizes `E`.

For WHY and HOW, compare candidate proposition `C` with event proposition `E`:

```text
C causes, motivates, justifies, enables, or gives the purpose of E -> why
C is the means, manner, mechanism, procedure, or implementation of E -> how
E produces C as a result                                            -> neither
C only shares the topic                                             -> reject
```

Use semantic direction, not cue words. An unmarked relation may be retained as `implicit` when local discourse strongly supports it. Never infer it from world knowledge.

## Candidate Policy

Caps apply per event and are maxima, not slots:

```text
who:   typical 1-3, hard maximum 5
what:  typical 1,   hard maximum 2
when:  hard maximum 1
where: hard maximum 1
why:   typical 0-1, hard maximum 2
how:   typical 0-1, hard maximum 2
total: usually 2-6, hard maximum 12
```

Deduplicate record-local nodes by `Node_Type + normalized referent/text`. Collapse aliases, titles, pronouns, and repeated mentions that denote one participant. Reject clause-length WHO nodes.

## Output Contract

Use `schema_version: "ceh-cluster-v3"` by default:

```json
{
  "schema_version": "ceh-cluster-v3",
  "records": [
    {
      "Id": "R1",
      "Text": "source text",
      "Sentences": [],
      "Nodes": [],
      "Event_Clusters": [
        {
          "Cluster_Id": "EC1",
          "Topic": "coherent event-chain topic",
          "Central_Event": "E1",
          "Events": [],
          "Relations": []
        }
      ],
      "Cross_Cluster_Relations": [],
      "Review": {
        "Mode": "independent_agent",
        "Status": "passed",
        "Reviewer": "semantic_critic",
        "Issues_Found": [],
        "Changes_Made": []
      }
    }
  ]
}
```

Every sentence and node uses half-open record offsets:

```text
Text[Tag_Start:Tag_End] == Tag_Text
```

Use `Evidence_Status: explicit|implicit|converted`. Add `Reliability_Label` only when requested.

Detailed fields and a complete example are in `references/schema.md`.

## Mandatory Review Gate

The extractor's first output is never final.

When sub-agents are available:

1. Give a fresh critic Agent only the raw record, candidate JSON, schema, and review checklist.
2. Ask it to audit cluster boundaries, event duplication, central-event choice, per-event role attachment, WHY/HOW direction, node boundaries, offsets, and relation evidence.
3. Apply supported corrections.
4. Re-run the critic when it found a major cluster or event error.
5. Record the result in `Review` with `Mode: "independent_agent"`.

When sub-agents are unavailable, run a separated self-critic pass and set:

```json
{"Mode": "self_critic_fallback", "Status": "needs_human_review"}
```

Never describe fallback self-review as an independent Agent review.

## Validation

After semantic review, run:

```text
python scripts/validate_ceh_cluster_output.py output.json
python scripts/validate_ceh_cluster_semantic_output.py output.json --report risk-report.json
```

The second script is a deterministic risk linter. It cannot certify event meaning, causality, or method.

For batch work:

- send one record per extraction call;
- run one critic review per record;
- retry only the failed record;
- reset extraction context after at most 100 completed records;
- keep unresolved records in a review queue.

## Compatibility Modes

- `root_only=true`: emit the previous `ceh-record-v2` one-root-event view.
- `global_index=true`: project validated v3 records into the legacy global `ceh-5w1h-v1` index.
- `full_detail=true`: allow more supporting events, while keeping separate 5W1H hyperedges.
- `stability=true`: compare independent extraction passes before critic review.
- `reliability=true`: add reliability labels without changing role selection.

## Non-Negotiables

- Do not skip cluster discovery and jump directly to one global 5W1H frame.
- Do not create one cluster or event per sentence mechanically.
- Do not attach 5W1H nodes directly to a cluster; attach them to a specific event hyperedge.
- Do not let two events represent the same proposition with different wording.
- Do not use one event's WHY, HOW, WHEN, or WHERE for another event.
- Do not emit a WHO span containing an event predicate.
- Do not turn every country, organization, quantity, weapon, or repeated alias into a node.
- Do not assign WHY or HOW from lexical markers.
- Do not invent missing roles or event relations from world knowledge.
- Do not call output final before independent semantic review and deterministic validation.
