# CEH-5W1H Cluster-First Schema

## Contents

- Default `ceh-cluster-v3` record
- Sentences and record-local nodes
- Event clusters, events, and hyperedges
- Event relations and review metadata
- Compatibility formats

Use `ceh-cluster-v3` by default. It keeps the source text, `S*` evidence, `N*` nodes, clusters, events, hyperedges, and review result inside one record.

## Complete Shape

```json
{
  "schema_version": "ceh-cluster-v3",
  "records": [
    {
      "Id": "R1",
      "Text": "source text",
      "Sentences": [
        {
          "Sentence_Id": "S1",
          "Tag_Text": "exact source sentence",
          "Tag_Start": 0,
          "Tag_End": 21
        }
      ],
      "Nodes": [
        {
          "Node_Id": "N1",
          "Node_Type": "who",
          "Tag_Text": "exact source span",
          "Tag_Start": 0,
          "Tag_End": 2,
          "Evidence_Status": "explicit"
        }
      ],
      "Event_Clusters": [
        {
          "Cluster_Id": "EC1",
          "Topic": "one coherent topic or event chain",
          "Central_Event": "E1",
          "Events": [
            {
              "Event_Id": "E1",
              "Event_Level": "central",
              "Event_Text": "concise factual event summary",
              "Trigger": {
                "Tag_Text": "exact predicate span",
                "Tag_Start": 3,
                "Tag_End": 5
              },
              "Evidence": ["S1"],
              "Missing": ["when", "where", "why", "how"],
              "Event_Hyperedge": {
                "Hyperedge_Id": "HE1",
                "Event": "E1",
                "Nodes": {
                  "who": ["N1"],
                  "what": ["N2"],
                  "when": [],
                  "where": [],
                  "why": [],
                  "how": []
                }
              }
            }
          ],
          "Relations": [
            {
              "Relation_Id": "R1",
              "Source_Event": "E2",
              "Relation": "supports",
              "Target_Event": "E1",
              "Evidence": ["S2"]
            }
          ]
        }
      ],
      "Cross_Cluster_Relations": [
        {
          "Relation_Id": "CR1",
          "Source_Cluster": "EC2",
          "Relation": "background_of",
          "Target_Cluster": "EC1",
          "Evidence": ["S5"]
        }
      ],
      "Review": {
        "Mode": "independent_agent",
        "Status": "revised",
        "Reviewer": "semantic_critic",
        "Issues_Found": [
          {
            "Code": "ROLE_ATTACHMENT",
            "Event_Id": "E2",
            "Message": "A HOW candidate belonged to E3."
          }
        ],
        "Changes_Made": [
          "Removed the HOW node from E2."
        ]
      }
    }
  ]
}
```

The abbreviated example references `N2`; every real output must define all referenced nodes.

## Record Fields

- `Id`: preserve the source identifier when available.
- `Text`: preserve the exact source string.
- `Sentences`: exact-offset evidence units `S1...Sn`. These may be sentences, a headline, or a semantically complete clause when punctuation is missing.
- `Nodes`: record-local, deduplicated 5W1H nodes `N1...Nn`.
- `Event_Clusters`: cluster-first extraction result.
- `Cross_Cluster_Relations`: optional evidence-backed links between clusters; use an empty array when none are needed.
- `Review`: mandatory publication-gate result.

## Sentence Fields

```json
{
  "Sentence_Id": "S1",
  "Tag_Text": "exact source evidence unit",
  "Tag_Start": 0,
  "Tag_End": 10
}
```

Require:

```text
Text[Tag_Start:Tag_End] == Tag_Text
```

Sentence IDs are record-local. Do not create multiple `S*` entries for overlapping sliding windows.

## Node Fields

```json
{
  "Node_Id": "N1",
  "Node_Type": "who|what|when|where|why|how",
  "Tag_Text": "exact source span",
  "Tag_Start": 0,
  "Tag_End": 10,
  "Evidence_Status": "explicit|implicit|converted"
}
```

Optional when requested:

```json
{"Reliability_Label": "reliable|partially_reliable|unreliable"}
```

Rules:

- Require exact half-open offsets.
- Deduplicate inside one record by `Node_Type + normalized referent/text`.
- Reuse one node ID across event hyperedges when the same node answers the same role for multiple events.
- A reused node is evidenced when either its canonical offset or the same exact `Tag_Text` appears in one of that event's `S*` units. Do not add an unrelated sentence merely to cover the canonical offset.
- Use separate node IDs when one source span legitimately has different roles in different events.
- Prefer a canonical explicit mention over pronouns and aliases.
- A node is an answer span, not a whole evidence sentence by default.

## Cluster Fields

- `Cluster_Id`: record-local `EC*` ID.
- `Topic`: concise topic or causal/implementation chain shared by the cluster.
- `Central_Event`: ID of exactly one event in `Events`.
- `Events`: accepted events with distinct predicates.
- `Relations`: directed links among events in the same cluster.

A cluster is not a paragraph bucket. Its events must be mutually coherent and connected by a useful event relation or a shared central event.

## Event Fields

- `Event_Id`: record-local `E*` ID, unique across all clusters in the record.
- `Event_Level`: `central` or `supporting`.
- `Event_Text`: concise factual summary; it may be abstractive.
- `Trigger`: exact source predicate span.
- `Evidence`: one or more `S*` IDs.
- `Missing`: lowercase roles with no accepted node for this event.
- `Event_Hyperedge`: one n-ary link from the event to its 5W1H node IDs.

Exactly one event in each cluster must be `central`, and its ID must equal `Central_Event`.

## Event Hyperedge

```json
{
  "Hyperedge_Id": "HE1",
  "Event": "E1",
  "Nodes": {
    "who": ["N1"],
    "what": ["N2"],
    "when": [],
    "where": [],
    "why": [],
    "how": []
  }
}
```

Each referenced node must exist and its `Node_Type` must match the containing role key.

Caps apply per event:

```text
who <= 5
what <= 2
when <= 1
where <= 1
why <= 2
how <= 2
total <= 12
```

## Relations

Use only the controlled vocabulary:

```text
discloses
supports
motivates
causes
part_of
component_of
background_of
enables
contrasts_with
```

Every relation must:

- be directed;
- reference existing events or clusters in the same record;
- use at least one `S*` evidence ID;
- express more than topic similarity.

Do not connect every event pair.

## Review

```json
{
  "Mode": "independent_agent|self_critic_fallback",
  "Status": "passed|revised|needs_human_review",
  "Reviewer": "reviewer identifier",
  "Issues_Found": [],
  "Changes_Made": []
}
```

- `independent_agent`: a fresh Agent reviewed the candidate without inheriting the extractor's hidden reasoning.
- `self_critic_fallback`: no independent Agent was available.
- A fallback review must use `needs_human_review`; it cannot claim `passed`.
- `revised` means the critic found issues and accepted corrections were applied.

## Compatibility

- Use `ceh-record-v2` only for `root_only=true`.
- Use `ceh-5w1h-v1` only for `global_index=true` or graph-database export.
- Never regenerate a giant global node index merely to review one record.
