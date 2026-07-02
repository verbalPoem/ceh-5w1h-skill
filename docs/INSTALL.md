# 安装教程

语言：中文 | [English](INSTALL.en.md)

## 手动安装

1. 下载或 clone 本仓库。
2. 找到仓库中的 `ceh-5w1h/` 文件夹。
3. 将整个 `ceh-5w1h/` 文件夹复制到 Codex 的 skills 目录。

Windows PowerShell：

```powershell
Copy-Item -Recurse .\ceh-5w1h "$env:USERPROFILE\.codex\skills\"
```

macOS / Linux：

```bash
cp -R ./ceh-5w1h ~/.codex/skills/
```

4. 新开一个 Codex 线程。
5. 使用：

```text
$ceh-5w1h 把下面文本抽成事件簇 5W1H 知识超图：
...
```

## 检查安装

最终路径应类似：

Windows：

```text
C:\Users\YOUR_NAME\.codex\skills\ceh-5w1h\SKILL.md
```

macOS / Linux：

```text
~/.codex/skills/ceh-5w1h/SKILL.md
```

如果新开的 Codex 线程能够识别 `$ceh-5w1h`，说明安装成功。

## 验证输出

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

期望输出：

```text
VALID: 1 cluster(s), 2 event(s), 2 event hyperedge(s), 1 relation hyperedge(s)
```

## 稳定性比较

如果你让模型对同一文本抽取多次，并保存为多个 JSON 文件，可以运行：

```bash
python ceh-5w1h/scripts/compare_ceh_outputs.py pass1.json pass2.json pass3.json
```

它会列出事件、事件簇、关系、5W1H 节点中的 stable / unstable / one-pass only 项，方便做高置信抽取或论文实验。
