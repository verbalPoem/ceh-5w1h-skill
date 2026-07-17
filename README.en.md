# CEH-5W1H Skill

Language: [中文](README.md) | English

`ceh-5w1h` is a Codex skill for cluster-first 5W1H extraction and event-hypergraph construction. The default mode is **Cluster-first + Per-event 5W1H + Independent Critic Agent**: discover event clusters, retain one central event and a small number of relation-critical supporting events, build a separate 5W1H hyperedge for each event, and require an independent semantic review.

```text
Text -> Event_Clusters -> Events -> 5W1H Nodes -> Hyperedges/Relations -> Critic Agent -> Validation
```

## What's New in v3

- Restores and strengthens the cluster-first pipeline: discover clusters, select events, then extract 5W1H per event without collapsing a document into one frame or generating sliding-window event explosions.
- Uses record-local `S* / N* / EC* / E* / HE*` identifiers so source evidence, nodes, events, and hyperedges remain directly traceable.
- Gives every event its own 5W1H roles, `Missing` list, and hyperedge. Roles cannot be borrowed across events, while genuinely shared entities reuse one node.
- Adds an independent Critic Agent protocol, structural validator, and semantic risk linter for clause-length WHO spans, duplicate events, role attachment, and WHY/HOW direction.
- Processes batches as stateless one-record calls with immediate validation and targeted retries, supported by Chinese cases and cross-lingual gold calibration.

## Default Output: ceh-cluster-v3

```json
{
  "schema_version": "ceh-cluster-v3",
  "records": [
    {
      "Id": "R1",
      "Text": "Court ordered Japan to stop whaling.",
      "Sentences": [
        {
          "Sentence_Id": "S1",
          "Tag_Text": "Court ordered Japan to stop whaling.",
          "Tag_Start": 0,
          "Tag_End": 36
        }
      ],
      "Nodes": [
        {
          "Node_Id": "N1",
          "Node_Type": "who",
          "Tag_Text": "Court",
          "Tag_Start": 0,
          "Tag_End": 5,
          "Evidence_Status": "explicit"
        },
        {
          "Node_Id": "N2",
          "Node_Type": "what",
          "Tag_Text": "Japan to stop whaling",
          "Tag_Start": 14,
          "Tag_End": 35,
          "Evidence_Status": "explicit"
        }
      ],
      "Event_Clusters": [
        {
          "Cluster_Id": "EC1",
          "Topic": "Court order stopping Japanese whaling",
          "Central_Event": "E1",
          "Events": [
            {
              "Event_Id": "E1",
              "Event_Level": "central",
              "Event_Text": "Court ordered Japan to stop whaling",
              "Trigger": {
                "Tag_Text": "ordered",
                "Tag_Start": 6,
                "Tag_End": 13
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
          "Relations": []
        }
      ],
      "Cross_Cluster_Relations": [],
      "Review": {
        "Mode": "independent_agent",
        "Status": "passed",
        "Reviewer": "semantic_critic",
        "Issues_Found": [],
        "Changes_Made": []
      }
    }
  ]
}
```

Default constraints:

- Discover clusters first, then accepted events, then per-event 5W1H. Do not skip cluster discovery for one global frame.
- Every cluster has exactly one central event and normally zero to two relation-critical supporting events; five is the hard maximum.
- Each event has its own frozen predicate, `Missing`, and event hyperedge. Roles cannot be borrowed across events.
- `S*` evidence and `N*` nodes are record-local and auditable, rather than one giant global index.
- Keep the best answer per role by default. Two to six nodes per event is typical, and 12 is only a hard ceiling.
- WHO is usually one to three minimal entity phrases; keep indispensable participants but collapse coreferent names, titles, abbreviations, and pronouns.
- WHY/HOW does not depend on cue words: a cue is not sufficient, and an unmarked relation may still be explicit or strongly implied by discourse.
- `Tag_Text` must equal `Text[Tag_Start:Tag_End]`.
- No duplicate `Node_Type + Tag_Text` within one record; shared entities reuse one `N*` node.
- Prefer `Missing` over a low-confidence guess.
- `Evidence_Status` records explicit or implicit support. Add the independent `Reliability_Label` only when reliability is requested.
- A fresh Critic Agent must review the draft. Without sub-agents, output remains `self_critic_fallback + needs_human_review`.
- The old one-root `ceh-record-v2` view requires `root_only=true`; the global index requires `global_index=true`.

## Repository Layout

