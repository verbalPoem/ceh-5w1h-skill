# Cross-Lingual Calibration For Chinese 5W1H

Use the Spanish annotations as semantic and structural calibration, not as Spanish-language pattern rules.

## Calibration Evidence

A local audit of the labeled FLARES subtask-1 train and trial files found 1,753 records and 7,485 exact-span tags. All audited offsets followed the half-open rule `Text[start:end] == Tag_Text`.

```text
ROLE   records with role   share of records   total tags
WHO          1,137              64.9%            1,981
WHAT         1,514              86.4%            2,949
WHEN           652              37.2%              840
WHERE          614              35.0%              867
WHY            219              12.5%              245
HOW            496              28.3%              603
```

These rates are drift priors, not quotas or universal Chinese benchmarks. They show that missing roles are normal and that WHY/HOW should not be forced into every record.

## Transferable Principles

1. Anchor every question to the current event predicate, not to any nearby noun or sentence.
2. Preserve exact source spans and compute half-open character offsets after span selection.
3. Allow multiple indispensable participants, but do not confuse participant coverage with repeated mentions.
4. Treat roles as optional. Empty is better than a weakly attached answer.
5. Separate WHAT from HOW: WHAT states the root action or state; HOW states its manner, instrument, procedure, or implementation.
6. Separate WHY from HOW by directed semantic relation, not by prepositions or connectors.
7. Judge the reliability of each answer span independently when reliability is requested.

## Deliberate CEH Differences

The source annotation scheme is document-wide and may annotate repeated aliases, pronouns, long descriptions, or several local predicates. CEH is cluster-first and event-attached, so it deliberately changes these choices:

- collapse repeated mentions and coreferent aliases into one canonical participant tag;
- prefer a concise Chinese entity mention over a full descriptive noun phrase;
- retain a participant only when it belongs to the current event or its direct causal/implementation chain;
- discover event clusters before role extraction;
- attach every role to one accepted event predicate before constructing that event's hyperedge;
- keep only relation-critical supporting events in the default cluster;
- give every retained supporting event its own 5W1H frame.

The source guide treats WHY primarily as cause rather than intended purpose. General Chinese 5W1H also uses motivation and purpose. CEH may retain cause, motivation, justification, or purpose under WHY, but only when that relation explains why the current intentional event occurred. A predicted consequence or desired result is not automatically WHY.

## Chinese-Specific Adaptation

Chinese extraction must handle phenomena that Spanish syntactic templates do not solve:

- topic-comment structure: the topic is not automatically WHO;
- omitted subjects: recover them only from explicit local context;
- local coreference: resolve `该系统`, `其`, `后者`, `该国`, and similar mentions before deduplication;
- serial verbs: ordered actions such as `先拆除，再安装` may express HOW without a method connector;
- implicit causality: adjacent events may express WHY without `因为` or `由于`;
- attribution shells: unwrap `据报道`, `表示`, and `称` when an embedded event is more central;
- noun-verb ambiguity: military units, projects, systems, and countries are WHO only when they participate in the current event.

Never translate Spanish cue lists into Chinese regexes. Use the source data to calibrate sparsity, span discipline, participant functions, and role attachment.

## Root-Predicate Attachment Test

For each candidate span `C`, restate the current event as `E = actor + predicate + object/result`, then ask the role question about that exact predicate.

```text
WHO:   who participates in E?
WHAT:  what action/state is E?
WHEN:  when does E occur or hold?
WHERE: where does E occur or apply?
WHY:   what proposition explains E?
HOW:   what proposition realizes E?
```

If `C` answers a neighboring predicate instead, reject it from the root frame even when its local label would be valid in a sentence-level annotation.

Example:

```text
周三，市政府批准新防洪工程。施工单位将分三期加固堤坝。

root E: 市政府批准新防洪工程
HOW for E: missing
reason: 分三期加固堤坝 is HOW for a later construction event, not HOW for the approval.
```
