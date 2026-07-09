# Installation

Language: [中文](INSTALL.md) | English

## Manual Install

1. Download or clone this repository.
2. Locate the `ceh-5w1h/` folder.
3. Copy the whole `ceh-5w1h/` folder into your Codex skills directory.

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
$ceh-5w1h Extract the root event and 5W1H tags from the following text using ceh-record-v2:
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

## Validate Record-First Output

```bash
python ceh-5w1h/scripts/validate_ceh_record_output.py examples/ceh-record-v2-output.json
```

Expected:

```text
VALID: 1 record(s), 4 tag(s)
```

## Convert Legacy Output

If you already have a legacy `ceh-5w1h-v1` global JSON file, convert it into a record-first view for manual review:

```bash
python ceh-5w1h/scripts/convert_ceh_global_to_record_view.py old_ceh.json old_ceh_record_v2.json
python ceh-5w1h/scripts/validate_ceh_record_output.py old_ceh_record_v2.json
```

The converter does not redo semantic annotation. It mainly fixes the legacy structure where source text and tags were separated and repeated nodes were hard to review.

## Legacy Validation

Run this only when you explicitly use the old global-index format:

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```
