# Chinese Contrastive Calibration Cases

Use these cases as semantic few-shot calibration. Match the reasoning pattern, not the words.

## Contents

- Multi-party event and clause-length WHO
- Implicit WHY and HOW
- Neighboring-predicate and attribution-shell rejection
- Cause, method, and result direction
- Final contrastive check

## 1. Multi-Party Court Event

```text
周一，国际法院裁定日本不得继续年度捕鲸活动，并驳回日本关于科学研究目的的说法。法院要求日本撤销现有许可并停止发放新许可。此前，澳大利亚政府挑战日本捕鲸项目。日本捕鲸船队和SeaShepherd等环保组织长期围绕捕鲸活动对峙。
```

```text
root: 国际法院裁定日本不得继续年度捕鲸活动
WHO: 国际法院；日本；澳大利亚政府；日本捕鲸船队；SeaShepherd等环保组织
WHAT: 国际法院裁定日本不得继续年度捕鲸活动
WHEN: 周一
WHERE: 国际法院（司法论坛）
WHY: 澳大利亚政府挑战日本捕鲸项目；法院驳回科学研究目的说法
HOW: 法院要求撤销现有许可并停止发放新许可
```

Five WHO tags are justified because they are distinct participants in the direct adjudication, challenge, implementation, or monitored activity chain. Do not add reporters or every organization mentioned in background.

## 2. Clause-Length WHO

```text
俄罗斯联邦空军基本战斗序列将组建7个战役司令部。
```

```text
wrong WHO: 俄罗斯联邦空军基本战斗序列将组建7个战役司令部
right WHO: 俄罗斯联邦空军
right WHAT: 俄罗斯联邦空军基本战斗序列将组建7个战役司令部
```

The predicate belongs in WHAT, never inside WHO.

## 3. Implicit WHY Without A Connector

```text
关键零部件连续两周未到货，工厂将首批设备的交付期限推迟到下月。
```

```text
root: 工厂推迟交付期限
WHY: 关键零部件连续两周未到货
Evidence_Status: implicit
```

The first proposition explains the second even though there is no `因为` or `由于`.

## 4. Implicit HOW As Serial Actions

```text
工程团队先拆除旧雷达，再安装新阵列，完成了系统升级。
```

```text
root: 工程团队完成系统升级
HOW: 先拆除旧雷达，再安装新阵列
Evidence_Status: implicit
```

The ordered actions realize the upgrade without `通过` or `利用`.

## 5. Neighboring Predicate Is Not The Root

```text
周三，市政府批准新防洪工程。施工单位将分三期加固堤坝。
```

```text
root: 市政府批准新防洪工程
HOW for root: missing
```

`分三期加固堤坝` answers how the later construction will occur, not how the approval occurred.

## 6. Attribution Shell

```text
国防部长表示，俄罗斯将在年底前完成两部反导雷达建设。
```

```text
root: 俄罗斯将在年底前完成两部反导雷达建设
WHO: 俄罗斯
WHAT: 俄罗斯将在年底前完成两部反导雷达建设
```

Do not select `表示` as trigger or the minister as root actor unless the statement itself is the essential event.

## 7. Cause, Method, And Result Direction

```text
预算削减，团队先停用旧设备并安装新阵列，完成升级后探测距离提高。
```

```text
root: 团队完成升级
WHY: 预算削减 only when the text supports it as motivation or constraint
HOW: 先停用旧设备并安装新阵列
result: 探测距离提高, not WHY/HOW for the upgrade
```

Always identify proposition direction before selecting a span.

## Final Contrastive Check

Before output, ask:

1. Does every node answer the frozen predicate of its own event?
2. Is every WHO an entity rather than a clause?
3. Did coreferent mentions collapse into one participant?
4. Does WHY explain the root rather than describe its result?
5. Does HOW realize the root rather than describe another event?
6. Would the tag still be correct if all familiar cue words were removed?
