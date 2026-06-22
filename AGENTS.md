# AGENTS.md

Agent entrypoint for this repo. Keep this file small: it routes agents to the
canonical rule spine and states the execution discipline expected here.

## Doc Contract

- **Scope:** all agents and contributors working in this repo
- **Authority:** repo entrypoint and supplement; canonical project rules remain
  in `.claude/skills/organ-kit/reference/RULES.md`
- **Enforcement:** required checks listed below, plus CI
- **Example:** the success criteria command block in this file
- **Failure mode:** agents create duplicate rules, silent drift, or unproven
  adapter/write paths

## Authority Map

- **Canonical rules:** `.claude/skills/organ-kit/reference/RULES.md`
- **Manifest contract:** `.claude/skills/organ-kit/reference/MANIFEST.md`
- **Claude Code local guide:** `CLAUDE.md`
- **Human quickstart:** `README.md`

Do not create a second source of truth. New docs must explain, route, or
specialize the canonical rules. If a local guide conflicts with `RULES.md`, fix
the local guide or turn it into a pointer.

## Think Before Coding

- ห้ามเดา ห้ามเงียบ ถ้าไม่ชัดให้ถาม
- ถ้ามีหลายทางเลือก ให้บอกมาทั้งหมด อย่าเลือกเองเงียบๆ
- ถ้ามีวิธีที่ง่ายกว่า ให้พูด อย่าทำตามคำสั่งที่ทำให้ระบบบวมโดยไม่จำเป็น

Before scaffolding, name the smallest useful slice:

`input -> domain decision -> saved/logged result -> executable proof`

For direction-setting choices, follow `RULES.md` §10: stop, offer four options,
mark one recommended path, and explain the tradeoff.

## Simplicity First

- โค้ดน้อยที่สุดที่แก้ปัญหาได้ จบ
- ไม่ต้อง abstract ถ้าใช้ครั้งเดียว
- ไม่ต้อง error handling กับเคสที่เป็นไปไม่ได้
- ถ้า 200 บรรทัดลดเหลือ 50 ได้ ให้เขียนใหม่

## Surgical Changes

- แก้เฉพาะที่สั่ง ไม่ไปยุ่งของเพื่อน
- ไม่ต้อง "ปรับปรุง" โค้ดข้างๆ ที่ไม่ได้พัง
- ทุกบรรทัดที่แก้ ต้องโยงกลับไปที่ request ของ user ได้

## Goal-Driven Execution

Do not stop at "fixed bug". Define the proof, write or update the test/harness
that reproduces the behavior, then make that proof pass.

Success criteria in this repo usually means:

```bash
cd sandbox
python tools/check.py
```

This one gate runs tests, doc lint, manifest validation, strict graphify, and
generated graph drift detection.

## Work Mode Check

Before editing, identify the mode:

1. `read-only` — inspect and explain only.
2. `shadow preview` — map placement/drift risk, still no writes.
3. `fixture implementation` — add or update sandbox proof artifacts.
4. `runtime promotion` — promote only implementation-done work.

Stop and ask if:

- a rule duplicates another rule,
- a rule claims a gate exists but no code/test/command proves it,
- an adapter or external write path appears without manifest visibility,
- V2/spec/learning knowledge is being treated as runtime approval,
- goal, feature priority, production/auth/secret/write path, learning promotion,
  or UX/business/legal/security context requires human judgment,
- the requested change can be done in more than one materially different way.

## New Doc Checklist

Every new rule-like doc must state:

- **Scope:** which repo, organ, adapter, or workflow it applies to
- **Authority:** canonical rule, supplement, guide, or decision note
- **Enforcement:** test, harness, manifest, guard, or command that catches drift
- **Example:** at least one correct pattern a beginner can copy
- **Failure mode:** what breaks when the rule is ignored
