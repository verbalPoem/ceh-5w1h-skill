# 安装教程

语言：中文 | [English](INSTALL.en.md)

## 手动安装

1. 下载或 clone 本仓库。
2. 找到仓库中的 `ceh-5w1h/` 文件夹。
3. 将该文件夹复制到 Codex 的 skills 目录。

Windows PowerShell：

```powershell
Copy-Item -Recurse .\ceh-5w1h "$env:USERPROFILE\.codex\skills\"
```

macOS / Linux：

```bash
cp -R ./ceh-5w1h ~/.codex/skills/
```

4. 新开一个 Codex 线程。
5. 输入：

```text
$ceh-5w1h 把下面文本抽成事件簇 5W1H 知识超图：
...
```

## 检查安装是否成功

安装后，目标路径应类似：

Windows：

```text
C:\Users\你的用户名\.codex\skills\ceh-5w1h\SKILL.md
```

macOS / Linux：

```text
~/.codex/skills/ceh-5w1h/SKILL.md
```

如果新线程里能识别 `$ceh-5w1h`，说明安装成功。

## 验证输出格式

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

期望结果：

```text
VALID: 1 cluster(s), 2 event(s), 2 event hyperedge(s), 1 relation hyperedge(s)
```
