# Organ Manifest Schema

Every organ has `manifest.json`. `graphify.py` reads these files to build
`CATALOG.md`, `graph.json`, `graph.mmd`, and to detect shadows.

Use `sandbox/manifest.schema.json` for editor help. In an organ manifest, set:

```json
{
  "$schema": "../../manifest.schema.json"
}
```

## Required Fields

| Field | Type | Used by graphify | Meaning |
|---|---:|---|---|
| `organ` | string | yes | Stable id. Must match the organ folder name. |
| `title` | string | yes | Human-readable name. |
| `version` | string | yes | Organ version. |
| `language` | string | no | Main implementation language. |
| `phase` | enum | yes | Current skeleton-first phase; graphify reports this. |
| `status` | string | yes | Free-form lifecycle note. Do not use it for graph/reporting. |
| `purpose` | string | yes | One-sentence user-visible job this organ owns. |
| `ports` | string[] | yes | Port/interface names. |
| `adapters` | object | yes | Map each port to concrete adapter ids for the Mermaid graph. |
| `exposes` | string[] | no | Published contract signatures other organs may call. |
| `depends_on` | string[] | yes | Other organ ids this organ depends on. |
| `owns_data` | string[] | yes | Canonical data domains/files this organ owns. |

## Optional Fields

| Field | Type | Used by graphify | Meaning |
|---|---:|---|---|
| `external_writes` | string[] | yes | External write operations, such as `clickup.create_task`. |
| `safety_gate` | boolean | yes | Must be `true` when `external_writes` is non-empty. |

## Shadow Detection Contract

`python3 tools/graphify.py --strict` checks:

- `depends_on`: circular dependencies and missing organs
- `owns_data`: two organs claiming the same data domain, case-insensitive
- `external_writes` + `safety_gate`: external writes without a safety gate

If an organ writes to an external API/database/third-party service, declare both:

```json
{
  "external_writes": ["provider.operation"],
  "safety_gate": true
}
```

If an organ has no external writes, omit `external_writes` or set it to `[]`.

## Phase Contract

`phase` is the machine-readable skeleton-first progress marker. Use exactly one:

| Phase | Done when |
|---|---|
| `skeleton` | Folder, package files, manifest, and event/log shape exist. |
| `contracts` | Ports/interfaces define the boundary the domain needs. |
| `harness-proof` | A test/demo proves the scaffold wiring and can fail on regressions. |
| `domain-logic` | Pure domain behavior implements the real decision without I/O. |
| `adapters` | Real I/O sits behind ports and external writes are declared. |
| `workflow` | The user-facing flow runs through the same service. |
| `optimization` | Caching/token/state tuning is being added after proof. |
| `slice-proven` | Tests pass, demo runs, and `graphify --strict` is clean. |

Every organ should also keep a `CHECKLIST.md` beside `manifest.json`. Update
both files together: the checklist is the human artifact; `phase` is what
`graphify` reports.

## Minimal Example

```json
{
  "$schema": "../../manifest.schema.json",
  "organ": "registry",
  "title": "Registration",
  "version": "0.1.0",
  "language": "python",
  "phase": "slice-proven",
  "status": "slice-proven",
  "purpose": "Register a member, reject invalid names, and log the result.",
  "ports": ["MemberRepository", "Logger", "Inbound"],
  "adapters": {
    "MemberRepository": ["jsonl_member_repo"],
    "Logger": ["jsonl_logger"],
    "Inbound": ["demo_inbound"]
  },
  "exposes": ["register(username, source) -> Result[Member]"],
  "depends_on": [],
  "owns_data": ["members.jsonl", "registry.log.jsonl"]
}
```
