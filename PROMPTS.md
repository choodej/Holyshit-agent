# PROMPTS.md

Copy-paste prompts for using this repo with Claude Code, Codex, or another AI
coding agent.

## Doc Contract

- **Scope:** beginner-friendly prompts for working inside this repo
- **Authority:** guide only; canonical rules remain in `.claude/skills/organ-kit/reference/RULES.md`
- **Enforcement:** `python tools/check.py` is the one proof gate
- **Example:** each section below is a prompt you can paste into an agent
- **Failure mode:** prompts become a second source of truth or skip `RULES.md` §10 decision gates

## วิธีใช้

1. เริ่มด้วย "Prompt ชุดใหญ่" ถ้าคุณอยากให้ AI คุมงานทั้งรอบ.
2. ใช้ prompt ย่อยเมื่องานแคบลง เช่น สร้าง organ, ใส่ domain logic, เพิ่ม adapter.
3. ถ้าเจอ decision ใหญ่ ให้ใช้ prompt Decision Gate ก่อนปล่อย AI ทำต่อ.
4. ก่อนบอกว่างานเสร็จ ต้องผ่าน:

```bash
cd sandbox
python tools/check.py
```

## Prompt ชุดใหญ่

```text
คุณกำลังทำงานใน repo นี้โดยต้องตาม framework organ-kit

อ่านก่อน:
- README.md
- AGENTS.md
- CLAUDE.md
- .claude/skills/organ-kit/SKILL.md
- .claude/skills/organ-kit/reference/RULES.md
- .claude/skills/organ-kit/reference/MANIFEST.md
- ANTI_DRIFT_EXAMPLES.md

กฎสำคัญ:
- RULES.md คือ canonical source of truth อย่าสร้างกฎฉบับใหม่
- ถ้าเป้าหมายจริง, feature priority, production/auth/secret/external write,
  learning-done promotion, หรือ UX/business/legal/security ยังไม่ชัด ให้หยุดถามตาม RULES.md §10
- เวลาถาม decision ใหญ่ ให้เสนอ 4 ทางเลือก A/B/C/D พร้อม recommended และเหตุผล/tradeoff
- เริ่มจาก smallest useful slice: input -> domain decision -> saved/logged result -> proof
- ใช้ generator เท่านั้นเมื่อสร้าง organ ใหม่
- ทำ skeleton-first ตาม RULES.md §8
- learning-done ไม่เท่ากับ implementation-done ตาม RULES.md §9
- external write ต้องผ่าน SafetyGate และ manifest ต้องประกาศ external_writes + safety_gate: true
- ห้ามแก้ graph artifacts ด้วยมือ ให้ graphify generate เท่านั้น

งานของคุณ:
1. สรุปก่อนว่าเข้าใจเป้าหมายงานนี้ว่าอะไร
2. ถ้ามี decision point ตาม RULES.md §10 ให้ถาม 4 ทางเลือกก่อนทำ
3. ถ้าไม่มี ให้เสนอ first slice ที่เล็กที่สุดพร้อม proof
4. ทำงานแบบ surgical เฉพาะไฟล์ที่เกี่ยวข้อง
5. ก่อนบอกว่าสำเร็จ ให้รัน:
   cd sandbox
   python tools/check.py
6. รายงานผลตามจริง: ผ่านอะไร, fail อะไร, แก้ไฟล์ไหน, ยังเหลือ risk อะไร

ห้าม:
- เดาเป้าหมายแทนเจ้าของงาน
- เพิ่ม dashboard/database/queue/AI brain ก่อน proof
- promote งานจาก sandbox/ ไป project/ ถ้ายังไม่ implementation-done
- เพิ่มกฎใหม่โดยไม่บอก scope/authority/enforcement/example/failure mode
```

## 0. เริ่มต้น / ทำความเข้าใจ repo

```text
อ่าน README.md, AGENTS.md, CLAUDE.md, .claude/skills/organ-kit/SKILL.md,
.claude/skills/organ-kit/reference/RULES.md และ MANIFEST.md

สรุปให้ฟังว่า:
- framework นี้คืออะไร
- organ คืออะไร
- กฎ 10 ข้อใน RULES.md มีอะไรบ้าง
- Human Decision Gate ใน RULES.md §10 ต้องถามเมื่อไหร่
- workflow มาตรฐานตั้งแต่สร้าง organ จนถึง implementation-done เป็นยังไง
- คำสั่ง proof gate คืออะไร

อย่าเพิ่งแก้โค้ด แค่อธิบาย
```

