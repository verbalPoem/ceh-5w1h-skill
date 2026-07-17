# Algorithm Playbook

## Contents

- Cluster discovery, central-event selection, and coarse-to-fine construction
- QA-style role extraction and semantic relation classification
- Document-level memory and span graph reasoning
- Constrained generation and stability audit
- Checked source ideas

Use this playbook when extraction quality matters, especially for noisy news, military reports, policy text, or paper-style method demonstrations. Read `gold-calibration.md` first.

The playbook converts well-established extraction ideas into CEH-5W1H rules without requiring a specific model implementation.

Default mode is `ceh-cluster-v3`: read one record, discover coherent event clusters, select one central event plus only relation-critical supporting events per cluster, extract sparse record-local `N*` nodes for every accepted event, and connect them through per-event hyperedges. Caps are maxima, not quotas.

## 1. Cluster First, Then Central Events

Goal: avoid shredding a document into unrelated 5W1H fragments.

First group candidate predicates using `cluster-policy.md`. Then score candidate central events inside each cluster:

```text
central_score =
  source_position
  + predicate_salience
  + relation_degree
  + evidence_density
  + cluster_explanation_power
  - side_detail_penalty
```

Signals:

- `source_position`: title, lead sentence, opening claim, or summary sentence.
- `predicate_salience`: announced, disclosed, deployed, completed, died, launched, exhibited, warned, claimed, built, tested.
- `relation_degree`: how many other accepted events depend on or explain this event.
- `evidence_density`: whether who/what/when/where are explicitly recoverable.
- `cluster_explanation_power`: whether the event organizes the cluster's event chain.
- `side_detail_penalty`: numerical details, equipment specs, quote fragments, or background facts with weak relation value.

Keep exactly one central event per cluster. Retain supporting events only when they have distinct predicates and useful evidence-backed relations to that central event. Do not force an entire multi-brief record into one event.

Before scoring event candidates, remove attribution shells. In `某官员表示，X完成了测试`, prefer `X完成了测试` unless the statement itself is the main news. Reporting verbs receive a penalty when a stronger embedded action is available.

## 2. Coarse-to-Fine Hyperedge Construction

Do not jump directly from raw text to a full hyperedge.

Use three passes:

```text
binary skeleton -> qualified skeleton -> event hyperedge
```

Pass A, binary skeleton:

- actor/source/owner
- predicate/action/state
- object/target/result

Pass B, qualifiers:

- time, place, cause, purpose, method, quantity, status, condition.

Pass C, hyperedge:

- map the enriched event into who/what/when/where/why/how tag groups.
- preserve exact source spans with `Tag_Start` and `Tag_End`.

This mirrors the useful part of coarse-to-fine knowledge hypergraph extraction: build a stable structural backbone before adding fine-grained qualifiers.

## 3. QA-Style Role Extraction

For each accepted event, ask role questions against only that event's evidence span.

Question templates:

- Who is the actor, source, owner, participant, victim, or affected party?
- What action, state, claim, system, object, or result is central?
- When is the event time, as-of time, planned time, deadline, or report time?
- Where is the location, deployment site, affected area, facility, theater, or platform?
- Why is the event happening, what risk/goal/cause/motivation is stated?
- How is it performed, enabled, measured, deployed, built, transported, or demonstrated?

Rules:

- Prefer exact spans over paraphrases.
- Select one best answer per role by default. Multiple tags are allowed only when they contribute distinct, indispensable information within the hard caps.
- Do not borrow a role from a neighboring event unless a relation hyperedge explains why.
- Omit missing tags and list their uppercase labels in `Missing`.
- For `WHO`, keep the directly connected event ecology: actor/source, target, challenger, affected actor, and monitoring/opposition group when they are explicitly stated.
- For `HOW`, include legal, administrative, or procedural implementation spans such as orders, permit revocation, or refusal to issue new permits.
- For `WHO`, reject noun phrases containing an event predicate or an entire subordinate clause.
- For `WHY`, require a supported explanatory relation to the current event, but allow the relation to be implicit in local discourse.
- For `HOW`, require a supported means, manner, mechanism, procedure, action sequence, or implementation relation, even when no method cue word appears.

After answering all roles, run a contrastive pass: ask whether each span answers its assigned question better than its nearest competing question. This is mandatory for WHO/WHAT and WHY/HOW. Keywords may retrieve candidates but must not assign roles.

## 4. Semantic Relation Classification

For every WHY/HOW candidate, compare two propositions:

```text
E = current event proposition
C = candidate evidence proposition
```

Classify the directed relation:

