# CLAUDE.md

Project instructions for Claude Code.

## Mission

This repo is a beginner "first-button" project skill. Help users start useful
projects with a small, testable first slice before adding architecture.

## Before Coding

- Do not guess silently. If the purpose, user-visible slice, or proof is unclear,
  ask first.
- If a beginner describes only the desired result, explain the missing brief in
  plain language, use simple comparisons, and ask short rounds until no guessing
  is needed.
- If multiple valid paths exist, list the options and mark one recommended path.
- For major decision points, follow `.claude/skills/organ-kit/reference/RULES.md`
  §10: offer four options, recommend one, and explain the tradeoff.
- Define the first slice before scaffolding:
  input -> domain decision -> saved/logged result -> test/demo proof.
- Success criteria must be executable: tests pass, demo runs, and graphify is
  strict-clean. Before reporting success, run `python tools/check.py` from
  `sandbox/`.

## Organ Rules

- Keep new/prototype work in `sandbox/`; promote to `project/` only after it is
  complete and proven.
- Build organs as OOP/Hexagonal modules: pure `domain/`, interfaces in `ports/`,
  real I/O in `adapters/`.
- Organs must communicate through contracts/adapters, not by importing each
  other's internals.
- Use `.claude/skills/organ-kit/scripts/new_organ.py` to scaffold a new organ.
  Do not hand-write the scaffold.
- Keep `organs/<organ>/CHECKLIST.md` synced with `manifest.json.phase`.
  `status` can be a note, but `phase` is the graph/reporting field.
- Follow `.claude/skills/organ-kit/reference/RULES.md` §8 for skeleton-first,
  §9 for two-tier DoD, and §10 for human decision gates.
- External writes must go through `sandbox/shared/safety.py`.
- Keep raw logs local as JSONL. External tools get summaries through adapters.
- Use `sandbox/tools/token_compressor.py` only for next-agent context/state
  handoff after a slice runs. Never compress the canonical JSONL audit log.

## Generated Graph Contract

- Read `.claude/skills/organ-kit/reference/MANIFEST.md` before hand-editing any
  `manifest.json`.
- Use `sandbox/manifest.schema.json` as the manifest schema.
- Never hand-edit `sandbox/CATALOG.md`, `sandbox/graph.json`, or
  `sandbox/graph.mmd`.
- After manifest or organ changes, run:

```bash
cd sandbox
python tools/check.py
```

## Required Checks

Run these before reporting success:

```bash
cd sandbox
python tools/check.py
```

For repo-level agent discipline, read `AGENTS.md`. For detailed workflow rules,
read `.claude/skills/organ-kit/SKILL.md` and load
`.claude/skills/organ-kit/reference/RULES.md` when the reasoning behind a rule
matters.
