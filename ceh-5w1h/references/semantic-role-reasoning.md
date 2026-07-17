# Semantic Role Reasoning For WHY And HOW

Use proposition-level meaning, not keyword matching.

## Contents

- Build root and candidate propositions
- Classify their directed relation
- Run bidirectional paraphrase tests
- Recover implicit relations
- Separate cause, method, and result
- Assign reliability
- Perform an independent semantic review

## 1. Build Two Propositions

Represent the current accepted event as proposition `E` and each candidate evidence span as proposition `C`. Freeze the predicate of `E`; a relation to another local predicate does not answer the current event.

```text
E = actor + central predicate + object/result
C = the complete fact expressed by the candidate span or sentence
```

Resolve local pronouns and omitted subjects before comparing them. Do not add facts from world knowledge.

## 2. Classify The Directed Relation

Map a candidate to WHY when one of these directed relations is supported:

```text
CAUSE_OF(C, E)
MOTIVATES(C, E)
JUSTIFIES(C, E)
PURPOSE_OF(C, E)
ENABLING_CONDITION_OF(C, E)
RISK_ADDRESSED_BY(C, E)
```

Map a candidate to HOW when one of these directed relations is supported:

```text
MEANS_OF(C, E)
MANNER_OF(C, E)
INSTRUMENT_OF(C, E)
PROCEDURE_OF(C, E)
EXECUTION_STEP_OF(C, E)
IMPLEMENTATION_OF(C, E)
```

Reject these relations as WHY/HOW for `E`:

```text
RESULT_OF(C, E) or CONSEQUENCE_OF(C, E) with direction E -> C
BACKGROUND_ONLY(C, E)
TOPIC_SIMILARITY(C, E)
TEMPORAL_COINCIDENCE(C, E)
DETAIL_OF_A_DIFFERENT_EVENT(C, E)
```

## 3. Run Bidirectional Paraphrase Tests

Test the candidate in both frames without changing its meaning:

```text
WHY test: E happened, was selected, or was needed because of C.
HOW test: E was performed, implemented, or achieved by C.
```

Interpretation:

- only WHY test is coherent -> WHY;
- only HOW test is coherent -> HOW;
- both are coherent -> inspect relation direction and choose the more specific relation, otherwise review;
- neither is coherent -> reject.

These tests are semantic. Words such as `因为`, `为了`, `通过`, or `利用` may help locate a candidate but never decide the label.

## 4. Recover Implicit Relations

Allow a relation without an explicit connector when discourse structure strongly supports it.

### Implicit WHY

```text
项目预算被削减，研发团队只能暂停原型机测试。
E: 研发团队暂停原型机测试
C: 项目预算被削减
relation: CAUSE_OF(C, E)
WHY: 项目预算被削减
Evidence_Status: implicit
```

```text
敌机连续抵近领空，部队紧急增派防空系统。
E: 部队紧急增派防空系统
C: 敌机连续抵近领空
relation: MOTIVATES(C, E)
WHY: 敌机连续抵近领空
Evidence_Status: implicit
```

### Implicit HOW

```text
工程人员先拆除旧雷达，再安装新阵列，系统升级完成。
E: 系统升级完成
C: 工程人员先拆除旧雷达，再安装新阵列
relation: PROCEDURE_OF(C, E)
HOW: 先拆除旧雷达，再安装新阵列
Evidence_Status: implicit
```

```text
法院撤销现有许可并停止发放新许可，落实了禁捕裁决。
E: 法院落实禁捕裁决
C: 法院撤销现有许可并停止发放新许可
relation: IMPLEMENTATION_OF(C, E)
HOW: 撤销现有许可并停止发放新许可
Evidence_Status: explicit or implicit according to how explicitly the text links the actions
```

## 5. Separate Cause, Method, And Result

Use direction, not vocabulary:

```text
预算削减 -> 项目暂停                 WHY
拆除旧设备 + 安装新设备 -> 完成升级  HOW
完成升级 -> 性能提高                 result, not WHY/HOW for the upgrade
```

A sentence may contain both WHY and HOW. Extract separate minimal spans only when each relation is independently supported.

## 6. Evidence Status

- `explicit`: the text explicitly states the role relation, regardless of whether it uses a familiar cue word.
- `implicit`: the evidence proposition is explicit, but its WHY/HOW relation to the current event is strongly implied by local discourse.
- Do not use `implicit` for assumptions based on domain knowledge alone.

Do not confuse evidence status with optional content reliability. See `reliability.md`.

## 7. Semantic Critic

Before final output, independently re-evaluate every WHY/HOW tag:

1. Restate `E` and `C` internally.
2. Name the directed relation from the inventories above.
3. Verify that `C` attaches to the predicate of `E`, not a neighboring predicate.
4. Test WHY and HOW paraphrases.
5. Check relation direction.
6. Reject or review candidates whose relation cannot be named confidently.

Do not output this internal reasoning unless the user requests an explanation.
