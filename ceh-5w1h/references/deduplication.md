# Deduplication Rules

Apply these rules before producing `ceh-record-v2`.

## Normalize

For duplicate comparison:

```text
normalize(text) = lowercase/casefold + trimmed whitespace + collapsed spaces
```

For Chinese text, also remove spaces between characters when they are only formatting noise.

## Exact Duplicate Rule

Inside one record, the key must be unique:

```text
5W1H_Label + normalize(Tag_Text)
```

If duplicates exist, keep the candidate with:

1. exact offset match;
2. longer and more specific span;
3. earlier source position;
4. higher confidence, if available.

## Substring Rule

Within the same role, prefer the more specific span:

- keep "美国国务院" over "美国";
- keep "E-2D先进鹰眼预警机" over "飞机";
- keep "海基雷达系统" over "系统";
- keep "2014年11月5日至7日" over "2014年".

Do not keep a generic substring if the longer phrase fills the same role.

## Role Conflict Rule

When the same text could be more than one role:

- country or organization as actor/source/owner -> `WHO`;
- country or region as affected/deployment location -> `WHERE`;
- system/platform/object being acted on -> `WHAT`;
- capability, method, mechanism, or procedure -> `HOW`;
- purpose, risk, cause, or motivation -> `WHY`.

Do not output the same `Tag_Text` as both `WHO` and `WHERE` in the same record unless the sentence explicitly uses it in both functions.

## Generic Span Guard

Avoid standalone generic tags when a more specific span exists in the record:

```text
系统
导弹
武器
飞机
潜艇
计划
目前
公司
海军
空军
陆军
中心
```

These words may appear inside a longer specific tag.

## Caps

Default caps:

```text
WHO <= 2
WHAT <= 2
WHEN <= 1
WHERE <= 1
WHY <= 1
HOW <= 1
TOTAL <= 8
```

If too many candidates remain:

1. keep tags attached to the root event;
2. keep tags with exact offsets;
3. keep longer specific spans;
4. keep earlier spans;
5. drop side details.

## Missing Roles

If a role has no retained tag, add the uppercase label to `Missing`.

Do not fill missing roles from world knowledge.
