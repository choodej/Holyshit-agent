# CATALOG — system index (auto-generated, do not edit by hand)

Organs: 1

## registry — สมัครสมาชิก (Registration)
- status: `slice-proven` | version: `0.1.0`
- path: `organs/registry`
- purpose: รับคำสั่งสมัครสมาชิกผ่านช่องทางใดก็ได้ ตรวจซ้ำ แล้วบันทึก + log
- ports: MemberRepository, Logger, Inbound
- depends on: (independent)
