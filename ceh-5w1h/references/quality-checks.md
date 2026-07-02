# CEH-5W1H Quality Checks

## Top-Level Checks

- Output uses `schema_version: "ceh-5w1h-v1"`.
- Output contains `sentences`, `nodes`, `events`, `event_hyperedges`, `relation_hyperedges`, and `event_clusters`.
- IDs are compact and stable: `S*`, `N*`, `E*`, `HE*`, `RH*`, `EC*`.

## Cluster Checks

- Every `event_clusters.*.root_event` exists in `events`.
- Every listed event belongs to the same topic thread.
- A cluster is not just a paragraph wrapper; it should preserve a coherent issue or story.
- A cluster should not contain unrelated independent briefs.

## Event Checks

- Every event has a short factual summary.
- Every event has one event hyperedge.
- Do not promote every technical detail to an event.
- Mark only root or central events as `main: true`.

## 5W1H Checks

- 5W1H nodes attach to events through `event_hyperedges`.
- Every event hyperedge has exactly six node groups: `who`, `what`, `when`, `where`, `why`, `how`.
- Empty groups use `[]` and are listed in `missing`.
- Preserve source wording for weapons, dates, places, quantities, and organization names.

## Relation Checks

- Every relation hyperedge references existing source and target events.
- Relation type must be in the controlled vocabulary.
- Do not create dense all-to-all event links.
- Use `discloses`, not `reports`.
- Use `motivates` only when the source event/claim drives the target event.
- Use `causes` only when causality is explicit.

## Failure Patterns

- Flattening a whole document into one 5W1H table.
- Extracting every sentence as an independent event.
- Losing event relations and returning only isolated hyperedges.
- Attaching 5W1H nodes to clusters instead of events.
- Using unsupported relation names.
- Omitting evidence IDs.
