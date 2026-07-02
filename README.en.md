# CEH-5W1H Skill

Language: [中文](README.md) | English

`ceh-5w1h` is a Codex skill for extracting clustered event 5W1H knowledge hypergraphs. It does not flatten text into a global 5W1H table. Instead, it structures news, military reports, policy text, incident briefings, and technical reports as:

```text
Document -> Event Clusters -> Events -> 5W1H Event Hyperedges -> Event Relation Hyperedges
```

## Core Idea

```text
EC1 / EC2 = event clusters
E1 / E2 = events
HE1 / HE2 = event-level 5W1H hyperedges
RH1 / RH2 = event-to-event relation hyperedges
N1 / N2 = 5W1H nodes
S1 / S2 = evidence sentences
```

Default output:

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

## Relation Vocabulary

Default event relations:

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

## Repository Layout

```text
.
|-- ceh-5w1h/                 # installable Codex skill
|   |-- SKILL.md
|   |-- agents/
|   |-- references/
|   `-- scripts/
|-- examples/
|   `-- ceh-minimal-output.json
|-- docs/
|   |-- INSTALL.md
|   `-- INSTALL.en.md
|-- prompts/
|   |-- install-with-ai.zh.md
|   `-- install-with-ai.en.md
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
$ceh-5w1h extract clustered event 5W1H hypergraphs from the following text and draw a Mermaid diagram:
...
```

For detailed installation instructions, see [docs/INSTALL.en.md](docs/INSTALL.en.md).

## Validate Output

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

Expected:

```text
VALID: 1 cluster(s), 2 event(s), 2 event hyperedge(s), 1 relation hyperedge(s)
```

## License

MIT License. See [LICENSE](LICENSE).
