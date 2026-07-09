# CEH-5W1H Schema

Use `ceh-record-v2` by default.

The older `ceh-5w1h-v1` global-index schema is optional. Use it only when the user explicitly asks for `global_index=true`, graph database import, or full event-to-event hypergraph indexing.

## Default Schema: ceh-record-v2

```json
{
  "schema_version": "ceh-record-v2",
  "records": [
    {
      "Id": "sample id",
      "Text": "source text",
      "Root_Event": {
        "Event_Id": "E1",
        "Event_Text": "one concise center event",
        "Trigger": {
          "Tag_Text": "trigger",
          "Tag_Start": 0,
          "Tag_End": 0
        }
      },
      "Tags": [
        {
          "Tag_Text": "source span",
          "Tag_Start": 0,
          "Tag_End": 0,
          "5W1H_Label": "WHO",
          "Reliability_Label": "direct"
        }
      ],
      "Missing": ["WHY"],
      "Event_Hyperedge": {
        "event": "E1",
        "who": [0],
        "what": [],
        "when": [],
        "where": [],
        "why": [],
        "how": []
      }
    }
  ]
}
```

## Record Fields

- `Id`: source sample id. Keep original dataset id when available.
- `Text`: exact source text for this record. Do not merge unrelated samples.
- `Root_Event`: the single center event for this record.
- `Tags`: FLARES-style 5W1H spans beside the same source text.
- `Missing`: uppercase labels with no evidence-backed tag.
- `Event_Hyperedge`: connects the root event to tag indexes in `Tags`.

## Tag Fields

Each tag must be auditable:

```json
{
  "Tag_Text": "source span",
  "Tag_Start": 0,
  "Tag_End": 0,
  "5W1H_Label": "WHO|WHAT|WHEN|WHERE|WHY|HOW",
  "Reliability_Label": "direct|inferred|converted"
}
```

Rules:

- `Text[Tag_Start:Tag_End]` must equal `Tag_Text`.
- Use uppercase 5W1H labels.
- Use `direct` for explicitly stated spans.
- Use `converted` only when converting legacy CEH output.
- Do not include duplicate `5W1H_Label + normalize(Tag_Text)` pairs in one record.

## Default Caps

Default extraction is compact but participant-complete:

```text
WHO <= 5
WHAT <= 2
WHEN <= 1
WHERE <= 1
WHY <= 2
HOW <= 2
TOTAL TAGS <= 12
ROOT EVENTS = 1
```

Only exceed these caps when the user explicitly asks for `full_detail=true`.

## Hyperedge Indexes

`Event_Hyperedge` stores zero-based indexes into `Tags`.

Example:

```json
{
  "event": "E1",
  "who": [0],
  "what": [1],
  "when": [2],
  "where": [],
  "why": [],
  "how": []
}
```

The tag at each listed index must have the matching 5W1H label.

## Optional Legacy Schema: ceh-5w1h-v1

Use the older global-index schema only when requested:

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

When using the legacy schema, still apply record-level deduplication before creating global `nodes`.
