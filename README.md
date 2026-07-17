# CEH-5W1H Skill

语言：中文 | [English](README.en.md)

`ceh-5w1h` 是一个面向 Codex 的事件簇优先 5W1H 与知识超图抽取 skill。默认采用 **Cluster-first + Per-event 5W1H + Independent Critic Agent**：先发现事件簇，再选出簇内中心事件及少量关系关键的辅助事件，随后为每个事件建立独立 5W1H 超边，最后交给独立 Agent 复核。

```text
Text -> Event_Clusters -> Events -> 5W1H Nodes -> Hyperedges/Relations -> Critic Agent -> Validation
```

## v3 本次更新

- 恢复并强化“先事件簇、后事件、再逐事件 5W1H”的主流程，避免把整篇文本压成一个事件，也避免滑窗式事件爆炸。
- 使用记录内 `S* / N* / EC* / E* / HE*` 稳定编号，让原文、证据、节点、事件和超边可直接追溯。
- 每个事件独立维护 5W1H、`Missing` 和超边，禁止跨事件借用角色；共享实体只复用节点，不重复创建。
- 增加独立 Critic Agent 复核协议、结构校验器和语义风险检查器，重点检查长句 WHO、重复事件、错误角色归属及 WHY/HOW 方向。
- 批处理改为单条无状态抽取、逐条校验和失败单条重试，并加入中文案例与跨语言金标校准资料。

## 默认输出：ceh-cluster-v3

```json
{
  "schema_version": "ceh-cluster-v3",
  "records": [
    {
      "Id": "R1",
      "Text": "国际法院裁定日本停止捕鲸。",
      "Sentences": [
        {
          "Sentence_Id": "S1",
          "Tag_Text": "国际法院裁定日本停止捕鲸。",
          "Tag_Start": 0,
          "Tag_End": 13
        }
      ],
      "Nodes": [
        {
          "Node_Id": "N1",
          "Node_Type": "who",
          "Tag_Text": "国际法院",
          "Tag_Start": 0,
          "Tag_End": 4,
          "Evidence_Status": "explicit"
        },
        {
          "Node_Id": "N2",
          "Node_Type": "what",
          "Tag_Text": "日本停止捕鲸",
          "Tag_Start": 6,
          "Tag_End": 12,
          "Evidence_Status": "explicit"
        }
      ],
      "Event_Clusters": [
        {
          "Cluster_Id": "EC1",
          "Topic": "国际法院裁定日本停止捕鲸",
          "Central_Event": "E1",
          "Events": [
            {
              "Event_Id": "E1",
              "Event_Level": "central",
              "Event_Text": "国际法院裁定日本停止捕鲸",
              "Trigger": {
                "Tag_Text": "裁定",
                "Tag_Start": 4,
                "Tag_End": 6
              },
              "Evidence": ["S1"],
              "Missing": ["when", "where", "why", "how"],
              "Event_Hyperedge": {
                "Hyperedge_Id": "HE1",
                "Event": "E1",
                "Nodes": {
                  "who": ["N1"],
                  "what": ["N2"],
                  "when": [],
                  "where": [],
                  "why": [],
                  "how": []
                }
              }
            }
          ],
          "Relations": []
        }
      ],
      "Cross_Cluster_Relations": [],
      "Review": {
        "Mode": "independent_agent",
        "Status": "passed",
        "Reviewer": "semantic_critic",
        "Issues_Found": [],
        "Changes_Made": []
      }
    }
  ]
}
```

默认约束：

- 先抽事件簇，再抽簇内事件，最后逐事件抽 5W1H；不能跳过簇发现直接做一张全局表。
- 每个事件簇恰好一个中心事件，默认只保留 0-2 个关系关键的辅助事件，硬上限为 5。
- 每个事件都有自己的中心谓词、`Missing` 和超边，不能跨事件借用角色。
- `S1/S2` 是记录内证据编号，`N1/N2` 是记录内去重节点编号，不再使用难审阅的全局节点大索引。
- 默认只保留每个角色最优答案；通常每事件 2-6 个节点，12 只是硬上限。
- `WHO` 通常 1-3 个，且必须是最小实体短语；保留必要参与方，但合并同一对象的全称、简称、头衔和代词。
- WHY/HOW 不依赖关键词：有提示词不等于标签成立，没有提示词也可以存在明确或上下文隐含的 WHY/HOW 关系。
- `Tag_Text` 必须等于 `Text[Tag_Start:Tag_End]`。
- 同一 record 内不得重复输出 `Node_Type + Tag_Text`；共享实体由多个事件超边复用同一 `N*`。
- 找不到可靠答案时写入 `Missing`，不为了完整而猜测。
- `Evidence_Status` 表示显式或隐式证据；只有要求可靠性时才增加独立的 `Reliability_Label`。
- 初稿必须经过独立 Critic Agent；没有子 Agent 能力时只能标记为 `self_critic_fallback + needs_human_review`。
- 旧的单根事件 `ceh-record-v2` 仅在 `root_only=true` 时使用；全局索引仅在 `global_index=true` 时使用。

## 仓库结构

