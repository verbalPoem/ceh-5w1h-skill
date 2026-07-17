# Strict Role Coverage

## Contents

- Event-link and root-predicate tests
- WHO, WHAT, WHEN, and WHERE boundaries
- Semantic WHY and HOW boundaries
- Neighboring-predicate rejection

Extract roles separately for each accepted event, not once for the whole cluster or topic. A role must pass both an event-link test and a boundary test.

First freeze the current event's predicate. Ask all six questions about that predicate, not about whichever local verb is closest to the candidate span.

## Event-Link Test

Keep a span only if this sentence is true:

```text
The span directly answers ROLE for CURRENT_EVENT.
```

Topic similarity, shared equipment names, and presence in the first three sentences are not sufficient.

## WHO

WHO is a minimal entity or noun phrase, never an event clause.

Allowed participant functions:

- actor, decision maker, adjudicator, source when the reporting act is central;
- target, regulated party, victim, owner, affected party;
- challenger, opponent, monitor, or implementing organization when indispensable to the current event.

Build the participant set from semantic functions, not grammatical subject position alone. Chinese subjects may be omitted, topicalized, or replaced by `该国`, `其`, `后者`, or `该系统`; resolve these only from the local evidence corridor.

Boundary rules:

- Stop before finite predicates such as `宣布`, `表示`, `组建`, `构成`, `部署`, `要求`, or `计划`.
- Remove leading time, place, source, and discourse material.
- Prefer the most specific acting entity over a nested country alias: keep `俄罗斯联邦空军`, not both `俄罗斯` and `俄罗斯联邦空军`.
- Keep two same-country entities only when they are different referents, such as `日本` and `日本捕鲸船队`.
- Collapse repeated full names, abbreviations, titles, and pronouns that refer to the same participant. Keep the clearest exact mention as the canonical tag.
- Do not keep reporters, websites, or quoted speakers unless their communicative act is the current event.

Example:

```text
wrong WHO: 俄罗斯联邦空军基本战斗序列将组建7个战役司令部
right WHO: 俄罗斯联邦空军
right WHAT: 俄罗斯联邦空军基本战斗序列将组建7个战役司令部
```

Typical WHO count is one to three. Four or five requires a genuinely multi-party event.

## WHAT

WHAT is the compact main claim: central predicate plus required object, target, state, or result.

- Remove attribution shells when the embedded action is stronger.
- Remove publication/source prefixes and unrelated trailing clauses.
- Do not return only an equipment name when the text states an action involving that equipment.
- Prefer one WHAT. Keep two only for coordinated, equally central actions under the same event.

Example:

```text
source: 某官员宣布，俄罗斯联邦空军将组建7个战役司令部，同时继续改造高空歼击机。
primary WHAT: 俄罗斯联邦空军将组建7个战役司令部
optional second WHAT: 继续对高空歼击机进行现代化改造
```

## WHEN

Choose the time that belongs to the root action.

Priority:

1. explicit current-event time;
2. deadline or as-of time for a plan/status event;
3. publication-relative time only when it clearly anchors the event.

Do not choose a historical background date because it is the only four-digit year in the record.

## WHERE

Choose the most specific explicit event setting:

- physical location or affected area;
- deployment site, base, ship, platform, theater, or venue;
- institutional forum when the action occurs through that forum.

A country or organization mention is not automatically WHERE. The same text may be WHO and WHERE only when it explicitly serves as both actor/forum or organization/site.

## WHY

WHY is a proposition that causally, motivationally, purposively, or normatively explains the current event. Decide by the directed relation `C -> E`, not by whether the span contains a familiar connector.

Valid relations include cause, motivation, justification, purpose, enabling condition, legal challenge, and risk addressed by the current event.

Possible cue words may help locate candidates, but are optional and never sufficient. A WHY can be expressed through sentence order, modality, contrast, a preceding condition, or an event relation without `因为` or `由于`.

Examples:

```text
项目预算被削减，研发团队只能暂停测试
WHY: 项目预算被削减

敌机连续抵近领空，部队紧急增派防空系统
WHY: 敌机连续抵近领空

澳大利亚政府挑战日本捕鲸项目，法院最终作出裁决
WHY for the ruling: 澳大利亚政府挑战日本捕鲸项目
```

For each candidate, test whether `E happened, was selected, or was needed because of C` preserves the source meaning. Reject consequences, coincidence, and background that do not explain the current event.

Use `Evidence_Status: implicit` when the evidence fact is explicit but the explanatory relation is strongly implied rather than stated. Do not infer from world knowledge.

## HOW

HOW is a proposition that realizes the current event as its means, manner, instrument, mechanism, procedure, execution sequence, required action, or implementation. Decide by the directed relation `C -> E`, not by a method keyword.

A HOW can be expressed as serial verbs, ordered steps, a subordinate action, a passive construction, a composition statement, or an administrative action without `通过` or `利用`.

Examples:

```text
工程人员先拆除旧雷达，再安装新阵列，系统升级完成
HOW for the upgrade: 先拆除旧雷达，再安装新阵列

法院撤销现有许可并停止发放新许可，落实禁捕裁决
HOW for implementing the ruling: 撤销现有许可并停止发放新许可

7个战役司令部由航空基地和空天防御旅组成
HOW for forming the command structure: 由航空基地和空天防御旅组成
```

For each candidate, test whether `E was performed, implemented, or achieved by C` preserves the source meaning. Reject causes, purposes, results, and neighboring-event details that do not describe execution.

For mixed spans, identify the propositions first and then split by relation:

```text
预算受限，团队先拆除旧设备再安装新阵列，完成系统升级
WHY: 预算受限
HOW: 先拆除旧设备再安装新阵列
```

If no clean exact span exists, leave the role missing rather than outputting a mixed clause. See `semantic-role-reasoning.md` for the full relation inventory and critic procedure.

## Neighboring-Predicate Rejection

An answer may be locally correct but wrong for the current event:

```text
周三，市政府批准新防洪工程。施工单位将分三期加固堤坝。

root WHAT: 市政府批准新防洪工程
HOW for root: missing
```

`分三期加固堤坝` is HOW for the construction event, not HOW for the approval. Create a secondary frame only when `full_detail=true`.
