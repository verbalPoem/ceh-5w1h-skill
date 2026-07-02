# CEH-5W1H Finite-State Controller

Use this controller for multi-event text.

```text
S0_SEGMENT
  -> S1_EVENT_CANDIDATES
  -> S2_NODE_SPAN_CANDIDATES
  -> S3_CLUSTER_GROUP
  -> S4_ROOT_SELECT
  -> S5_COARSE_SKELETON
  -> S6_ROLE_5W1H
  -> S7_RELATION_LINK
  -> S8_STABILITY_VALIDATE
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

## S2_NODE_SPAN_CANDIDATES

Collect possible nodes before final event formation:

- actors, sources, organizations, countries, persons
- systems, weapons, platforms, projects, policies
- time expressions and as-of dates
- places, regions, bases, vessels, theaters
- causes, risks, motivations, purposes
- methods, mechanisms, capabilities, procedures

Keep exact spans and tentative offsets. Do not output these yet; use them as candidates for event hyperedges.

## S3_CLUSTER_GROUP

Group candidates into `event_clusters`.

Cluster events when they share:

- same report or source disclosure
- same policy/security issue
- same weapon system/project
- same exhibition/test/construction story
- same accident/incident chain

Do not merge independent news briefs merely because they share a broad domain such as "military".

## S4_ROOT_SELECT

Pick one root event per cluster:

```text
root_score =
  source_position
  + predicate_salience
  + relation_degree
  + evidence_density
  + cluster_explanation_power
  - side_detail_penalty
```

The root event should be the easiest entry point for a reader.

## S5_COARSE_SKELETON

Build a coarse skeleton before 5W1H:

```text
who/source -> predicate/action/state -> what/object/result
```

Then attach candidate qualifiers:

- time or validity period
- place or affected area
- cause, purpose, concern, or motivation
- method, mechanism, platform, or capability
- quantity or status when it describes the event

Reject a candidate event if no clear predicate/action/state can be identified.

## S6_ROLE_5W1H

For each accepted event, create one `event_hyperedge` that connects the event to its 5W1H nodes.

Do not attach 5W1H nodes directly to a cluster.

Ask role questions event by event:

- who: actor, source, owner, participant, affected party
- what: action, state, claim, system, object, result
- when: event time, report time, as-of time, deadline, plan time
- where: location, affected area, platform, base, facility
- why: cause, purpose, risk, motivation, concern
- how: method, mechanism, capability, procedure, platform

## S7_RELATION_LINK

Add `relation_hyperedges` between events only when useful.

Prefer these patterns:

- disclosure event -> status events: `discloses`
- concern or threat -> action: `motivates`
- background plan -> assessment: `background_of`
- system component -> larger inventory/project: `component_of`
- capability/configuration -> operational advantage: `supports` or `enables`

## S8_STABILITY_VALIDATE

Check:

- every cluster has a `root_event`
- every cluster event exists in `events`
- every event references an event hyperedge
- every event hyperedge references existing nodes
- every relation hyperedge references existing events
- relation names come from the controlled vocabulary
- no global flat 5W1H table is produced

For high-confidence mode, compare independent passes:

- stable: same event meaning and role assignment repeats
- unstable: same approximate event but role, boundary, or relation changes
- missed: central evidence-backed event absent from a pass

Prefer stable root events. Review unstable and missed events before adding them.
