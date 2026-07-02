# Relation Vocabulary

Use these event-to-event relation types by default.

## Controlled Relations

- `discloses`: an announcement, report, document, briefing, or release reveals another event or state.
- `supports`: one event, fact, or evidence item supports another event or claim.
- `motivates`: a concern, goal, threat, or need drives another event.
- `causes`: one event directly causes another event or result.
- `part_of`: one event is a sub-event inside a larger event.
- `component_of`: one event/state is a component of a larger system, inventory, project, or cluster.
- `background_of`: one event provides context for another but is not the direct cause.
- `enables`: one event, capability, system, or method makes another event possible.
- `contrasts_with`: two events or claims are explicitly contrasted.

## Selection Rules

- Prefer `discloses` over vague reporting labels when a source releases details.
- Prefer `motivates` when a concern or purpose leads to an action.
- Prefer `background_of` when the relation is contextual but not causal.
- Prefer `component_of` for inventories, project parts, system components, and grouped status events.
- Use `supports` for evidence support, not for generic sequence.
- Use `causes` only for explicit causality.
- Use `part_of` when one event is contained inside a larger event.
- Use `enables` for capability, method, or infrastructure enabling an action.
- Use `contrasts_with` only when the text explicitly contrasts two claims or states.

## Avoid

- Do not use `reports`; use `discloses` when the relation is disclosure/reporting.
- Do not invent relation types in default mode.
- Do not connect every event pair. Add only relations useful for reading or graph construction.
