# ohlyshit — First-Button Project Skill for AI Agents

กฎ + skill สำหรับมือใหม่ที่อยากเริ่มโปรเจคหรืองานให้ถูกตั้งแต่ "กระดุมเม็ดแรก"
ก่อนเขียนของใหญ่ ให้บีบงานให้เป็น slice เล็กที่ทดสอบได้จริง แล้วค่อยแยกเป็น
"อวัยวะ" (organ) อิสระที่ซ่อม/ทดสอบ/ต่อยอดได้ทีละชิ้น

## ใช้ทำอะไร

- ปูพื้นฐานโปรเจคใหม่ให้ไม่เริ่มจากโครงใหญ่เกินตัว
- บังคับให้มี success criteria ก่อนเขียนโค้ด
- สร้าง module/service/department แบบมี test และ safety gate ตั้งแต่แรก
- ให้ AI assistant ทำงานแบบถามเมื่อไม่ชัด เสนอทางเลือกเมื่อมีหลายทาง และแก้แบบ surgical

## Quickstart 60 วินาที

```bash
git clone https://github.com/choodej/ohlyshit.git
cd ohlyshit
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r sandbox/requirements.txt
cd sandbox
python -m pytest -q
python tools/validate_manifests.py
python organs/registry/app.py --demo          # includes compressed next-agent handoff state
python tools/graphify.py --strict
```

ผ่านแล้วแปลว่าเครื่องคุณพร้อม: tests เขียว, demo slice รันได้, handoff state ถูกย่อ,
manifest/checklist ไม่ drift, และ graph ไม่มี shadow.

ถ้าจะสร้าง organ แรกของตัวเอง:

```bash
cd ..
python3 .claude/skills/organ-kit/scripts/new_organ.py first_task --title "First task"
cd sandbox
python -m pytest organs/first_task/tests -q
python tools/validate_manifests.py
python tools/graphify.py --strict
```

ใช้กับ Claude Code: เปิด repo นี้แล้ว `CLAUDE.md` จะบอกกฎ project ให้ Claude โหลดอัตโนมัติ.
ใช้กับ agent อื่น: อ่าน `AGENTS.md` ก่อน แล้วตาม pointer ไปที่ `RULES.md`.

**Core features (frozen):**
- 🧩 **Hexagonal OOP** — domain บริสุทธิ์ คุยโลกภายนอกผ่าน ports/adapters เท่านั้น
- 🗺️ **Graphify auto-mapping** — สร้างสารบัญ + Mermaid + ตรวจ "เงา" (วน/ทับ/ขาด) อัตโนมัติ
- 🪶 **Token optimization** — ย่อ context/state ให้ประหยัด token (ไม่แตะ audit log)
- 🛡️ **Built-in Safety Gates** — ทุก external write ผ่าน dry-run + ขออนุมัติก่อนเขียนจริง

## หลักการ (กฎที่ล็อกแล้ว)

0. **ติดกระดุมเม็ดแรกให้ถูกก่อนเขียนโค้ด**
   - ถ้ายังตอบไม่ได้ว่า "ผู้ใช้ทำอะไรได้ 1 อย่าง" และ "พิสูจน์ว่าผ่านยังไง" ให้ถามก่อน
   - เริ่มจาก vertical slice ที่เล็กที่สุด: input → domain decision → saved/logged result
   - success criteria ต้องทดสอบได้ เช่น test ผ่าน, demo command รันได้, graph ไม่มี shadow
1. **แยก sandbox / project ชัดเจน**
   - `sandbox/` = ที่เขียนใหม่ ทดลอง พิสูจน์ว่าทำงานจริง
   - `project/` = ของจริง รับเฉพาะอวัยวะที่สมบูรณ์พร้อมใช้แล้วเท่านั้น
2. **ทุกอวัยวะเป็น OOP + Hexagonal** — domain (core บริสุทธิ์) คุยกับโลกภายนอก
   ผ่าน `ports/` (interface) เท่านั้น ของจริงอยู่ใน `adapters/` (เปลี่ยน/ซ่อมได้ทีละชิ้น)
3. **อวัยวะคุยกันผ่าน contract เท่านั้น** ห้ามเรียกข้างในกันตรงๆ
4. **ปลอดภัยแต่ไม่ช้า** — งานที่ย้อนกลับได้ทำเลย; งานที่ทำลายของเดิม / id ซ้ำ /
   ชื่อซ้ำ / กระทบหลายแผนก → คืน "ทางเลือก" ให้คนตัดสินใจก่อน (ไม่สร้างมั่ว)
5. **Log จริงเก็บ local (JSONL)** เร็วและค้นได้; ส่งเฉพาะสรุป/ผลงานไป ClickUp ผ่าน adapter
6. **สารบัญ (graph) generate อัตโนมัติจากโค้ดเท่านั้น** ห้ามเขียนมือ — ดู `sandbox/tools/graphify.py`
7. **ทุก external write ผ่าน SafetyGate** — dry-run preview + ขออนุมัติ (งานย้อนกลับได้ auto) — ดู `sandbox/shared/safety.py`
8. **Skeleton-first + deferred work** — ดู canonical rule ที่ `.claude/skills/organ-kit/reference/RULES.md` §8
9. **Two-tier DoD** (`learning-done` ≠ `implementation-done`) — ดู `.claude/skills/organ-kit/reference/RULES.md` §9

## Core utilities (frozen framework)

| ไฟล์ | หน้าที่ |
|---|---|
| `sandbox/shared/safety.py` | `SafetyGate` (PolicyGate/DryRunGate/...) + `ExternalWriteAdapter` กั้นทุกการเขียนนอก |
| `sandbox/manifest.schema.json` | schema ของ `manifest.json`; ระบุ field ที่ graphify ใช้จับ shadow |
| `sandbox/tools/validate_manifests.py` | ตรวจ `manifest.json` + `CHECKLIST.md` phase ก่อน graphify/CI |
| `sandbox/tools/graphify.py` | สารบัญ + Mermaid + shadow detection (cycle/overlap/dangling/unguarded-write); `--strict` สำหรับ CI |
| `sandbox/tools/token_compressor.py` | ย่อ state สำหรับส่งต่อ agent ถัดไป — ใช้กับ context เท่านั้น ไม่แตะ audit log |
| `sandbox/organs/*/CHECKLIST.md` | checklist ของ skeleton-first; sync กับ `manifest.json.phase` |

## เส้นแรกที่พิสูจน์แล้ว (vertical slice)

`Register (สมัครสมาชิก) → รับคำสั่งผ่าน Inbound (Telegram) → เขียน Log (JSONL) → ย่อ handoff state ให้ agent ถัดไป`

ดู `sandbox/README.md`

## Skill แจกฟรี: `organ-kit`

แม่แบบ + กฎทั้งหมดถูกแพ็กเป็น Claude Code Skill ที่เป็นกลาง ใช้ได้ทุกโปรเจค
อยู่ที่ `.claude/skills/organ-kit/` — ก็อปโฟลเดอร์นี้ไปวางใน `.claude/skills/` ของ repo ไหนก็ได้

สร้างอวัยวะใหม่ (รันได้โดยไม่ต้องมี AI):

```bash
python3 .claude/skills/organ-kit/scripts/new_organ.py <organ_name> --title "ชื่อ"
```

ได้อวัยวะที่ **รันได้ + ผ่านเทสทันที** พร้อมกฎ ask-before-create, log JSONL, และ
graphify ในตัว ดูรายละเอียดที่ `.claude/skills/organ-kit/SKILL.md`
