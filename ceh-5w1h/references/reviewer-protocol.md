# Independent Reviewer Protocol

## Purpose

Use a fresh semantic critic after extraction. The critic is a release gate, not another unconstrained extractor.

## Independence

Give the critic:

- the raw record;
- the candidate `ceh-cluster-v3` JSON;
- schema and review checklists.

Do not give it:

- hidden chain-of-thought;
- the extractor's confidence narrative;
- a gold answer;
- suspected errors or intended fixes, unless testing a specific known regression.

When no sub-agent tool exists, run a separated self-critic pass and mark `Mode: self_critic_fallback`. A fallback review cannot produce final `passed` status.

## Review Order

The critic audits in this order:

1. record and evidence-unit integrity;
2. cluster boundaries;
3. event admission, merging, and central-event choice;
4. event-to-event relation direction and evidence;
5. per-event 5W1H attachment;
6. node span minimality and alias deduplication;
7. WHY/HOW semantic direction;
8. offsets, IDs, caps, and `Missing`.

Do not review role details before deciding whether the event decomposition is valid.

## Required Checks

### Clusters

- Are unrelated briefs separated?
- Are events grouped by a real source-supported chain rather than shared entities?
- Is any cluster only a paragraph bucket?
- Are two clusters actually one coherent chain?

### Events

- Does every event have a distinct predicate and useful fact?
- Are numerical details or paraphrases incorrectly promoted?
- Are duplicate events using different wording?
- Does every supporting event have a controlled relation to the central event?
- Is the selected central event the best organizer of the cluster?

### 5W1H

- Does each node answer its role for this exact event?
- Is every WHO a minimal entity, not a clause?
- Does WHAT contain the event predicate and necessary object/result?
- Do WHEN and WHERE belong to this event?
- Does WHY explain the event with direction `C -> E`?
- Does HOW realize the event with direction `C -> E`?
- Does any node actually belong to a neighboring event?

### Graph Integrity

- Are aliases collapsed into one record-local node?
- Are shared nodes reused where role and referent match?
- Do hyperedges reference existing nodes of the right type?
- Are event relations supported by listed `S*` evidence?
- Do offsets reproduce exact source spans?

## Critic Output

Return only one verdict and a concise issue list:

```json
{
  "Verdict": "PASS|REVISE|NEEDS_HUMAN_REVIEW",
  "Issues": [
    {
      "Code": "CLUSTER_SPLIT|EVENT_DUPLICATE|CENTRAL_EVENT|ROLE_ATTACHMENT|WHY_HOW|SPAN|OFFSET|RELATION|MISSING|OTHER",
      "Cluster_Id": "EC1",
      "Event_Id": "E1",
      "Node_Id": "N1",
      "Message": "concise source-grounded finding",
      "Suggested_Action": "specific repair"
    }
  ]
}
```

Omit IDs that do not apply. Do not rewrite the entire annotation unless the cluster structure is invalid.

## Repair Policy

- `PASS`: set review status to `passed`.
- `REVISE`: apply source-supported fixes, record them, and set status to `revised` after required re-review.
- `NEEDS_HUMAN_REVIEW`: preserve unresolved alternatives and do not claim high confidence.

Major changes requiring another independent review:

- split or merge a cluster;
- add or remove an event;
- change the central event;
- reverse an event relation;
- move a node between events;
- reassign WHY and HOW.

Offset-only repairs may be deterministically revalidated without another semantic review.

## Anti-Agreement Guard

The critic must not approve output merely because:

- JSON is valid;
- offsets match;
- every role is filled;
- the candidate looks detailed;
- the extractor used familiar cue words.

Empty roles and fewer events are acceptable when evidence is weak.