```text
cause/motivation/purpose/justification/enabling condition: C -> E -> WHY
means/manner/instrument/procedure/implementation:           C -> E -> HOW
result or consequence:                                     E -> C -> neither
background, coincidence, or topic similarity:                      reject
```

Run two semantic paraphrases: `E because of C` and `E by doing/using C`. Keep the reading that preserves the source meaning. If the relation is strongly implied but unmarked, retain the exact evidence span with `Evidence_Status: implicit`. Do not infer from world knowledge.

See `semantic-role-reasoning.md` for relation inventories and examples.

## 5. Document-Level Event Memory

Arguments often scatter across sentences. Maintain a temporary event memory:

```json
{
  "candidate_event": "short event label",
  "known_roles": {"who": [], "what": [], "when": [], "where": [], "why": [], "how": []},
  "open_questions": [],
  "supporting_sentences": []
}
```

Use memory to merge cross-sentence evidence when:

- a pronoun or abbreviated name refers to an earlier actor.
- a later sentence gives the time/place of an earlier event.
- a capability or method sentence explains how the current event is possible.
- a background sentence motivates a later action.

Do not use memory to merge independent briefs.

Clear this memory after every record. In batch mode, never let the actor list, event type, or missing roles from one record seed the next record.

## 6. Span Graph Reasoning

Before final JSON, check whether important spans are connected:

```text
entity span -> trigger/predicate -> argument span -> event -> cluster -> record
```

Use this to catch:

- dangling entities that should either become event tags or be discarded.
- missing triggers.
- an event with no evidence-backed what.
- a relation that links clusters only by topic similarity rather than textual evidence.

If an entity is important but not part of any accepted event hyperedge, either attach it to the correct event role or discard it.

## 7. Constrained Structure Generation

Generate JSON under constraints:

- Use `schema_version: "ceh-cluster-v3"` by default.
- Every record must contain one or more evidence-backed event clusters.
- Every cluster must have exactly one central event.
- Every accepted event must have exactly one `Event_Hyperedge`.
- Every hyperedge must contain six role groups.
- Every sentence, node, and trigger must pass `Tag_Text == Text[Tag_Start:Tag_End]`.
- Event relations use the controlled vocabulary and explicit `S*` evidence.
- Structural validity is only the first gate. Run an independent critic Agent, then use `validate_ceh_cluster_semantic_output.py` as a deterministic risk linter before release.

Use constrained generation thinking: fill required fields first, then optional detail. Do not output natural-language commentary inside JSON.

## 8. Stability Audit

For high-confidence extraction, compare independent passes.

Classify each candidate:

- `stable`: same event meaning and role assignment in most passes.
- `unstable`: same approximate event but different role, boundary, or relation.
- `missed`: evidence-backed event absent from at least one pass.

Decision rules:

- Keep stable clusters, central events, and supporting events.
- Review unstable events before including them.
- Add missed events only if they are central or relation-critical.
- Do not inflate the graph just because one pass found many side details.
- If WHY or HOW changes role across passes, omit it or send it to review instead of choosing the longer span.

When multiple JSON files exist, run:

```text
python ceh-5w1h/scripts/compare_ceh_outputs.py pass1.json pass2.json pass3.json
```

## Checked Source Ideas

This playbook adapts ideas from:

- Hyper-KGGen: use skill-driven, coarse-to-fine hypergraph extraction and stability-based feedback.
  Source: https://arxiv.org/abs/2602.19543
- Giveme5W1H: use 5W1H to describe a news article's main event rather than every sentence.
  Source: https://github.com/fhamborg/Giveme5W1H
- Imitating Human Reasoning to Extract 5W1H in News: use main-event evidence filtering and question-level reasoning; allow difficult roles to remain empty.
  Sources: https://doi.org/10.1145/3701716.3715532 and https://github.com/cmunhozc/5W1H-prompt-strategies
- Doc2EDAG: track document-level events whose arguments scatter across sentences.
  Source: https://arxiv.org/abs/1904.07535
- Event Extraction by Answering Natural Questions: formulate event arguments as QA.
  Source: https://aclanthology.org/2020.emnlp-main.49/
- PAIE: use prompt-based start/end span selection and multi-role argument interaction.
  Source: https://aclanthology.org/2022.acl-long.466/
- Text2Event: use constrained sequence-to-structure thinking for event output generation.
  Source: https://aclanthology.org/2021.acl-long.217/
- OneIE and DyGIE++: keep entity, relation, and event decisions graph-consistent.
  Sources: https://aclanthology.org/2020.acl-main.713/ and https://aclanthology.org/D19-1585/
