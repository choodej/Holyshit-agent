# sandbox

ที่เขียน/ทดลอง/พิสูจน์อวัยวะ ก่อนส่งเข้า `project/`

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
  tools/
    graphify.py           # generate สารบัญ (CATALOG.md/graph.json/graph.mmd) + shadow detection
    token_compressor.py   # ย่อ context/state ให้ token น้อยลง (ไม่แตะ audit log)
```

## รัน

```bash
cd sandbox
python3 -m pip install -r requirements.txt     # pytest (+ python-telegram-bot ถ้าจะต่อจริง)
python3 -m pytest organs/registry/tests -q     # พิสูจน์อวัยวะทำงานจริง
python3 organs/registry/app.py --demo          # รัน slice แบบ demo (ไม่ต้องมี token)
python3 -m pytest -q                            # เทสทั้งหมด (organs + core utilities)
python3 tools/graphify.py                        # สร้างสารบัญ + ตรวจเงา (เพิ่ม --strict ให้ fail บน warning)
```

ต่อ Telegram จริง: ตั้ง `TELEGRAM_BOT_TOKEN` แล้ว `python3 organs/registry/app.py --telegram`
