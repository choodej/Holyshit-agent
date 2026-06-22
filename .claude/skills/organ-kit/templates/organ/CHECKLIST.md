# {{ORGAN}} skeleton-first checklist

Keep this checklist in sync with `manifest.json`.

Current phase: `harness-proof`

- [x] `skeleton` — organ folder, package files, manifest, and event/log shape exist
- [x] `contracts` — ports define the boundaries the domain needs
- [x] `harness-proof` — generated smoke tests prove the scaffold wiring
- [ ] `domain-logic` — replace generic submit behavior with the real core decision
- [ ] `adapters` — keep real I/O behind ports and declare external writes in manifest
- [ ] `workflow` — add the real user flow only after domain behavior is proven
- [ ] `optimization` — only add caching/token tuning after the slice stays proven
- [ ] `slice-proven` — tests pass, demo runs, graphify strict is clean
