# 让 AI 自动安装本 Skill 的提示词

请帮我把当前仓库里的 Codex skill 安装到本机。

要求：

1. 找到当前仓库中的 `ceh-5w1h/` 文件夹。
2. 确认该文件夹中存在 `SKILL.md`。
3. 将整个 `ceh-5w1h/` 文件夹复制到当前用户的 Codex skills 目录：
   - Windows: `%USERPROFILE%\.codex\skills\`
   - macOS/Linux: `~/.codex/skills/`
4. 复制后检查目标路径中是否存在：
   - `ceh-5w1h/SKILL.md`
   - `ceh-5w1h/references/schema.md`
   - `ceh-5w1h/references/algorithm-playbook.md`
   - `ceh-5w1h/scripts/validate_ceh_output.py`
   - `ceh-5w1h/scripts/compare_ceh_outputs.py`
5. 不要删除或覆盖其他 skill。
6. 如果目标目录中已经存在 `ceh-5w1h/`，覆盖前先告诉我。
7. 安装完成后，提醒我新开一个 Codex 线程并使用：

```text
$ceh-5w1h 把下面文本抽成事件簇 5W1H 知识超图：
...
```

请执行安装，并报告最终安装路径和检查结果。
