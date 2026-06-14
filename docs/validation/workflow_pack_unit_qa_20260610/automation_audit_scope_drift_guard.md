# Automation Audit Scope Drift Guard — 2026-06-11

## Why this guard exists

During a broad VN project automation-level audit, the work drifted into a named-character focus (`Serena`) because a unit was labeled `title-specific heroine char_base` and the active project had rich Serena character/asset history. This produced useful migration evidence, but it was not aligned with the user's broader intent: validate automation/workflow maturity across the system, not optimize a specific character.

This document records the root cause and prevention rules for future VN titles.

## Exact drift chain

```text
User goal:
VN 프로젝트 자동화 수준을 넓게 점검

Intermediate unit name:
Unit 9D — title-specific heroine char_base prompt research

Agent interpretation:
active title heroine = Serena

Tool path:
search Obsidian Characters/Assets → find Serena approved base → inspect metadata → regenerate same-seed verification candidate → write Serena-specific notes

Problem:
The unit became character/asset-specific instead of workflow/system coverage-specific.
```

## Root causes

### 1. Unit naming created a production cue

`title-specific heroine` implies a specific protagonist. In an active title with known characters, this strongly pulls the task into character production.

Safer names:

```text
char_base runner coverage audit
char_base metadata handoff/migration check
character workflow automation coverage
approved-metadata fixture compatibility
```

Avoid in broad audit mode:

```text
title-specific heroine
Serena/Lucian character improvement
scene-specific event CG polish
approved asset refinement
```

### 2. Retrieval found high-signal character docs

Obsidian had detailed `Characters/serena.md` and `Assets/serena_char_base_candidates.md`, so retrieval naturally supplied concrete production context. That context was valid but too specific for broad audit mode.

Rule: retrieval in audit mode should classify named-character docs as **fixtures** unless the user requested character production.

### 3. Existing approved asset made the work feel operationally useful

Finding an approved Serena base revealed a real migration issue after `medium_breasts` moved from wrapper to `body_shape`. This made the side path appear valuable.

Rule: useful migration checks are allowed, but they must remain metadata/compatibility checks. Do not continue into visual optimization or replacement.

### 4. Success criteria were not restated after scope narrowing

The correct success criterion was workflow coverage, e.g. runner contracts, metadata shape, fail-closed gates. The actual local success criterion became Serena identity preservation.

Rule: whenever a named character enters an automation audit, restate the success criterion as a system property, not a character quality property.

## Audit-mode classification

Before generating or editing anything involving a named character/scene/asset, classify the action.

### Allowed as fixture/reference

```text
- inspect existing metadata shape
- verify approved seed/source handoff fields exist
- run prepare-only using existing prompt slots
- confirm runner validates prompt slots/taxonomy/fail-closed behavior
- test that generated candidate paths and metadata are recorded
- document migration rules for approved prompt semantics
- confirm approval gates prevent automatic replacement/promotion
```

### Not allowed without explicit user request

```text
- optimize a named character's face/outfit/body/expression
- generate multi-seed production candidates for a named character
- replace or promote an approved asset
- spend multiple iterations improving one character/scene
- write character-design conclusions as if they were workflow maturity results
```

## Pre-generation audit question

Before each generation in automation audit mode, answer:

```text
Is this generation proving workflow coverage, or improving a specific asset?
```

If it proves workflow coverage:

```text
- use neutral/generic fixture if possible
- keep batch minimal
- record runner/metadata/QA-gate evidence
- return to the coverage matrix
```

If it improves a specific asset:

```text
- stop
- ask for explicit confirmation or redirect to broad audit
```

## Safe fixture strategy

Prefer generic fixtures for broad coverage:

```text
sample_char_base_neutral_female
sample_char_base_neutral_male
sample_background_modern_classroom
sample_prop_ring
sample_prop_blank_document
sample_ui_alert_frame
sample_audio_sfx_door_knock
sample_audio_bgm_minor_waltz
```

Use title assets only when the workflow requires an existing approved source, e.g. scene_event_cg handoff:

```text
approved_char_base_metadata as read-only fixture
approved seed/source metadata as handoff input
no replacement, no promotion, no design iteration
```

## Coverage matrix to prefer over character focus

For each workflow, audit:

```text
- README/contract exists
- canonical API workflow exists
- runner exists or missing-runner gap is recorded
- prompt_slots schema is clear
- taxonomy validation path is live
- prepare-only works
- smoke generation works or blocker is explicit
- output path and metadata path are recorded
- candidate copy path is stable
- QA status is separate from promotion status
- approval gate is enforced
- failure modes fail closed
- cross-title portability assumptions are documented
```

## Recovery rule when drift is detected

If drift is detected mid-run:

```text
1. Stop generation/optimization for the named asset.
2. Mark any generated output as verification artifact only.
3. Do not promote or replace production files.
4. Write the narrow finding as a workflow lesson only if useful.
5. Return to the broad coverage matrix.
6. Update the task list to cancel character-specific follow-up unless explicitly requested.
```

## Lessons from the Serena incident

Valid system lesson:

```text
When a runner policy changes, approved prompt semantics may need explicit prompt-slot migration. Regenerated outputs are compatibility artifacts, not approved replacements.
```

Invalid future behavior:

```text
Using an automation audit as a reason to continue Serena-specific sprite/expression/event-CG production without explicit user request.
```

## Short guardrail phrase

Use this as a mental check during future titles:

```text
Automation audit measures the machine, not the heroine.
```