```text
.
|-- ceh-5w1h/                 # installable Codex skill
|   |-- SKILL.md
|   |-- agents/
|   |-- references/
|   |   |-- schema.md
|   |   |-- cluster-policy.md
|   |   |-- state-machine.md
|   |   |-- reviewer-protocol.md
|   |   |-- role-coverage.md
|   |   |-- deduplication.md
|   |   |-- semantic-role-reasoning.md
|   |   |-- cross-lingual-calibration.md
|   |   |-- chinese-calibration-cases.md
|   |   |-- reliability.md
|   |   |-- gold-calibration.md
|   |   `-- ...
|   `-- scripts/
|       |-- validate_ceh_cluster_output.py
|       |-- validate_ceh_cluster_semantic_output.py
|       |-- validate_ceh_record_output.py
|       |-- validate_ceh_semantic_output.py
|       |-- prepare_ceh_batch_jobs.py
|       |-- analyze_5w1h_jsonl.py
|       |-- migrate_ceh_evidence_fields.py
|       |-- convert_ceh_global_to_record_view.py
|       |-- validate_ceh_output.py
|       `-- compare_ceh_outputs.py
|-- examples/
|   |-- ceh-cluster-v3-output.json
|   |-- ceh-cluster-v3-risk-report.json
|   |-- ceh-record-v2-output.json
|   |-- ceh-whaling-output.json
|   |-- ceh-semantic-regression-output.json
|   |-- ceh-semantic-implicit-output.json
|   |-- ceh-chinese-calibration-output.json
|   `-- ceh-minimal-output.json
|-- docs/
|   `-- flares-calibration-summary.json
|-- prompts/
|-- README.md
|-- README.en.md
`-- LICENSE
```

The installable skill is the `ceh-5w1h/` folder.

## Quick Install

Windows PowerShell:

```powershell
Copy-Item -Recurse .\ceh-5w1h "$env:USERPROFILE\.codex\skills\"
```

macOS / Linux:

```bash
cp -R ./ceh-5w1h ~/.codex/skills/
```

Then start a new Codex thread:

```text
$ceh-5w1h Discover event clusters first, extract a separate 5W1H hyperedge for every retained event, and run an independent Critic Agent:
...
```

For detailed installation instructions, see [docs/INSTALL.en.md](docs/INSTALL.en.md).

## Validate Output

Run cluster/event semantic review, an independent Critic Agent, structural validation, and deterministic risk linting:

```bash
python ceh-5w1h/scripts/validate_ceh_cluster_output.py examples/ceh-cluster-v3-output.json
python ceh-5w1h/scripts/validate_ceh_cluster_semantic_output.py examples/ceh-cluster-v3-output.json --report risk-report.json
```

The independent critic checks cluster boundaries, duplicate events, central-event choice, per-event role attachment, and WHY/HOW direction. Python only checks known structural and boundary risks. `LINT_CLEAR` is not proof of semantic correctness or accuracy.

Prepare line-based batch jobs with one stateless model call per record and a context reset after at most 100 records:

```bash
python ceh-5w1h/scripts/prepare_ceh_batch_jobs.py input.txt jobs --records-per-session 100
```

Never place 100 or 300 source records in one extraction prompt. Validate immediately and retry only failed records.

Convert legacy global CEH JSON into an auditable record-first view:

```bash
python ceh-5w1h/scripts/convert_ceh_global_to_record_view.py old_ceh.json old_ceh_record_v2.json
python ceh-5w1h/scripts/validate_ceh_record_output.py old_ceh_record_v2.json
```

Migrate legacy outputs that stored `direct/inferred/converted` in `Reliability_Label`:

```bash
python ceh-5w1h/scripts/migrate_ceh_evidence_fields.py old.json migrated.json
```

## Cross-Lingual Calibration

The local Spanish gold data contains 1,753 labeled records and 7,485 exact-span tags. WHY appears in 12.5% of records and HOW in 28.3%. These are sparsity warnings, not Chinese output quotas.

```bash
python ceh-5w1h/scripts/analyze_5w1h_jsonl.py train.json trial.json --report calibration.json
```

The skill transfers language-independent principles such as root-predicate attachment, exact spans, participant functions, and per-tag reliability. It does not turn Spanish prepositions, word order, or repeated-mention rules into Chinese regexes.

The complete audit snapshot is stored at [docs/flares-calibration-summary.json](docs/flares-calibration-summary.json).

The old global-index schema can still be validated:

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

## Use Cases

- center-event 5W1H extraction for Chinese or multilingual news;
- event-hyperedge construction for knowledge hypergraphs;
- converting noisy global node indexes into auditable record-first annotation views;
- reducing duplicate tags, generic-word tags, and sliding-window event explosions while preserving directly connected participants;
- rejecting clause-length WHO spans, attribution-shell roots, and keyword-only WHY/HOW assignments;
- skill-guided extraction baselines for papers or experiments.

Method calibration uses the public [Giveme5W1H](https://github.com/fhamborg/Giveme5W1H) gold data and main-event candidate-selection principles, the 2025 [5W1H prompt strategies](https://github.com/cmunhozc/5W1H-prompt-strategies) work on extractive and question-level reasoning, and local FLARES Spanish span and missingness statistics. The skill adapts these ideas for Chinese event hypergraphs rather than copying English or Spanish rules.

## License

MIT License. See [LICENSE](LICENSE).
