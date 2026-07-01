# ANTI_DRIFT_EXAMPLES.md

Examples for keeping AI work small, proven, and finishable.

## Doc Contract

- **Scope:** examples for agents and beginners working in this repo
- **Authority:** guide only; canonical rules remain in `.claude/skills/organ-kit/reference/RULES.md`
- **Enforcement:** `python tools/check.py` includes doc lint, manifest validation, tests, graphify, and generated graph drift checks
- **Example:** each case below shows a drifting path and a corrected path
- **Failure mode:** AI builds impressive but unproven work, creates duplicate rules, or treats learning notes as implementation

## หลงทาง

**เริ่มจากของใหญ่ก่อน proof**

ผิด:

```text
Build dashboard + database + queue + AI router first, then add tests later.
```

ผลเสีย: โปรเจคบวมเร็ว แต่ยังตอบไม่ได้ว่าผู้ใช้ทำอะไรได้ 1 อย่างและพิสูจน์ยังไง.

ถูก:

```text
input -> domain decision -> saved/logged result -> test/demo proof
```

ทำ slice เล็กก่อน เช่น register command -> validate duplicate -> save JSONL -> test passes.

**สร้างกฎใหม่ใน doc ใหม่โดยไม่ชี้ canonical**

ผิด:

```text
Create NEW_RULES.md with a rewritten skeleton-first policy.
```

ผลเสีย: rule drift เพราะมีหลายฉบับให้ AI เลือกเอง.

ถูก:

```text
State scope/authority, then point to RULES.md §8 or §9.
```

เอกสารใหม่ควร explain, route, หรือ specialize เท่านั้น ไม่เป็น source of truth เงียบๆ.

**ต่อ external write โดยไม่เห็นใน manifest**

ผิด:

```text
Add ClickUp/Sheets/DB write code directly in an adapter and skip manifest updates.
```

ผลเสีย: graphify มองไม่เห็น risk path และ agent อาจเขียนของจริงโดยไม่ผ่าน gate.

ถูก:

```json
{
  "external_writes": ["provider.operation"],
  "safety_gate": true
}
```

เขียนผ่าน `sandbox/shared/safety.py` และให้ manifest เปิดเผย write path.

**ยิง external API ตรงใน adapter**

ผิด:

```python
requests.post("https://api.example.com/tasks", json=payload)
```

ผลเสีย: SafetyGate และ manifest มองไม่เห็น write path; dry-run/approval ถูกข้าม.

ถูก:

```python
intent = WriteIntent(action="provider.create_task", target="tasks", payload=payload)
result = self.guarded(intent, lambda: self._post(intent))
```

แล้วประกาศใน `manifest.json`:

```json
{
  "external_writes": ["provider.create_task"],
  "safety_gate": true
}
```

**นับ spike ว่าเสร็จ**

ผิด:

```text
Temporary script found the API shape, so mark the organ done and promote it.
```

ผลเสีย: learning-done หลุดเข้า runtime แล้วพังตอนต่อกับงานจริง.

ถูก:

```text
Record learning in DEFERRED.md, delete the spike, or rebuild it in the right phase.
```

เฉพาะ implementation-done เท่านั้นที่ promote ได้ ตาม `RULES.md` §9.

**แก้ graph ด้วยมือ**

ผิด:

```text
Edit CATALOG.md so it looks correct.
```

ผลเสีย: graph กลายเป็นของตกแต่งและ drift จาก manifest.

ถูก:

```bash
cd sandbox
python tools/check.py
```

ให้ `graphify.py` generate graph จาก manifest เท่านั้น.

**เลือก feature หรือ production path แทนเจ้าของงาน**

ผิด:

```text
Goal is vague, so build auth + billing + production database first.
```

ผลเสีย: AI เลือกเป้าหมายจริงแทนคน และอาจผูกงานเข้ากับ secret/production ก่อนมี proof.

ถูก:

```text
Decision point: first production-facing slice

A. Smallest local proof — safest
B. Reversible spike — fastest learning
C. Full production path — only after approval
D. Shadow preview — map risk without writing

Recommended: A
Why: proves value before touching production/auth/secrets.
```

ใช้ `RULES.md` §10 ก่อนตัดสินใจใหญ่ทุกครั้ง.

**ไล่ phase เพราะเอกสารดูพร้อม**

ผิด:

```text
Phase 2 checklist exists, release note exists, and graph is clean, so start Phase 3.
```

ผลเสีย: control plane เดินหน้า แต่ runtime artifact chain ยังอาจพิสูจน์ไม่ได้
ว่า input ไหนเข้ามา, domain ตัดสินใจอะไร, save/log อะไร, และ command ไหนยืนยันผล.

ถูก:

```text
Capability Reality Check:
- current runtime state: demo/test command that passes
- artifact chain: input -> domain decision -> saved/logged result -> proof
- future intent: docs/phase notes not yet implemented
- blocker: deferred items that prevent implementation-done
```

ถ้าของจริงยังไม่ตามเอกสาร ให้ลด scope กลับไป proof เล็กสุดตาม `RULES.md` §9
ก่อนเพิ่ม phase/release/promote.

## ถูกทาง

ก่อนบอกว่างานเสร็จ ให้ผ่านประตูเดียวนี้:

```bash
cd sandbox
python tools/check.py
```

ถ้าประตูนี้ไม่ผ่าน งานยังไม่ใช่ implementation-done. ลด scope, แก้ proof, หรือบันทึกเป็น deferred แทนการขยายโปรเจค.
