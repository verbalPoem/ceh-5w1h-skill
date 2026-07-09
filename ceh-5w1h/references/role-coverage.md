# Role Coverage Rules

Use these rules before final tag selection. The goal is **center-event coverage**, not sentence fragmentation.

## Center-Event Corridor

Keep one `Root_Event`, but allow tags from sentences that are directly connected to that root event.

Directly connected context includes:

- the decision maker, announcer, court, agency, or source;
- the regulated target, affected actor, owner, victim, or object owner;
- the claimant, challenger, prosecutor, opponent, monitor, or organization that triggered the event;
- the order, measure, mechanism, permission, sanction, deployment, or administrative action that implements the event;
- the stated rationale, rejected rationale, motivation, legal challenge, risk, or purpose.

Do not create separate root events for these connected details unless `full_detail=true`.

## WHO Coverage

`WHO` is not only the grammatical subject. Include the central participants required to understand the root event:

```text
adjudicator/source/actor
regulated target
claimant/challenger/opponent
affected operational actor
monitoring or blocking organization
```

Example: for an international court ruling on whaling, keep `国际法院`, `日本`, `澳大利亚政府`, `日本捕鲸船队`, and `SeaShepherd等环保组织` as `WHO` if all are explicitly stated and directly connected to the ruling.

## WHERE Coverage

`WHERE` may be a physical location or an institutional forum.

Allow the same text to be both `WHO` and `WHERE` when it plays both functions:

- `国际法院` as the adjudicator/source (`WHO`) and the legal forum (`WHERE`);
- a meeting as the actor's stated forum and the event venue;
- a base or command as an organization/platform and the location.

Do not use country or organization names as `WHERE` just because they appear in the text.

## WHY Coverage

`WHY` includes:

- legal challenges or complaints that led to the root event;
- rejected rationales or denied justifications;
- stated risks, purposes, motivations, or causes.

Two `WHY` tags are allowed when both a cause/challenge and a rejected rationale are stated.

## HOW Coverage

`HOW` includes the mechanism or implementation of the root event, not only technical methods.

For rulings, policies, sanctions, permits, procurement, deployments, or investigations, `HOW` may be:

- an order or requirement;
- a permit revocation or refusal to issue permits;
- a procedural action;
- an administrative or legal mechanism.

Do not demote these spans to `WHAT` if they answer how the root decision is carried out.

## Default Caps

```text
WHO <= 5
WHAT <= 2
WHEN <= 1
WHERE <= 1
WHY <= 2
HOW <= 2
TOTAL <= 12
```

These caps are still strict enough to prevent node explosion, but large enough to keep the event ecology readable.
