# CEH-5W1H Schema

Use this schema by default.

```json
{
  "schema_version": "ceh-5w1h-v1",
  "sentences": {},
  "nodes": {},
  "events": {},
  "event_hyperedges": {},
  "relation_hyperedges": {},
  "event_clusters": {}
}
```

## Sentences

`sentences` stores source evidence as `S1`, `S2`, ...

```json
{
  "S1": {
    "text": "source sentence",
    "tag_start": 0,
    "tag_end": 20
  }
}
```

## Nodes

`nodes` stores 5W1H nodes as `N1`, `N2`, ...

```json
{
  "N1": {
    "node_type": "who|what|when|where|why|how",
    "text": "source span",
    "entity_type": "ORG|PERSON|COUNTRY|WEAPON|SYSTEM|PLATFORM|TIME|PLACE|CAUSE|PURPOSE|METHOD|CAPABILITY|CLAIM|QUANTITY|OTHER",
    "tag_start": 0,
    "tag_end": 0,
    "evidence": ["S1"],
    "confidence": 0.0
  }
}
```

## Events

`events` stores event frames as `E1`, `E2`, ...

```json
{
  "E1": {
    "event_type": "disclosure|inventory_status|risk_assessment|risk_demonstration|deployment_plan|exhibition|capability|construction|other",
    "summary": "one concise event sentence",
    "trigger": {
      "text": "source trigger",
      "tag_start": 0,
      "tag_end": 0
    },
    "main": true,
    "event_hyperedge": "HE1",
    "evidence": ["S1"],
    "confidence": 0.0
  }
}
```

Use `main: true` only for root or highly central events. A cluster should normally have one root event.

## Event Hyperedges

`event_hyperedges` connects one event to its 5W1H node groups.

```json
{
  "HE1": {
    "event": "E1",
    "nodes": {
      "who": ["N1"],
      "what": ["N2"],
      "when": [],
      "where": [],
      "why": [],
      "how": []
    },
    "evidence": ["S1"],
    "missing": ["where", "why", "how"],
    "confidence": 0.0
  }
}
```

## Relation Hyperedges

`relation_hyperedges` connects events to events.

```json
{
  "RH1": {
    "relation_type": "discloses|supports|motivates|causes|part_of|component_of|background_of|enables|contrasts_with",
    "source_events": ["E1"],
    "target_events": ["E2"],
    "evidence": ["S1"],
    "confidence": 0.0
  }
}
```

Use relation hyperedges only when the relation helps preserve document structure.

## Event Clusters

`event_clusters` stores topic-level groups as `EC1`, `EC2`, ...

```json
{
  "EC1": {
    "topic": "short cluster topic",
    "root_event": "E1",
    "events": ["E1", "E2", "E3"],
    "evidence": ["S1", "S2"],
    "confidence": 0.0
  }
}
```

## ID Rules

- Sentence IDs: `S1`, `S2`, ...
- Node IDs: `N1`, `N2`, ...
- Event IDs: `E1`, `E2`, ...
- Event hyperedge IDs: `HE1`, `HE2`, ...
- Relation hyperedge IDs: `RH1`, `RH2`, ...
- Event cluster IDs: `EC1`, `EC2`, ...

Use compact sequential IDs in reading order.
