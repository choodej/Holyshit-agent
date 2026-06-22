# registry skeleton-first checklist

Keep this checklist in sync with `manifest.json`.

Current phase: `slice-proven`

- [x] `skeleton` — organ folder, package files, manifest, and event/log shape exist
- [x] `contracts` — ports define the boundaries the domain needs
- [x] `harness-proof` — tests prove the first slice and can fail on regressions
- [x] `domain-logic` — pure domain behavior handles success, duplicate, and reject paths
- [x] `adapters` — JSONL repository/logger and inbound adapters are wired through ports
- [x] `workflow` — demo and Telegram composition roots run through the same service
- [ ] `optimization` — only add caching/token tuning after the slice stays proven
- [x] `slice-proven` — tests pass, demo runs, graphify strict is clean
