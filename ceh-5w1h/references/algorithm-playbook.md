# Algorithm Playbook

Use this playbook when extraction quality matters, especially for noisy news, military reports, policy text, or paper-style method demonstrations.

The playbook converts well-established extraction ideas into CEH-5W1H rules without requiring a specific model implementation.

## 1. Main-Event First

Goal: avoid shredding a document into unrelated 5W1H fragments.

For each cluster, score candidate events:

```text
root_score =
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
- `cluster_explanation_power`: whether the event summarizes why the cluster exists.
- `side_detail_penalty`: numerical details, equipment specs, quote fragments, or background facts with weak relation value.

Keep one root event per cluster unless the text truly contains two co-equal central claims.

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

- map the enriched event into who/what/when/where/why/how node groups.
- preserve original spans and evidence IDs.

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
- Multiple nodes are allowed for one role when the event genuinely has multiple participants, sites, systems, or methods.
- Do not borrow a role from a neighboring event unless a relation hyperedge explains why.
- Use empty lists for missing roles.

## 4. Document-Level Event Memory

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
- a capability or method sentence explains how the root event is possible.
- a background sentence motivates a later action.

Do not use memory to merge independent briefs.

## 5. Span Graph Reasoning

Before final JSON, check whether important spans are connected:

```text
entity span -> trigger/predicate -> argument span -> event -> cluster
```

Use this to catch:

- dangling entities that should be nodes.
- missing triggers.
- an event with no evidence-backed what.
- a relation that links clusters only by topic similarity rather than textual evidence.

If an entity is important but not part of any event hyperedge, either attach it to an event role or discard it.

## 6. Constrained Structure Generation

Generate JSON under constraints:

- IDs must be compact and sequential.
- Every event must have exactly one event hyperedge.
- Every hyperedge must contain six role groups.
- Relation names must come from the controlled vocabulary.
- Every node/event/relation/cluster must cite evidence IDs.

Use constrained generation thinking: fill required fields first, then optional detail. Do not output natural-language commentary inside JSON.

## 7. Stability Audit

For high-confidence extraction, compare independent passes.

Classify each candidate:

- `stable`: same event meaning and role assignment in most passes.
- `unstable`: same approximate event but different role, boundary, or relation.
- `missed`: evidence-backed event absent from at least one pass.

Decision rules:

- Keep stable root events.
- Review unstable events before including them.
- Add missed events only if they are central or relation-critical.
- Do not inflate the graph just because one pass found many side details.

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
