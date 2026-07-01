# organ-kit — rules & rationale

Neutralized from a real build. Each rule fixes a concrete failure mode and is
written so it stays cheap (no bloat, no slowdown).

## 0. First-button rule: define the proof before code
**Why:** beginners often start by copying folders, choosing infrastructure, or
asking an AI to "build the system" before the job has a testable shape. That is
how projects become impressive but useless.

Before coding, define:
- **public-good purpose:** who benefits, in one sentence
- **smallest useful slice:** one action a real user can complete
- **input:** what the slice receives
- **domain decision:** what the core must decide without external I/O
- **output:** what is saved or logged
- **success criteria:** a test/demo command that proves the slice works

If any of these are unclear, ask until the brief is complete enough that the
agent does not need to guess. A beginner does not need to know what details to
provide; the agent must collect the missing brief proactively.

Start with a plain-language explanation before asking. Use comparisons a
non-programmer can understand, such as:
- **brief = ใบสั่งงาน** before a builder starts,
- **first slice = กระดุมเม็ดแรก** that keeps the shirt aligned,
- **proof gate = จุดตรวจงาน** before saying "done",
- **organ = ชิ้นงาน/module** that can later connect to other pieces.

Keep the intake small:
- desired result,
- who uses it,
- first action they should be able to complete,
- input needed for that action,
- what should be saved/logged,
- constraints or "must not" rules,
- external write / production / secret / auth risk,
- proof command or demo that would count as success.

Ask in short rounds (about 3-5 questions at a time). After each answer, say what
is still missing instead of inventing it. When the brief is complete, summarize
it back in plain language and ask for confirmation before coding.

If there are several valid slices, return the options and mark one recommended
path. Do not silently choose.

Good first slice:
`submit request -> validate/decide category -> save JSONL record -> emit audit log`

Bad first slice:
`build the full platform with dashboard, AI, database, automation, and deploy`

## 1. sandbox / project separation
**Why:** designing big and stuffing everything into one place becomes
uncontrollable. Prove organs in `sandbox/`; only finished, ready organs move to
`project/`. The two never mix.

## 2. OOP + Hexagonal, but only at the boundary
**Why:** forcing OOP and an adapter onto *every* line is itself bloat. The win
comes from one rule: **domain talks to the outside only through `ports/`
(interfaces); real I/O lives in `adapters/`.** Inside domain, write plain code.
- Downside if over-applied: indirection everywhere, slower to read. So bound it.

## 3. Organs connect only through contracts
**Why:** when something breaks you repair one organ without a chain reaction.
No organ imports another organ's internals — only its published interface/adapter.

## 4. Safe but not slow — tiered "ask before create"
Don't ask on every action (that contradicts "be on time"). Tier it:
- **Auto-proceed:** reversible, new, non-conflicting work.
- **Ask first (return choices + a recommendation):** overwrite/delete, duplicate
  id, duplicate name, anything touching multiple organs.

The code expresses this with a `Result` that can be `OK`, `NEEDS_DECISION`
(carries choices), or `REJECTED`. Risky paths return `NEEDS_DECISION` instead of
acting.

## 5. Logs local, summaries external
**Why:** ClickUp/Sheets are not log stores — slow, rate-limited, not queryable.
Raw logs go to local JSONL (fast). A separate decorator adapter forwards only
*reportable* events (e.g. "created") to ClickUp. Swap it in without touching domain.
That outbound summary is still an external write, so it must follow rule 7.
- Downside avoided: one slow external call per log line dragging the whole system.

## 6. Auto-generated catalog (graphify)
**Why a graph helps:** in a multi-organ/multi-repo system you need a dependency
map + index to find things fast and avoid duplicate work.
**Its real downsides:** hand-maintained graphs go stale and become a second thing
to maintain. **Fix:** generate it from `manifest.json` contract files only, in
one command (or CI). The manifest is the source for the graph; it must stay
synced with code. `tools/validate_manifests.py` catches the cheap, important
drift cases before graphify runs.
`tools/graphify.py` also flags **shadows**: circular dependencies, two organs
owning the same data domain, dependencies on missing organs, and external writes
without a declared safety gate. Run with `--strict` to fail CI on any shadow.

## 7. Safety gates for external writes
**Why:** an agent should never silently hit a real database/API. Every external
write is described as a `WriteIntent` and routed through a `SafetyGate`
(`shared/safety.py`). `PolicyGate` auto-approves reversible work and requires
explicit approval for irreversible work; `DryRunGate` previews and never writes.
Blocked writes return `Result.NEEDS_DECISION`, reusing the same ask-before-create
contract — no parallel concept.
- Bounded, not bloated: enforced by a small `ExternalWriteAdapter` base class +
  convention, not a heavy framework.

## 8. Skeleton-first build order (bone before tissue)
**Why:** the classic failure is building "tissue" (real adapters, UI, deep
workflow logic) before the "bone" (contracts and a proof) exists — so the proof
never comes and the design ossifies around accidental choices.

