# CEH-5W1H Skill

Language: [中文](README.md) | English

`ceh-5w1h` is a Codex skill for event-centered 5W1H extraction and knowledge-hypergraph construction. The default mode is now **Record-first + Root event only**: each source text is kept beside its root event, 5W1H tags, and event hyperedge, so outputs are easy to audit and do not explode into a huge global `nodes/events` index.

```text
Record Text -> Root_Event -> Tags(WHO/WHAT/WHEN/WHERE/WHY/HOW) -> Event_Hyperedge
```

## Default Output: ceh-record-v2

```json
{
  "schema_version": "ceh-record-v2",
  "records": [
    {
      "Id": "sample id",
      "Text": "source text",
      "Root_Event": {
        "Event_Id": "E1",
        "Event_Text": "center event summary",
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

Default constraints:

- One `Root_Event` per `Text`.
- At most 12 tags per record: `WHO <= 5`, `WHAT <= 2`, `WHEN/WHERE <= 1`, and `WHY/HOW <= 2`.
- `Tag_Text` must equal `Text[Tag_Start:Tag_End]`.
- No duplicate `5W1H_Label + Tag_Text` within the same record.
- The old `ceh-5w1h-v1` global-index schema is optional and should be used only with `global_index=true`.

## Repository Layout

```text
.
|-- ceh-5w1h/                 # installable Codex skill
|   |-- SKILL.md
|   |-- agents/
|   |-- references/
|   |   |-- schema.md
|   |   |-- state-machine.md
|   |   |-- role-coverage.md
|   |   |-- deduplication.md
|   |   `-- ...
|   `-- scripts/
|       |-- validate_ceh_record_output.py
|       |-- convert_ceh_global_to_record_view.py
|       |-- validate_ceh_output.py
|       `-- compare_ceh_outputs.py
|-- examples/
|   |-- ceh-record-v2-output.json
|   |-- ceh-whaling-output.json
|   `-- ceh-minimal-output.json
|-- docs/
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
$ceh-5w1h Extract the root event and 5W1H tags from the following text using ceh-record-v2:
...
```

For detailed installation instructions, see [docs/INSTALL.en.md](docs/INSTALL.en.md).

## Validate Output

Validate record-first output:

```bash
python ceh-5w1h/scripts/validate_ceh_record_output.py examples/ceh-record-v2-output.json
python ceh-5w1h/scripts/validate_ceh_record_output.py examples/ceh-whaling-output.json
```

Expected:

```text
VALID: 1 record(s), 4 tag(s)
```

Convert legacy global CEH JSON into an auditable record-first view:

```bash
python ceh-5w1h/scripts/convert_ceh_global_to_record_view.py old_ceh.json old_ceh_record_v2.json
python ceh-5w1h/scripts/validate_ceh_record_output.py old_ceh_record_v2.json
```

The old global-index schema can still be validated:

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

## Use Cases

- center-event 5W1H extraction for Chinese or multilingual news;
- event-hyperedge construction for knowledge hypergraphs;
- converting noisy global node indexes into auditable record-first annotation views;
- reducing duplicate tags, generic-word tags, and sliding-window event explosions while preserving directly connected participants;
- skill-guided extraction baselines for papers or experiments.

## License

MIT License. See [LICENSE](LICENSE).
