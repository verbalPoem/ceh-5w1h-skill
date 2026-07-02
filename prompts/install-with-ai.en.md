# AI-Assisted Install Prompt

Please install the Codex skill in this repository on my local machine.

Requirements:

1. Locate the `ceh-5w1h/` folder in the current repository.
2. Confirm that `SKILL.md` exists inside that folder.
3. Copy the entire `ceh-5w1h/` folder into the current user's Codex skills directory:
   - Windows: `%USERPROFILE%\.codex\skills\`
   - macOS/Linux: `~/.codex/skills/`
4. After copying, check that these files exist in the target path:
   - `ceh-5w1h/SKILL.md`
   - `ceh-5w1h/references/schema.md`
   - `ceh-5w1h/scripts/validate_ceh_output.py`
5. Do not delete or overwrite any other skill.
6. If `ceh-5w1h/` already exists in the target directory, tell me before overwriting it.
7. After installation, tell me to start a new Codex thread and invoke:

```text
$ceh-5w1h extract clustered event 5W1H hypergraphs from the following text:
...
```

Please perform the installation and report the final install path and verification result.
