# Deduplication And Selection

## Contents

- Text normalization and exact duplicates
- Nested aliases and local coreference
- Clause and role-conflict guards
- Candidate ranking, cardinality, and generic spans

Apply these rules after semantic role assignment and before offset generation.

## Normalize

```text
normalize(text) = casefold + trim + collapse whitespace
```

For Chinese, remove spaces that are only formatting noise between Chinese characters.

## Exact Duplicate

The key must be unique inside one record:

```text
Node_Type + normalize(Tag_Text)
```

Keep the candidate with the best event linkage, semantic fit, and source offset.

## Nested Same-Referent Spans

Collapse nested aliases that refer to the same participant:

```text
俄罗斯 + 俄罗斯空军 + 俄罗斯联邦空军 -> 俄罗斯联邦空军
美国 + 美国国务院                   -> 美国国务院
```

Do not collapse distinct referents merely because one string contains another:

```text
日本 + 日本捕鲸船队 -> keep both when both are central participants
```

For other roles, retain the shortest span that is complete. A longer clause does not win merely because it contains more words.

## Coreference Duplicate

Create a record-local identity key before selecting WHO tags:

```text
full name + short name + title + pronoun -> one participant identity
```

Examples:

```text
国际法院 + 法院                         -> keep 国际法院
谢尔盖·绍益古 + 俄罗斯国防部长 + 他     -> keep the clearest named mention
俄罗斯 + 该国                           -> keep 俄罗斯 when both refer to the same actor
```

Do not emit a pronoun as a second WHO merely because it has a different offset. Frequency supports confidence but never creates additional nodes.

## Clause Guard

Reject WHO and WHERE candidates that include an event predicate. Reject spans containing unrelated coordinated clauses.

Common invalid WHO endings:

```text
宣布  表示  称  将组建  将构成  计划部署  进行测试  完成采购
```

## Role Conflict

Assign a span to the question it answers best:

- entity/noun phrase -> WHO;
- central action/state -> WHAT;
- event time -> WHEN;
- event setting -> WHERE;
- cause/purpose/rationale -> WHY;
- means/manner/procedure -> HOW.

Allow exact WHO/WHERE reuse only for an explicit forum or site with both functions. Do not duplicate text across other roles.

## Candidate Ranking

Use this priority:

1. direct connection to the current event predicate;
2. correct semantic role;
3. concise completeness;
4. explicit source span;
5. headline/lead or root-sentence proximity;
6. frequency/coreference support;
7. earlier position.

Drop a candidate when its role confidence is lower than the false-positive risk. `Missing` is a valid result.

## Cardinality

Caps are maxima:

```text
WHO typical 1-3, max 5
WHAT typical 1, max 2
WHEN max 1
WHERE max 1
WHY typical 0-1, max 2
HOW typical 0-1, max 2
TOTAL typical 2-6; 7+ needs explicit justification; max 12
```

The second answer for a role must be non-overlapping in meaning and indispensable. Never select extra candidates simply because capacity remains.

## Generic Span Guard

Reject standalone generic spans when a specific phrase exists:

```text
系统  导弹  武器  飞机  潜艇  计划  项目  目前  公司  海军  空军
```

These words may remain inside a specific entity or action phrase.