**Scope: this order applies _within one organ_, not as a global gate across the
whole system.** At the system level you still build a thin **vertical slice**
first (rule below) — one path cut through every layer — then widen. The two are
not in conflict: the slice decides _which_ organ to build next; this rule
decides the _order inside_ that organ.

Default order inside an organ:
1. skeleton — minimal class/object shells, manifest, audit/event schema
2. contracts — the `ports/` (ABC interfaces) the domain needs
3. harness proof — a test that **fails first**, pinning the intended behavior
4. domain logic — make the failing test pass (pure, no I/O)
5. adapters — real I/O behind the ports (DB, API, Telegram, ...)
6. UI / workflow detail
7. optimization (incl. token compression, caching)

**Rule, not a straitjacket:** a task that lands in a later step before an
earlier one is finished is **deferred by default** — mark it deferred, note why,
and return to the missing bone first. It is *not* "invalid". Throwaway spikes to
_learn_ a contract are allowed and encouraged; just discard them once the
contract is understood, then build it properly in order. Deep adapter logic
before its port + a failing test exist is the one hard "no".

("Models" is intentionally not a numbered step: domain models are bone and live
in step 1/4; serving an ML model is tissue and lives in step 5+.)

Each organ tracks this order in two places:
- `CHECKLIST.md` — the human checklist to follow while building
- `manifest.json.phase` — the machine-readable phase that graphify reports

## 9. Two-tier Definition of Done
**Why:** a spike can teach the right contract without being production-ready.
Treating that as "done" is how throwaway discoveries leak into real systems.

Use two explicit done states:

- **learning-done:** the question is answered, the contract is clearer, or the
  risky unknown is reduced. Spikes, notes, screenshots, and temporary scripts can
  qualify. This does **not** mean the organ is ready to promote.
- **implementation-done:** the organ's current slice is built in order, tests
  pass, demo runs, `graphify --strict` is clean, external writes are guarded, and
  `CHECKLIST.md` plus `manifest.json.phase` agree.

Only **implementation-done** work can move from `sandbox/` to `project/`.
Learning-done work must either be deleted after it teaches the contract, turned
into implementation work in the right phase, or recorded in the organ's
`DEFERRED.md`.

Every organ keeps a local `DEFERRED.md` beside `CHECKLIST.md`. Use it only for
work intentionally delayed because it belongs to a later phase or needs a real
trigger. Do not use it as a general wishlist.

Before adding a phase, release ceremony, promotion note, or "done" claim, run a
**Capability Reality Check**. This catches the same failure mode people may call
control-plane drift, process overhang, spec-implementation skew, ceremony ahead
of capability, or phase chasing: the docs/gates/phase labels move faster than
the artifact chain that actually runs.

Reality check questions:
- What is the current runtime state, and which command proves it?
- What exact artifact chain exists now: input -> domain decision ->
  saved/logged result -> proof?
- Which docs or phase labels describe future intent rather than current
  capability?
- Which checklist/deferred items block implementation-done or promotion?
- Does `python tools/check.py` prove the claim, or only prove the control plane?

If the artifact chain is not proven, do not add another phase to chase. Mark the
work as learning-done or deferred, reduce the slice, and return to the missing
runtime proof.

Before reporting success, do one final review loop:
- compare the final diff against the user's original request and confirmed brief,
- check for unintended files, scope creep, duplicate rules, and manual graph edits,
- run the proof gate (`python tools/check.py`) and fix anything it catches,
- if anything remains incomplete, say so plainly instead of calling it done.

Do not send the final result as "complete" until this review is clean or the
remaining blocker is explicitly reported.

## 10. Human Decision Gate
**Why:** code guards catch drift after work starts, but the most expensive drift
happens before coding: the agent chooses the wrong goal, wrong feature, wrong
write path, or treats learning as runtime approval. That choice belongs to the
human.

Pause and ask before acting when any of these are true:
- the real project goal or user benefit is unclear,
- several features or first slices could reasonably come first,
- the path touches external writes, production, secrets, auth, billing, or real
  user/customer data,
- learning-done work might be promoted, deleted, deferred, or rebuilt,
- UX, business, legal, or security context would change the correct answer.

Use this format:

```text
Decision point: <what must be decided>

Plain-language frame: <one sentence using a beginner-friendly comparison>

A. <safest/smallest proof> — best when...
B. <fastest reversible spike> — best when...
C. <fuller implementation> — best when...
D. <defer / shadow preview / read-only mapping> — best when...

Recommended: <A/B/C/D>
Why: <reason + tradeoff>
Anti-drift proof: <how this choice avoids guessing, bloat, or hidden risk>
```

Do not ask four choices for small reversible implementation details, formatting,
or code style when the user's goal is already clear. If the user already chose a
path and no new trigger appears, continue. If a new trigger appears, stop again.

## What this kit deliberately does NOT do
- No mandatory message broker, no mandatory DB, no mandatory cloud. Start with
  files; add infrastructure only when an organ proves it needs it.
- No global "brain" until enough organs are individually proven. Build a thin
  end-to-end slice first, then widen.
