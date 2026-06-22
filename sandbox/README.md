# sandbox

ที่เขียน/ทดลอง/พิสูจน์อวัยวะ ก่อนส่งเข้า `project/`

## Doc Contract

- **Scope:** วิธีรันและตรวจงานใน `sandbox/`
- **Authority:** guide เท่านั้น; canonical rules อยู่ที่ `.claude/skills/organ-kit/reference/RULES.md`
- **Enforcement:** `python tools/check.py` เป็น proof gate เดียว
- **Example:** command ใน section `รัน`
- **Failure mode:** มือใหม่รันคำสั่งเก่าแยกหลายชุดแล้วพลาด doc/manifest/graph drift หรือ RULES.md §10 decision gate

## โครงสร้าง (แม่แบบของทุกอวัยวะ)

```
sandbox/
  manifest.schema.json    # schema ของ organs/*/manifest.json
  shared/                 # contract กลางที่ทุกอวัยวะใช้ร่วม
    result.py             # Result/Outcome — ปลอดภัย ไม่ throw มั่ว, รองรับ "ถามก่อนสร้าง"
    ids.py                # สร้าง id + ตรวจซ้ำ
    ports.py              # base Port (ABC)
    safety.py             # SafetyGate — กั้นทุก external write (dry-run + ขออนุมัติ)
  organs/
    registry/             # อวัยวะที่ 1 — สมัครสมาชิก
      domain/             # OOP core บริสุทธิ์ (ไม่รู้จัก telegram/db)
      ports/              # interface (ABC) ที่ domain ต้องการ
      adapters/           # ของจริง: jsonl, telegram, clickup
      tests/              # เทสว่าทำงานจริง
      app.py              # composition root — ต่อสายทุกชิ้นแล้วรัน slice
      manifest.json       # ข้อมูลอวัยวะ (graphify อ่านอันนี้)
      CHECKLIST.md        # skeleton-first checklist; sync กับ manifest phase
  tools/
    check.py              # proof gate เดียวก่อนบอกว่างานเสร็จ
    graphify.py           # generate สารบัญ (CATALOG.md/graph.json/graph.mmd) + shadow detection
    token_compressor.py   # ย่อ handoff state ให้ agent ถัดไป (ไม่แตะ audit log)
```

## รัน

```bash
cd sandbox
python organs/registry/app.py --demo           # รัน slice + ย่อ handoff state ให้ agent ถัดไป
python tools/check.py                           # tests + doc lint + manifest + graph guard
```

ต่อ Telegram จริง: ตั้ง `TELEGRAM_BOT_TOKEN` แล้ว `python3 organs/registry/app.py --telegram`

เวลาเลื่อนขั้น skeleton-first ให้แก้ `organs/<organ>/CHECKLIST.md` กับ
`organs/<organ>/manifest.json` field `phase` พร้อมกัน แล้วรัน `python tools/check.py`.

`token_compressor.py` ใช้หลัง slice ทำงานแล้วเท่านั้น: log จริงยังเก็บเป็น JSONL เต็ม
ใน `.data/registry.log.jsonl`; demo จะย่อสำเนา state สำหรับส่งต่อ agent ถัดไปให้ดู
เพื่อประหยัด context โดยไม่ทำ audit log เสียรูป.
