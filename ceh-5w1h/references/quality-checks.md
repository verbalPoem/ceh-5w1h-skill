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
- Do not promote quantities, equipment specs, or quotation fragments to events unless they express a central state, action, or claim.
- Mark only root or central events as `main: true`.
- Root events should have high cluster explanation power, not merely early position.

## 5W1H Checks

- 5W1H nodes attach to events through `event_hyperedges`.
- Every event hyperedge has exactly six node groups: `who`, `what`, `when`, `where`, `why`, `how`.
- Empty groups use `[]` and are listed in `missing`.
- Preserve source wording for weapons, dates, places, quantities, and organization names.
- Every non-empty node should answer a role question for the specific event, not for the whole document.
- Do not borrow `why` or `how` from a neighboring event unless a relation hyperedge supports the connection.

## Diagram Checks

- If a Mermaid diagram is requested, it must not replace 5W1H extraction.
- Every displayed root event must show six 5W1H roles in the diagram or in an adjacent 5W1H table.
- Use `missing` for absent roles; do not silently omit absent roles.
- Do not use generic background nodes such as `B1` as substitutes for event frames or 5W1H nodes.
- For many clusters, split diagrams into batches rather than deleting 5W1H roles.

## Relation Checks

- Every relation hyperedge references existing source and target events.
- Relation type must be in the controlled vocabulary.
- Do not create dense all-to-all event links.
- Use `discloses`, not `reports`.
- Use `motivates` only when the source event/claim drives the target event.
- Use `causes` only when causality is explicit.

## Stability Checks

- Stable items repeat across independent passes with the same meaning.
- Unstable items have shifting role boundaries, relation labels, or event granularity.
- Missed items are central evidence-backed events absent from one pass.
- Do not add side details simply because one pass extracted them.
- Use `scripts/compare_ceh_outputs.py` when comparing multiple CEH JSON files.

## Failure Patterns

- Flattening a whole document into one 5W1H table.
- Extracting every sentence as an independent event.
- Losing event relations and returning only isolated hyperedges.
- Attaching 5W1H nodes to clusters instead of events.
- Using unsupported relation names.
- Omitting evidence IDs.
- Choosing a side detail as the cluster root.
- Filling missing roles from background knowledge instead of source evidence.
- Drawing only event clusters/relations while omitting 5W1H roles.
