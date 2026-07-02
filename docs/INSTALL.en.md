# Installation

Language: [中文](INSTALL.md) | English

## Manual Install

1. Download or clone this repository.
2. Locate the `ceh-5w1h/` folder.
3. Copy it into your Codex skills directory.

Windows PowerShell:

```powershell
Copy-Item -Recurse .\ceh-5w1h "$env:USERPROFILE\.codex\skills\"
```

macOS / Linux:

```bash
cp -R ./ceh-5w1h ~/.codex/skills/
```

4. Start a new Codex thread.
5. Invoke:

```text
$ceh-5w1h extract clustered event 5W1H hypergraphs from the following text:
...
```

## Check Installation

The final path should look like:

Windows:

```text
C:\Users\YOUR_NAME\.codex\skills\ceh-5w1h\SKILL.md
```

macOS / Linux:

```text
~/.codex/skills/ceh-5w1h/SKILL.md
```

If a new Codex thread recognizes `$ceh-5w1h`, the installation is successful.

## Validate Output

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

Expected:

```text
VALID: 1 cluster(s), 2 event(s), 2 event hyperedge(s), 1 relation hyperedge(s)
```

## Compare Stability

If you extract the same text multiple times and save each pass as JSON, run:

```bash
python ceh-5w1h/scripts/compare_ceh_outputs.py pass1.json pass2.json pass3.json
```

The script lists stable, unstable, and one-pass-only events, clusters, relations, and 5W1H role nodes.
