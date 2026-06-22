# ohlyshit — Universal OOP Base Framework for AI Agents

ระบบที่ประกอบจาก "อวัยวะ" (organ) อิสระ แต่ละอวัยวะทดสอบได้จริงด้วยตัวเอง
ก่อนจะนำมาต่อกันเป็น "สมอง + เส้นประสาท" ภายหลัง

**Core features (frozen):**
- 🧩 **Hexagonal OOP** — domain บริสุทธิ์ คุยโลกภายนอกผ่าน ports/adapters เท่านั้น
- 🗺️ **Graphify auto-mapping** — สร้างสารบัญ + Mermaid + ตรวจ "เงา" (วน/ทับ/ขาด) อัตโนมัติ
- 🪶 **Token optimization** — ย่อ context/state ให้ประหยัด token (ไม่แตะ audit log)
- 🛡️ **Built-in Safety Gates** — ทุก external write ผ่าน dry-run + ขออนุมัติก่อนเขียนจริง

## หลักการ (กฎที่ล็อกแล้ว)

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

## Core utilities (frozen framework)

| ไฟล์ | หน้าที่ |
|---|---|
| `sandbox/shared/safety.py` | `SafetyGate` (PolicyGate/DryRunGate/...) + `ExternalWriteAdapter` กั้นทุกการเขียนนอก |
| `sandbox/tools/graphify.py` | สารบัญ + Mermaid + shadow detection (cycle/overlap/dangling/unguarded-write); `--strict` สำหรับ CI |
| `sandbox/tools/token_compressor.py` | ย่อ JSON/log เป็น state แน่นๆ (lossless / digest) — สำหรับ context ไม่ใช่ audit log |

## เส้นแรกที่พิสูจน์แล้ว (vertical slice)

`Register (สมัครสมาชิก) → รับคำสั่งผ่าน Inbound (Telegram) → เขียน Log (JSONL)`

ดู `sandbox/README.md`

## Skill แจกฟรี: `organ-kit`

แม่แบบ + กฎทั้งหมดถูกแพ็กเป็น Claude Code Skill ที่เป็นกลาง ใช้ได้ทุกโปรเจค
อยู่ที่ `.claude/skills/organ-kit/` — ก็อปโฟลเดอร์นี้ไปวางใน `.claude/skills/` ของ repo ไหนก็ได้

สร้างอวัยวะใหม่ (รันได้โดยไม่ต้องมี AI):

```bash
python .claude/skills/organ-kit/scripts/new_organ.py <organ_name> --title "ชื่อ"
```

ได้อวัยวะที่ **รันได้ + ผ่านเทสทันที** พร้อมกฎ ask-before-create, log JSONL, และ
graphify ในตัว ดูรายละเอียดที่ `.claude/skills/organ-kit/SKILL.md`
