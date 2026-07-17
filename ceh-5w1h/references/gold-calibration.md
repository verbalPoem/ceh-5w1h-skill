# Gold Calibration And Research Basis

Use this reference to calibrate candidate counts, boundary decisions, and batch prompting. Adapt the principles; do not copy an English parser into Chinese text.

## Giveme5W1H Lessons

The Giveme5W1H paper defines main-event descriptors as concise: as short as possible while retaining all necessary event information. Its pipeline preprocesses text, generates candidates by question, and scores candidates to select the best answers.

Important transferable rules:

- describe the article's main event rather than every sentence;
- discard WHO noun phrases containing an embedded verb phrase because they become too long;
- rank WHO and WHAT jointly enough to ensure they describe the same action;
- prefer candidates near the headline/lead, but do not let position override semantic fit;
- return no WHY or HOW when confidence is below threshold instead of forcing a false positive;
- treat WHY and HOW as harder than the first four W roles.

Giveme5W1H's original implementation uses linguistic and domain rules because it is an English parser. Do not reproduce that mechanism as a keyword labeler inside an LLM skill. For this skill, use those rules only as historical candidate-generation ideas; assign WHY/HOW through proposition meaning and directed event relations.

Primary sources:

- Paper: https://arxiv.org/abs/1909.02766
- Repository and gold data: https://github.com/fhamborg/Giveme5W1H

## Gold-Set Shape

The public repository's `gold_standard/data` contains 96 annotated articles. A local audit of those files shows:

```text
WHO:  1-3 answers, mean 1.60 per article
WHAT: 1-3 answers, mean 1.41 per article
WHEN: usually 0-1; 15/96 articles have no answer
WHERE: usually 0-1; 24/96 articles have no answer
WHY: often 0-1; 14/96 articles have no textual answer
HOW: often 0-2; 11/96 articles have no textual answer
```

These are calibration signals, not hard Chinese-language limits. The key lesson is that a gold annotation is sparse and selective. It does not fill every available slot.

## LLM Prompting Evidence

The 2025 study `Imitating Human Reasoning to Extract 5W1H in News` compares zero-shot, few-shot, extractive reasoning, and question-level reasoning on the Giveme5W1H data. Its findings support:

- filter body sentences that do not directly support the main event;
- reason separately for each role;
- reason over the semantic relation between the candidate proposition and the main-event proposition, including relations with no explicit connector;
- use extractive reasoning for difficult causal selection;
- use question-level reasoning for role boundaries;
- expect HOW to remain the hardest role and allow empty answers.

Primary sources:

- Paper: https://doi.org/10.1145/3701716.3715532
- Reproducible prompts: https://github.com/cmunhozc/5W1H-prompt-strategies

## CEH Adaptation

CEH-5W1H differs from Giveme5W1H because it also builds an event hyperedge and may retain multiple indispensable participants. Preserve that contribution while keeping gold-style selectivity:

```text
one central event per cluster plus only relation-critical supporting events
+ minimal role spans
+ exact offsets
+ participant completeness when justified
+ semantic validation
= one auditable event hyperedge
```

Do not claim direct benchmark comparability between English Giveme5W1H and Chinese CMNEE-style text without a manually annotated Chinese test set.

## Spanish Cross-Lingual Calibration

The local FLARES Spanish train and trial data add a second calibration source: 1,753 labeled records with 7,485 exact-span tags. WHAT appears in 86.4% of records, while WHY appears in 12.5% and HOW in 28.3%. This supports sparse optional roles and exact offsets, but not Spanish cue-word transfer.

The official guide anchors each question to the main verb, allows multiple event participants, and scores reliability per answer span using objectivity and precision. CEH adapts those ideas while deliberately collapsing repeated aliases, discovering event clusters first, and attaching each 5W1H frame to one accepted event predicate. See `cross-lingual-calibration.md` and `reliability.md`.
