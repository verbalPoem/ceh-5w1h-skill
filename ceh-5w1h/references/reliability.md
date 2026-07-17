# Evidence Status And Reliability

Do not use one field for two different judgments.

## Evidence Status

`Evidence_Status` describes how the role relation is supported by the local text:

```text
explicit  the answer and its relation to the current event are explicitly stated
implicit  the answer span is explicit, but its role relation is strongly implied by local discourse
converted the tag came from a legacy-format conversion and still needs semantic review
```

Evidence status does not say whether the statement is true, objective, or precise.

## Reliability Label

Emit `Reliability_Label` only when the user requests reliability analysis. It evaluates the linguistic presentation of that exact answer span using two dimensions:

```text
reliable            objective and precise
partially_reliable  objective but imprecise, or precise but subjective
unreliable          neither objective nor precise
```

Cross-lingual mapping from the Spanish calibration data:

```text
confiable      -> reliable
semiconfiable  -> partially_reliable
no confiable   -> unreliable
```

Assess meaning in context rather than matching a word list.

Objectivity risks include evaluative or emotional wording, author opinion, rhetorical framing, one-sided accusation, sarcasm, insult, and unsupported certainty.

Precision risks include unresolved pronouns, vague quantities, unspecified sources, uncertain modality, unclear dates or places, and descriptions that cannot identify the referent.

## Independence Examples

```text
项目预算被削减，团队只能暂停测试。
WHY span: 项目预算被削减
Evidence_Status: implicit
Reliability_Label: reliable
```

The causal relation is implicit, but the span itself is objective and precise.

```text
据说某些专家认为这个荒唐计划可能很快启动。
WHO span: 某些专家
Evidence_Status: explicit
Reliability_Label: partially_reliable
```

The participant relation is explicit, but the referent is vague and the surrounding presentation is subjective.

## Guardrails

- Judge the tag span in its local context, not the publisher's overall reputation.
- Do not fact-check through world knowledge unless the user explicitly requests external verification.
- A quote may be explicit evidence while still being subjective or imprecise.
- Do not downgrade an answer merely because its WHY/HOW relation is implicit.
- Do not upgrade vague information merely because a named source reported it.
- When uncertain between adjacent reliability values, use `partially_reliable` and flag the record for review.
