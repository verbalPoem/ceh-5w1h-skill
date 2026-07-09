# CEH-5W1H Skill

语言：中文 | [English](README.en.md)

`ceh-5w1h` 是一个面向 Codex 的 5W1H 事件超图抽取 skill。它现在默认采用 **Record-first + Root event only**：每条原文旁边直接放中心事件、5W1H tags 和事件超边，方便人工逐条审阅，不再默认生成一个巨大的全局 `nodes/events` 索引。

```text
Record Text -> Root_Event -> Tags(WHO/WHAT/WHEN/WHERE/WHY/HOW) -> Event_Hyperedge
```

## 默认输出：ceh-record-v2

```json
{
  "schema_version": "ceh-record-v2",
  "records": [
    {
      "Id": "sample id",
      "Text": "原文",
      "Root_Event": {
        "Event_Id": "E1",
        "Event_Text": "中心事件摘要",
        "Trigger": {
          "Tag_Text": "触发词",
          "Tag_Start": 0,
          "Tag_End": 0
        }
      },
      "Tags": [
        {
          "Tag_Text": "原文片段",
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

默认约束：

- 每条 `Text` 只抽一个 `Root_Event`。
- 每条记录最多 12 个 tags：`WHO <= 5`、`WHAT <= 2`、`WHEN/WHERE <= 1`、`WHY/HOW <= 2`。
- `Tag_Text` 必须等于 `Text[Tag_Start:Tag_End]`。
- 同一 record 内不得重复输出 `5W1H_Label + Tag_Text`。
- 旧版 `ceh-5w1h-v1` 全局索引只在明确要求 `global_index=true` 时使用。

## 仓库结构

```text
.
|-- ceh-5w1h/                 # 可安装的 Codex skill
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

真正需要安装的是 `ceh-5w1h/` 文件夹。

## 快速安装

Windows PowerShell：

```powershell
Copy-Item -Recurse .\ceh-5w1h "$env:USERPROFILE\.codex\skills\"
```

macOS / Linux：

```bash
cp -R ./ceh-5w1h ~/.codex/skills/
```

然后新开一个 Codex 线程：

```text
$ceh-5w1h 请按 ceh-record-v2 抽取下面文本的中心事件与 5W1H tags：
...
```

更详细的安装说明见：[docs/INSTALL.md](docs/INSTALL.md)

## 校验输出

校验新版 record-first 输出：

```bash
python ceh-5w1h/scripts/validate_ceh_record_output.py examples/ceh-record-v2-output.json
python ceh-5w1h/scripts/validate_ceh_record_output.py examples/ceh-whaling-output.json
```

期望输出：

```text
VALID: 1 record(s), 4 tag(s)
```

把旧的全局 CEH JSON 转成便于人工审阅的 record-first 视图：

```bash
python ceh-5w1h/scripts/convert_ceh_global_to_record_view.py old_ceh.json old_ceh_record_v2.json
python ceh-5w1h/scripts/validate_ceh_record_output.py old_ceh_record_v2.json
```

旧版全局索引仍可校验：

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

## 方法定位

这个 skill 适合用于：

- 中文或多语新闻的中心事件 5W1H 抽取；
- 面向知识超图的事件超边构建；
- 把旧的全局节点索引改造成可审阅的 record-first 标注视图；
- 抑制重复 tag、泛化词 tag 和滑窗式事件爆炸，同时保留中心事件相关参与方；
- 论文或实验中的 skill-guided extraction baseline。

## License

MIT License. See [LICENSE](LICENSE).
