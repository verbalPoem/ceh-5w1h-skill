# Diagram Guide

Use Mermaid when the user asks to draw or explain the graph.

## Compact Cluster Diagram

```mermaid
flowchart LR
  EC1["EC1: cluster topic"]
  E1["E1: root event"]
  E2["E2: related event"]
  E3["E3: related event"]

  EC1 --> E1
  EC1 --> E2
  EC1 --> E3

  E1 -- "discloses" --> E2
  E2 -- "motivates" --> E3

  E1 --> W1["who: ..."]
  E1 --> T1["what: ..."]
  E1 --> D1["when: ..."]
```

## Diagram Rules

- Show `EC*` clusters.
- Show `E*` events.
- Show relation labels on event-to-event edges.
- Show only the root event's key 5W1H nodes unless full detail is requested.
- Keep labels short.
- Use controlled relation names.