```text
.
|-- ceh-5w1h/                 # 可安装的 Codex skill
|   |-- SKILL.md
|   |-- agents/
|   |-- references/
|   |   |-- schema.md
|   |   |-- cluster-policy.md
|   |   |-- state-machine.md
|   |   |-- reviewer-protocol.md
|   |   |-- role-coverage.md
|   |   |-- deduplication.md
|   |   |-- semantic-role-reasoning.md
|   |   |-- cross-lingual-calibration.md
|   |   |-- chinese-calibration-cases.md
|   |   |-- reliability.md
|   |   |-- gold-calibration.md
|   |   `-- ...
|   `-- scripts/
|       |-- validate_ceh_cluster_output.py
|       |-- validate_ceh_cluster_semantic_output.py
|       |-- validate_ceh_record_output.py
|       |-- validate_ceh_semantic_output.py
|       |-- prepare_ceh_batch_jobs.py
|       |-- analyze_5w1h_jsonl.py
|       |-- migrate_ceh_evidence_fields.py
|       |-- convert_ceh_global_to_record_view.py
|       |-- validate_ceh_output.py
|       `-- compare_ceh_outputs.py
|-- examples/
|   |-- ceh-cluster-v3-output.json
|   |-- ceh-cluster-v3-risk-report.json
|   |-- ceh-record-v2-output.json
|   |-- ceh-whaling-output.json
|   |-- ceh-semantic-regression-output.json
|   |-- ceh-semantic-implicit-output.json
|   |-- ceh-chinese-calibration-output.json
|   `-- ceh-minimal-output.json
|-- docs/
|   `-- flares-calibration-summary.json
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
$ceh-5w1h 请先发现事件簇，再为簇内每个保留事件抽取独立 5W1H 超边，并用独立 Agent 复核：
...
```

更详细的安装说明见：[docs/INSTALL.md](docs/INSTALL.md)

## 校验输出

新版输出依次经过“事件簇/事件语义检查 + 独立 Agent 复核 + 结构校验 + 确定性风险检查”四道门：

```bash
python ceh-5w1h/scripts/validate_ceh_cluster_output.py examples/ceh-cluster-v3-output.json
python ceh-5w1h/scripts/validate_ceh_cluster_semantic_output.py examples/ceh-cluster-v3-output.json --report risk-report.json
```

独立 Critic Agent 先检查事件簇、重复事件、中心事件、逐事件角色归属及 WHY/HOW 命题方向；脚本只能发现偏移、引用、长句 WHO、重复和密度等已知风险。脚本返回 `LINT_CLEAR` 仅表示没有命中已知风险，不代表语义正确。

风险检查器是质量门，不是准确率证明；在建立中文人工金标测试集并完成抽样评测前，不应宣称达到“高质量”或某个准确率。

批量文本先按最多 100 条划分任务会话，但每次模型调用仍只处理一条记录：

```bash
python ceh-5w1h/scripts/prepare_ceh_batch_jobs.py input.txt jobs --records-per-session 100
```

处理原则是“单条无状态抽取、逐条校验、失败单条重试、每 100 条重置上下文”，禁止把 100 或 300 条原文塞进一个提示词。

把旧的全局 CEH JSON 转成便于人工审阅的 record-first 视图：

```bash
python ceh-5w1h/scripts/convert_ceh_global_to_record_view.py old_ceh.json old_ceh_record_v2.json
python ceh-5w1h/scripts/validate_ceh_record_output.py old_ceh_record_v2.json
```

旧输出如果把 `direct/inferred/converted` 错放在 `Reliability_Label`，可无损迁移：

```bash
python ceh-5w1h/scripts/migrate_ceh_evidence_fields.py old.json migrated.json
```

## 跨语言校准

本地西班牙语金标的 1,753 条已标注记录共含 7,485 个精确跨度；WHY 仅出现在 12.5% 的记录中，HOW 出现在 28.3% 中。这些数字只用于提醒“缺失是正常的、不要强行填满”，不是中文输出配额。

```bash
python ceh-5w1h/scripts/analyze_5w1h_jsonl.py train.json trial.json --report calibration.json
```

Skill 只迁移中心谓词锚定、精确跨度、多参与方和逐标签可靠性等语言无关原则；不会把西班牙语介词、词序或重复标注规则改写成中文正则表达式。

本次完整统计快照见：[docs/flares-calibration-summary.json](docs/flares-calibration-summary.json)

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
- 拒绝长句 WHO、归因壳中心事件和依赖关键词的 WHY/HOW 误判，并恢复无连接词但语义关系明确的隐式 WHY/HOW；
- 论文或实验中的 skill-guided extraction baseline。

方法校准参考了 [Giveme5W1H](https://github.com/fhamborg/Giveme5W1H) 的公开黄金数据与主事件候选排序思想、2025 年 [5W1H prompt strategies](https://github.com/cmunhozc/5W1H-prompt-strategies) 的逐问题推理与正文过滤方法，以及本地 FLARES 西班牙语金标的跨度与缺失分布。这里采用的是面向中文事件超图的重新设计，并非照搬英语或西班牙语规则系统。

## License

MIT License. See [LICENSE](LICENSE).
