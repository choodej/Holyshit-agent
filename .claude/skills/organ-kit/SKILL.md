---
name: organ-kit
description: Help beginners start a project/task with the right first button, then scaffold and grow an "organ-based" backend: independent, testable modules ("organs") in clean OOP/Hexagonal style connected only through adapters. Use when the user wants rules/skills for project foundations, needs a new module/service/"department"/"organ", wants to set up this architecture in any project, or asks for a safe scaffold with ask-before-create guards, local JSONL logging, and an auto-generated dependency catalog. Language-agnostic in spirit; ships a Python generator.
---

# organ-kit

A small, neutral kit for building systems out of **organs**: each organ is an
independent unit you can build, test, and repair on its own, then connect to the
rest through adapters. Designed so a big system stays controllable instead of
turning into one tangled blob.

Its first job is simpler than architecture: help a beginner button the first
button correctly. Before writing code, reduce the project to one user-visible
slice with a testable success criterion.

ใช้ภาษาไทยกับผู้ใช้ได้ แต่ไฟล์ที่ generate เป็นกลาง ใช้ได้ทุกโปรเจค

## When to use
- User asks for beginner rules / a project-starting skill / "first button"
  guidance before building.
- User asks to add a new organ / module / "department" / service.
- User wants to set up the organ architecture in a fresh or existing project.
- User wants a scaffold that already runs and passes a smoke test.

## Core rules (read `reference/RULES.md` for the why)
0. **First-button rule:** if the purpose, smallest useful slice, or pass/fail
   proof is unclear, ask before coding. The first slice must fit this shape:
   input -> domain decision -> saved/logged result -> test/demo proves it.
1. **Separate `sandbox/` from `project/`.** Prove an organ in sandbox first;
   promote to project only when complete.
2. **Every organ is OOP + Hexagonal:** pure `domain/` talks to the world only
   through `ports/` (interfaces); real I/O lives in `adapters/`. Swap or fix one
   adapter without touching domain.
3. **Organs connect only via contracts/adapters** — never reach inside each other.
4. **Safe but not slow:** reversible work proceeds; risky work (overwrite,
   duplicate id, duplicate name, cross-organ impact) must return *choices* for a
   human to decide — never create-over silently. Always mark a recommended choice.
5. **Real logs are local JSONL** (fast, queryable). External tools (ClickUp,
   Sheets) receive only *summaries* through a separate adapter — never raw logs.
6. **The catalog/graph is auto-generated from code only** (`tools/graphify.py`),
   which also detects "shadows" (circular deps, data-domain overlaps, dangling
   deps, unguarded external writes). Never hand-write it, so it can never drift.
7. **Every external write goes through a `SafetyGate`** (`shared/safety.py`):
   dry-run preview + explicit approval; reversible work auto-approves.
8. **Skeleton-first + deferred work:** follow `reference/RULES.md` §8.
9. **Two-tier DoD:** `learning-done` is not `implementation-done`; follow
   `reference/RULES.md` §9.

## Built-in framework features
- **Hexagonal OOP** scaffolding for every organ.
- **Graphify** auto-mapping + shadow detection (`tools/graphify.py`, Mermaid output).
- **Token optimization** for agent context/state (`tools/token_compressor.py`) —
  never applied to the canonical audit log.
- **Safety gates** for human-in-the-loop external writes (`shared/safety.py`).

## Agent handoff state
Use `tools/token_compressor.py` after a slice has run and before passing context
to another agent. Compress a copy of the state or event digest only. Never
compress the canonical JSONL audit log.

## How to create a new organ

Prefer the deterministic generator (works with or without me):

```bash
python3 .claude/skills/organ-kit/scripts/new_organ.py <organ_name> \
    --title "Human title" --dir sandbox/organs
```

It will:
- refuse if the organ already exists (rule 4 — ask before create),
- ensure `manifest.schema.json` exists at the sandbox root,
- ensure `shared/` and `tools/` exist (created once, never overwritten),
- stamp out a self-contained organ: `domain/ ports/ adapters/ tests/ app.py manifest.json`,
- include `CHECKLIST.md` so skeleton-first is an artifact, not prose only,
- leave you an organ that **already runs and passes its smoke test**.

Then:
```bash
cd sandbox
python3 -m pytest organs/<organ_name>/tests -q    # should pass immediately
python3 organs/<organ_name>/app.py --demo         # see the slice run
python tools/check.py                             # full proof gate
```

## What I (Claude) should do when asked to start a project
1. Restate the public-good purpose in one sentence.
2. Ask only for missing critical facts. If there are multiple valid directions,
   list them plainly and mark one recommended path.
3. Define the first slice before scaffolding:
   - user-visible action,
   - input,
   - domain decision,
   - persisted/logged output,
   - success criteria as a test/demo command.
4. Create the smallest organ that proves that slice. Do not add a "brain",
   database, queue, dashboard, or optimization until the slice passes.
5. Run the demo and `python tools/check.py`. If anything fails, keep looping on
   that success criterion before widening scope.

## Manifest contract
Read `reference/MANIFEST.md` before hand-editing any `manifest.json`.
`graphify.py` uses `depends_on`, `owns_data`, `external_writes`, and
`safety_gate` for shadow detection, and reports `phase` as the organ's
skeleton-first progress marker. Keep each organ's `CHECKLIST.md` and
`manifest.json` phase in sync. Run `python tools/check.py` so
schema/checklist drift fails before catalog generation.

## What I (Claude) should do when asked to add an organ
1. Confirm the organ name + one-line purpose (ask if unclear — one question at a time).
2. Run the generator. Do **not** hand-write the scaffold.
3. Fill in the real domain logic inside `domain/service.py` only; keep ports/adapters thin.
4. Run `python tools/check.py`.
5. Report results plainly (tests passing/failing as they are).

## Distributing this skill
Copy `.claude/skills/organ-kit/` into any repo's `.claude/skills/`. It is
project-agnostic: no hard-coded tokens, names, or paths. Telegram/ClickUp
adapters are optional plug-ins, not requirements.
