# Cluster And Event Selection Policy

## Contents

- Cluster-first principle
- Cluster boundary tests
- Event admission and merge tests
- Central-event selection
- Anti-fragmentation limits

## Cluster-First Principle

Discover event clusters before extracting 5W1H. A cluster groups events that form one coherent report topic, causal chain, policy chain, implementation chain, confrontation, or inventory/status family.

Do not derive clusters from punctuation alone.

```text
same paragraph != necessarily same cluster
same sentence  != necessarily same event
same named entity != sufficient cluster relation
```

## Cluster Boundary Tests

Place two candidate events in the same cluster only when at least one condition holds:

- one discloses, supports, motivates, causes, enables, contrasts with, is part of, or provides background for the other;
- both are indispensable components of one central status, project, decision, or incident;
- both answer different stages of one coherent event chain;
- a reader needs both to understand the same central event.

Split them into different clusters when:

- they are independent news briefs pasted together;
- they share only a country, organization, weapon class, or broad topic;
- their actors, predicates, and outcomes form separate narratives;
- connecting them would require world knowledge rather than source evidence.

## Event Admission Test

Promote a candidate to an event only when all are true:

1. It has a distinct predicate or state.
2. It expresses an independently useful fact.
3. It has exact textual evidence.
4. It belongs to a cluster by an evidence-backed relation.
5. It can support at least a trustworthy WHAT node and normally a WHO or another argument.

Reject or merge:

- repeated formulations of the same proposition;
- aliases, pronouns, or restatements;
- pure quantities and specifications;
- lists of components that only elaborate one inventory state;
- claimed consequences that merely paraphrase the central event;
- supporting details whose removal does not alter the event chain.

## Merge Test

Merge candidates `A` and `B` into one event when:

- they share the same actor, predicate, object, and time;
- one only adds a quantity, model, feature, or example;
- they would receive nearly identical 5W1H nodes;
- their difference is wording rather than proposition.

Keep them separate when:

- they have different predicates;
- they occur at different stages or times;
- one causes, motivates, enables, discloses, supports, or contrasts with the other;
- separate hyperedges improve retrieval or reasoning.

## Central Event

Select exactly one central event per cluster. Score candidates by:

```text
centrality =
  lead_or_summary_salience
  + relation_degree
  + explanation_power
  + evidence_density
  - side_detail_penalty
  - attribution_shell_penalty
```

The central event should organize the cluster. A supporting event may be factually important without being central.

Treat `表示`, `称`, `报道`, `透露`, or `发布` as an attribution shell when a stronger embedded event explains the cluster. Keep the reporting/disclosure event when the publication, accusation, warning, or announcement itself is the essential event and links several disclosed facts.

## Anti-Fragmentation Limits

Typical:

```text
1-3 clusters per record
1 central + 0-2 supporting events per cluster
```

Hard default maximum:

```text
5 events per cluster
```

More than three events requires a short internal justification based on distinct predicates and relations. Do not expose that scratch justification unless asked.

Numerical procurement breakdowns, equipment characteristics, and ranked supplier lists usually remain evidence for one state event. They become separate events only when the source gives them an independent action, decision, deployment, or consequence.

## Final Cluster Audit

Before 5W1H extraction, ask:

1. Would two clusters still make sense if all entity names were replaced with placeholders?
2. Does every supporting event have a useful relation to the central event?
3. Are any events duplicates with different span boundaries?
4. Did a numerical detail become an event without a distinct predicate?
5. Did one pasted record contain unrelated briefs that must be separated?

Repair cluster structure before extracting nodes. Role extraction cannot rescue a bad event decomposition.
