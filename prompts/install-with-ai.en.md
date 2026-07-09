# Prompt For AI-Assisted Installation

Please install the Codex skill from the current repository onto this machine.

Requirements:

1. Locate the `ceh-5w1h/` folder in the current repository.
2. Confirm that it contains `SKILL.md`.
3. Copy the whole `ceh-5w1h/` folder into the current user's Codex skills directory:
   - Windows: `%USERPROFILE%\.codex\skills\`
   - macOS/Linux: `~/.codex/skills/`
4. After copying, check that the target path contains:
   - `ceh-5w1h/SKILL.md`
   - `ceh-5w1h/references/schema.md`
   - `ceh-5w1h/references/state-machine.md`
   - `ceh-5w1h/references/deduplication.md`
   - `ceh-5w1h/scripts/validate_ceh_record_output.py`
   - `ceh-5w1h/scripts/convert_ceh_global_to_record_view.py`
5. Do not delete or overwrite any other skill.
6. If `ceh-5w1h/` already exists in the target directory, tell me before overwriting it.
7. After installation, remind me to start a new Codex thread and use:

```text
$ceh-5w1h Extract the root event and 5W1H tags from the following text using ceh-record-v2:
...
```

Please perform the installation and report the final installation path and check result.
