# Diagram Guide

Use Mermaid when the user asks to draw or explain the graph.

## Non-Negotiable Diagram Contract

A CEH-5W1H diagram must still show 5W1H extraction.

For every displayed accepted event, include all six role nodes:

```text
who
what
when
where
why
how
```

If a role is not stated, show `missing`. Do not silently omit it.

When there are many clusters, use one of these layouts:

- an overview diagram plus a 5W1H table for all accepted events;
- multiple Mermaid diagrams, each covering 1-3 clusters;
- compact event-card subgraphs where each event connects to six role nodes.

Do not output only an event relation diagram. Do not use `B1`, `B2`, or other background nodes as a substitute for 5W1H nodes.

## Compact Event-Card Diagram

```mermaid
flowchart TD
  EC1["EC1: cluster topic"]
  E1["E1: central event"]

  EC1 --> E1

  E1 --> E1_WHO["who: ..."]
  E1 --> E1_WHAT["what: ..."]
  E1 --> E1_WHEN["when: ..."]
  E1 --> E1_WHERE["where: ..."]
  E1 --> E1_WHY["why: missing"]
  E1 --> E1_HOW["how: ..."]
```

## Cluster Relation Diagram With 5W1H

Use relation edges only after the relevant events' 5W1H roles are visible.

```mermaid
flowchart LR
  EC1["EC1: cluster topic"]
  E1["E1: central event"]
  E2["E2: supporting event"]

  EC1 --> E1
  EC1 --> E2
  E1 -- "background_of" --> E2

  E1 --> E1_WHO["who: ..."]
  E1 --> E1_WHAT["what: ..."]
  E1 --> E1_WHEN["when: ..."]
  E1 --> E1_WHERE["where: ..."]
  E1 --> E1_WHY["why: ..."]
  E1 --> E1_HOW["how: ..."]

  E2 --> E2_WHO["who: ..."]
  E2 --> E2_WHAT["what: ..."]
  E2 --> E2_WHEN["when: missing"]
  E2 --> E2_WHERE["where: ..."]
  E2 --> E2_WHY["why: missing"]
  E2 --> E2_HOW["how: ..."]
```

## Diagram Rules

- Show `EC*` clusters.
- Show `E*` events.
- Show all six 5W1H role nodes for every displayed accepted event.
- Show relation labels on event-to-event edges.
- Keep labels short.
- Use controlled relation names.
- Split large outputs instead of deleting 5W1H roles.
