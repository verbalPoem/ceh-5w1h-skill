# Algorithm Playbook

Use this playbook when extraction quality matters, especially for noisy news, military reports, policy text, or paper-style method demonstrations.

The playbook converts well-established extraction ideas into CEH-5W1H rules without requiring a specific model implementation.

Default mode is `ceh-record-v2`: read one record, select one root event, output capped inline `Tags`, and connect those tag indexes through one `Event_Hyperedge`. Treat cluster/node language below as optional global-index language unless the user explicitly asks for `global_index=true`.

## 1. Main-Event First

Goal: avoid shredding a document into unrelated 5W1H fragments.

For each record, score candidate events:

```text
root_score =
  source_position
  + predicate_salience
  + relation_degree
  + evidence_density
  + record_explanation_power
  - side_detail_penalty
```

Signals:

- `source_position`: title, lead sentence, opening claim, or summary sentence.
- `predicate_salience`: announced, disclosed, deployed, completed, died, launched, exhibited, warned, claimed, built, tested.
- `relation_degree`: how many other accepted events depend on or explain this event.
- `evidence_density`: whether who/what/when/where are explicitly recoverable.
- `record_explanation_power`: whether the event summarizes the record's essential content.
- `side_detail_penalty`: numerical details, equipment specs, quote fragments, or background facts with weak relation value.

Keep one root event per record unless the user explicitly asks for `full_detail=true`.

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
- Multiple tags are allowed for one role only within the default caps.
- Do not borrow a role from a neighboring event unless a relation hyperedge explains why.
- Omit missing tags and list their uppercase labels in `Missing`.

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
entity span -> trigger/predicate -> argument span -> root event -> record
```

Use this to catch:

- dangling entities that should either become event tags or be discarded.
- missing triggers.
- an event with no evidence-backed what.
- a relation that links clusters only by topic similarity rather than textual evidence.

If an entity is important but not part of the root event hyperedge, either attach it to an event role or discard it.

## 6. Constrained Structure Generation

Generate JSON under constraints:

- Use `schema_version: "ceh-record-v2"` by default.
- Every record must have exactly one `Root_Event`.
- Every record must have exactly one `Event_Hyperedge`.
- Every hyperedge must contain six role groups.
- Every tag must pass `Tag_Text == Text[Tag_Start:Tag_End]`.
- Relation names and global IDs are optional and belong to `global_index=true` output.

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