## 1. Human Decision Gate

```text
ก่อนเริ่มทำงานนี้ ให้เช็ก RULES.md §10 ว่ามี decision point หรือไม่:
- เป้าหมายจริงของโปรเจคยังไม่ชัดไหม
- มีหลาย feature หรือ first slice ที่ทำก่อนได้ไหม
- มี external write / production / secret / auth / billing / real user data ไหม
- มี learning-done ที่อาจต้อง promote/delete/defer/rebuild ไหม
- มี UX/business/legal/security context ที่ต้องให้คนตัดสินใจไหม

ถ้ามี ให้หยุดถามด้วย format นี้:

Decision point: <เรื่องที่ต้องตัดสินใจ>

A. <safest/smallest proof> — เหมาะเมื่อ...
B. <fastest reversible spike> — เหมาะเมื่อ...
C. <fuller implementation> — เหมาะเมื่อ...
D. <defer / shadow preview / read-only mapping> — เหมาะเมื่อ...

Recommended: <A/B/C/D>
Why: <เหตุผล + tradeoff>

ถ้าไม่มี decision point ให้บอกว่าไม่มี แล้วเสนอ smallest useful slice พร้อม proof
```

## 2. สร้าง organ ใหม่

```text
สร้าง organ ใหม่ชื่อ <ชื่อ> หน้าที่ "<อธิบายสั้นๆ บรรทัดเดียว>"

ข้อกำหนด:
- ใช้ generator เท่านั้น:
  python .claude/skills/organ-kit/scripts/new_organ.py <ชื่อ> --title "<ชื่อ>"
- ห้ามเขียน scaffold ด้วยมือ
- ถ้ามี organ ชื่อนี้อยู่แล้ว หยุดและเสนอทางเลือกตาม RULES.md §10
- หลังสร้าง ให้รัน:
  cd sandbox
  python organs/<ชื่อ>/app.py --demo
  python tools/check.py

รายงานผลตามจริงว่า demo/check ผ่านหรือ fail
```

## 3. ใส่ domain logic แบบ skeleton-first

```text
ใส่ logic จริงให้ organ <ชื่อ> ตาม RULES.md §8:

1. นิยาม ports/ ที่ domain ต้องใช้ก่อน
2. เขียน test ที่ fail ก่อน เพื่อปักพฤติกรรมที่ต้องการ
3. เขียน domain/service.py ให้ test ผ่าน โดย domain ต้อง pure และไม่มี I/O
4. งานที่กระโดดข้ามชั้น ให้ลง DEFERRED.md ไม่ใช่ทำมั่ว

แก้เฉพาะ domain/, ports/, tests/ และ DEFERRED.md ถ้าจำเป็น
ยังไม่ต้องแตะ adapter จริง เว้นแต่ถามและได้รับ decision แล้ว

ก่อนจบงาน รัน:
cd sandbox
python tools/check.py
```

## 4. เพิ่ม adapter ที่มี external write

```text
เพิ่ม adapter <ชื่อ> ให้ organ <ชื่อ> ที่เขียนออกนอกระบบไปยัง <DB/API/ClickUp/...>

ก่อนทำ ให้ถามตาม RULES.md §10 เพราะเกี่ยวกับ external write:
- A. local JSONL/dry-run proof ก่อน
- B. reversible spike
- C. real adapter พร้อม approval path
- D. shadow preview อ่านอย่างเดียว
พร้อม recommended + tradeoff

ถ้าได้รับอนุมัติให้ทำ:
- ใช้ ExternalWriteAdapter + SafetyGate จาก sandbox/shared/safety.py
- ห่อ write ด้วย WriteIntent + self.guarded(...)
- default เป็น DryRunGate หรือ preview path ที่ไม่เขียนจริง
- log จริงเก็บ local JSONL
- ส่งออกนอกแค่ summary/reportable event
- อัปเดต manifest.json: external_writes + safety_gate: true

ก่อนจบงาน รัน:
cd sandbox
python tools/check.py
```

## 5. เชื่อม organ ผ่าน contract

