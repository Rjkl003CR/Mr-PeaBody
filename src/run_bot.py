"""Run the Telegram bot using environment configuration."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from src.bot.interface import build_application
from src.memory.vector_store import MemoryStore


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    store = MemoryStore(path=os.getenv("CHROMA_PATH", "data/chroma_db"))
    build_application(token, store).run_polling()


if __name__ == "__main__":
    main()