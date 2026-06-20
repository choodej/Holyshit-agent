"""Adapter: รับคำสั่งสมัครผ่าน Telegram (ประตูติดต่อรับส่งงาน)

ต้องตั้ง env TELEGRAM_BOT_TOKEN และติดตั้ง python-telegram-bot ก่อนใช้จริง
import lib แบบ lazy เพื่อให้ slice/เทสวิ่งได้โดยไม่ต้องมี lib นี้

ผู้ใช้พิมพ์:  /register <username>
"""
from __future__ import annotations

import os
from typing import Callable

from ..ports.inbound import Inbound, RegisterCommand


class TelegramInbound(Inbound):
    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")

    def run(self, handle: Callable[[RegisterCommand], str]) -> None:
        if not self._token:
            raise RuntimeError("ยังไม่ได้ตั้ง TELEGRAM_BOT_TOKEN")

        # lazy import — มีเฉพาะตอนต่อจริง
        from telegram import Update
        from telegram.ext import (
            ApplicationBuilder,
            CommandHandler,
            ContextTypes,
        )

        async def on_register(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
            args = ctx.args or []
            username = args[0] if args else ""
            reply = handle(RegisterCommand(username=username, source="telegram"))
            await update.message.reply_text(reply)

        app = ApplicationBuilder().token(self._token).build()
        app.add_handler(CommandHandler("register", on_register))
        app.run_polling()