```text
ให้ organ <A> ใช้ organ <B> โดยผ่าน contract เท่านั้น ตาม RULES.md §3:

- สร้าง port แบบ Gateway ใน <A>/ports/
- adapter ใน <A>/adapters/ delegate ไปยัง published interface ของ <B>
- ห้าม import internals ของ <B>
- ต่อสายจริงเฉพาะใน app.py หรือ composition root
- อัปเดต depends_on ใน manifest.json ให้ตรง

ถ้าการเชื่อมนี้เปลี่ยน boundary หรือมีหลายทางเลือก ให้ถามตาม RULES.md §10 ก่อน

ก่อนจบงาน รัน:
cd sandbox
python tools/check.py
```

## 6. รัน + ตรวจเงา

```text
รัน proof gate แล้วรายงานผลตามจริง:

cd sandbox
python tools/check.py

ถ้า fail ให้แยกประเภท:
- tests fail
- doc-lint fail
- manifest validation fail
- graphify shadow: cycle / data overlap / dangling dependency / unguarded external write
- generated graph drift

อย่าแก้ graph artifacts ด้วยมือ ให้แก้ source manifest/code แล้วรัน check ใหม่
```

## 7. บันทึกงานที่เลื่อน

```text
ผมเลื่อนงาน <อะไร> ออกไปก่อน

ช่วยบันทึกใน organs/<ชื่อ>/DEFERRED.md ตามเจตนาของ RULES.md §8 และ §9:
- why_deferred
- risk
- must_close_before_promotion
- owner_decision_needed
- status

ใช้ template ที่ .claude/skills/organ-kit/templates/organ/DEFERRED.md เป็นตัวอย่าง
ห้ามใช้ DEFERRED.md เป็น wishlist ทั่วไป

ก่อนจบงาน รัน:
cd sandbox
python tools/check.py
```

## 8. เช็ก done + promote เข้า project

```text
organ <ชื่อ> ถึง implementation-done ตาม RULES.md §9 หรือยัง?

เช็กให้ครบ:
- tests/harness ผ่าน
- demo command ผ่าน
- python tools/check.py ผ่าน
- graphify strict สะอาด ไม่มี shadow
- external writes ทุกตัวมี SafetyGate และ manifest ประกาศถูก
- CHECKLIST.md phase ตรงกับ manifest.json.phase
- ไม่มี item must_close_before_promotion: true ค้างใน DEFERRED.md
- boundary สะอาด: domain ไม่ import I/O และ organ ไม่ import internals ของ organ อื่น

ถ้าครบจริง ให้เสนอแผน promote sandbox/ -> project/ พร้อมไฟล์ที่จะย้าย
ถ้ายังไม่ครบ ห้าม promote และบอกว่าขาดอะไร

ถ้าการ promote มีหลายทางเลือกหรือกระทบ production ให้ถามตาม RULES.md §10 ก่อน
```

## 9. ซ่อม / รีแฟกเตอร์ organ เดียว

```text
organ <ชื่อ> มีปัญหา <อาการ>

ช่วยซ่อมแบบ surgical:
- แก้เฉพาะ organ นี้
- ห้ามแก้ organ อื่น
- ห้ามเปลี่ยน contract เว้นแต่จำเป็นจริง
- ถ้าจำเป็นต้องเปลี่ยน contract ให้หยุดถามตาม RULES.md §10 พร้อม 4 ทางเลือก
- เพิ่มหรือแก้ test ให้ reproduce ปัญหาก่อน แล้วทำให้ผ่าน

ก่อนจบงาน รัน:
cd sandbox
python tools/check.py
```

## 10. Shadow preview / read-only planning

```text
ทำ shadow preview แบบอ่านอย่างเดียวสำหรับงาน <เรื่อง>

ห้ามเขียนไฟล์ ห้ามแก้โค้ด
ให้สำรวจและรายงาน:
- scope: เกี่ยวกับ organ/adapter/doc ไหน
- authority: canonical rule, supplement, guide, หรือ decision note
- enforcement: test/harness/manifest/guard/command อะไรพิสูจน์ได้
- example: มือใหม่ควรทำแบบไหน
- failure mode: ถ้าทำผิดจะพังยังไง
- shadow risk: มี doc/code/manifest ซ้ำหรือ drift ตรงไหน

ถ้าพบ decision point ให้เสนอ 4 ทางเลือกตาม RULES.md §10 พร้อม recommended
```
