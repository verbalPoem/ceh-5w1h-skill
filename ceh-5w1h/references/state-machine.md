# CEH-5W1H Record-First Controller

Use this controller for every default extraction.

```text
S0_READ_RECORD
  -> S1_ROOT_EVENT
  -> S2_TAGS
  -> S3_DEDUP
  -> S4_VALIDATE
```

## S0_READ_RECORD

Process one source record at a time.

Inputs may be:

- one raw text block;
- one dataset object with `Id` and `Text`;
- one legacy CEH event cluster during conversion.

Do not merge unrelated records into one extraction unit.

## S1_ROOT_EVENT

Select exactly one root event by default.

Root event criteria:

- best explains the record;
- has a clear predicate/action/state;
- supports the most useful 5W1H roles;
- is not a sliding window fragment;
- is not merely a quantity, equipment feature, quote, or background detail.

Set:

```json
{
  "Event_Id": "E1",
  "Event_Text": "concise event summary",
  "Trigger": {
    "Tag_Text": "trigger",
    "Tag_Start": 0,
    "Tag_End": 0
  }
}
```

Use one root event unless the user explicitly asks for `full_detail=true`.

## S2_TAGS

Extract 5W1H spans only for the root event.

Role questions:

- WHO: actor, source, owner, participant, affected party.
- WHAT: central action, claim, status, system, object, or result.
- WHEN: event time, report time, validity/as-of time, deadline, plan time.
- WHERE: location, deployment site, affected area, base, platform, theater.
- WHY: cause, purpose, risk, motivation, concern.
- HOW: method, mechanism, capability, procedure, platform.

Each tag must use exact source offsets:

```json
{
  "Tag_Text": "source span",
  "Tag_Start": 0,
  "Tag_End": 0,
  "5W1H_Label": "WHO",
  "Reliability_Label": "direct"
}
```

## S3_DEDUP

Apply `references/deduplication.md` before output.

Default caps:

```text
WHO <= 2
WHAT <= 2
WHEN <= 1
WHERE <= 1
WHY <= 1
HOW <= 1
TOTAL TAGS <= 8
```

Prefer specific spans:

- keep "US Department of Defense" over "US";
- keep "E-2D Advanced Hawkeye aircraft" over "aircraft";
- keep "missile defense system" over "system".

## S4_VALIDATE

Check:

- `schema_version` is `ceh-record-v2`;
- each record has `Text`, `Root_Event`, `Tags`, `Missing`, and `Event_Hyperedge`;
- `Tag_Text == Text[Tag_Start:Tag_End]`;
- no duplicate `5W1H_Label + normalize(Tag_Text)` pairs;
- role caps are respected;
- each hyperedge index points to an existing tag of the matching role;
- missing roles are listed in uppercase.

Use:

```text
python ceh-5w1h/scripts/validate_ceh_record_output.py output.json
```

## Optional Global Index

Only when requested with `global_index=true`:

```text
S0_READ_RECORD
  -> S1_ROOT_EVENT
  -> S2_TAGS
  -> S3_DEDUP
  -> S4_VALIDATE
  -> S5_GLOBAL_INDEX
```

`S5_GLOBAL_INDEX` may project records into `sentences`, `nodes`, `events`, `event_hyperedges`, `relation_hyperedges`, and `event_clusters`, but it must not reintroduce duplicate nodes.
