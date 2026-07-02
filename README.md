# CEH-5W1H Skill

语言：中文 | [English](README.en.md)

`ceh-5w1h` 是一个面向 Codex 的事件簇 5W1H 知识超图抽取 skill。它的目标不是把文本拆成一张扁平 5W1H 表，而是把新闻、军事报道、政策文本、事故通报和技术报告组织成：

```text
Document -> Event Clusters -> Events -> 5W1H Event Hyperedges -> Event Relation Hyperedges
```

## 核心思想

```text
EC1 / EC2 = 事件簇
E1 / E2 = 事件
HE1 / HE2 = 事件内部的 5W1H 超边
RH1 / RH2 = 事件之间的关系超边
N1 / N2 = 5W1H 节点
S1 / S2 = 证据句
```

默认输出结构：

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

## 关系词表

默认事件关系使用固定词表：

```text
discloses       披露
supports        支撑
motivates       驱动/促使
causes          导致
part_of         属于
component_of    组成部分
background_of   背景
enables         使能够
contrasts_with  对比
```

## 仓库结构

```text
.
|-- ceh-5w1h/                 # 可安装的 Codex skill
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
$ceh-5w1h 把下面文本抽成事件簇 5W1H 知识超图，并画 Mermaid 图：
...
```

更详细的安装说明见：[docs/INSTALL.md](docs/INSTALL.md)

## 验证输出

```bash
python ceh-5w1h/scripts/validate_ceh_output.py examples/ceh-minimal-output.json
```

期望输出：

```text
VALID: 1 cluster(s), 2 event(s), 2 event hyperedge(s), 1 relation hyperedge(s)
```

## 方法定位

`ceh-5w1h` 适合用于：

- 多事件新闻结构化
- 5W1H 事件簇标注
- 知识超图构建
- 事件关系建模
- LLM 抽取方法实验
- 论文方法设计与消融实验

## License

MIT License. See [LICENSE](LICENSE).
