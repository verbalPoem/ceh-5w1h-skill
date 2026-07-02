# CEH-5W1H Finite-State Controller

Use this controller for multi-event text.

```text
S0_SEGMENT
  -> S1_EVENT_CANDIDATES
  -> S2_CLUSTER_GROUP
  -> S3_ROOT_SELECT
  -> S4_EVENT_5W1H
  -> S5_RELATION_LINK
  -> S6_VALIDATE
```

## S0_SEGMENT

Split input into topic-level blocks. Strong split signals:

- different topic or system
- different country/company/person with a new predicate
- independent news brief boundary
- sharp reset of time/place/object

Do not split by every sentence.

## S1_EVENT_CANDIDATES

Find event candidates with clear predicates or states:

- disclosure or announcement
- possession, deployment, reserve, construction, test, exhibit
- claim, concern, risk assessment, demonstration
- capability or configuration when it supports a central event

Discard attractive technical details if they do not become useful events or 5W1H nodes.

## S2_CLUSTER_GROUP

Group candidates into `event_clusters`.

Cluster events when they share:

- same report or source disclosure
- same policy/security issue
- same weapon system/project
- same exhibition/test/construction story
- same accident/incident chain

## S3_ROOT_SELECT

Pick one root event per cluster:

```text
root_score = salience + explains_cluster + relation_degree + first_sentence_weight - side_detail_penalty
```

The root event should be the easiest entry point for a reader.

## S4_EVENT_5W1H

For each accepted event, create one `event_hyperedge` that connects the event to its 5W1H nodes.

Do not attach 5W1H nodes directly to a cluster.

## S5_RELATION_LINK

Add `relation_hyperedges` between events only when useful.

Prefer these patterns:

- disclosure event -> status events: `discloses`
- concern or threat -> action: `motivates`
- background plan -> assessment: `background_of`
- system component -> larger inventory/project: `component_of`
- capability/configuration -> operational advantage: `supports` or `enables`

## S6_VALIDATE

Check:

- every cluster has a `root_event`
- every cluster event exists in `events`
- every event references an event hyperedge
- every event hyperedge references existing nodes
- every relation hyperedge references existing events
- relation names come from the controlled vocabulary
- no global flat 5W1H table is produced
