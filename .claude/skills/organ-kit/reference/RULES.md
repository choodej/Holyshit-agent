# organ-kit — rules & rationale

Neutralized from a real build. Each rule fixes a concrete failure mode and is
written so it stays cheap (no bloat, no slowdown).

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
- Downside avoided: one slow external call per log line dragging the whole system.

## 6. Auto-generated catalog (graphify)
**Why a graph helps:** in a multi-organ/multi-repo system you need a dependency
map + index to find things fast and avoid duplicate work.
**Its real downsides:** hand-maintained graphs go stale and become a second thing
to maintain. **Fix:** generate it from `manifest.json` files only, in one command
(or CI). The code is the single source of truth; the graph can never drift.

## What this kit deliberately does NOT do
- No mandatory message broker, no mandatory DB, no mandatory cloud. Start with
  files; add infrastructure only when an organ proves it needs it.
- No global "brain" until enough organs are individually proven. Build a thin
  end-to-end slice first, then widen.
