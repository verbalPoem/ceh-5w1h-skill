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
$ceh-5w1h 请按 ceh-record-v2 抽取下面文本的中心事件与 5W1H tags：
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

如果新开的 Codex 线程能识别 `$ceh-5w1h`，说明安装成功。

## 校验新版输出

```bash
python ceh-5w1h/scripts/validate_ceh_record_output.py examples/ceh-record-v2-output.json
```

期望输出：

```text
VALID: 1 record(s), 4 tag(s)
```

## 转换旧结果

如果你手里已有旧版 `ceh-5w1h-v1` 全局 JSON，可以先转成 record-first 视图，方便人工审阅：

```bash
python ceh-5w1h/scripts/convert_ceh_global_to_record_view.py old_ceh.json old_ceh_record_v2.json
python ceh-5w1h/scripts/validate_ceh_record_output.py old_ceh_record_v2.json
```

转换器不会重做语义标注，它主要解决旧结果里“原文和标签分离、节点重复爆炸、人工难比对”的结构问题。

## 旧版校验

仅当你明确使用旧版全局索引时运行：

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```
