"""Telegram interface for the Mr. Peabody memory assistant."""

from __future__ import annotations

import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.bot.system_prompt import generate_answer
from src.main import save_memory
from src.memory.search import HybridSearch
from src.memory.vector_store import MemoryStore


async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save the text following /save."""
    if not update.message:
        return
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /save <note or URL>")
        return

    store: MemoryStore = context.application.bot_data["store"]
    count = save_memory(store, text)
    await update.message.reply_text(f"Saved {count} memory chunk(s).")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answer a question using retrieved memories."""
    if not update.message:
        return
    question = " ".join(context.args).strip()
    if not question:
        await update.message.reply_text("Usage: /ask <question>")
        return

    store: MemoryStore = context.application.bot_data["store"]
    memories = HybridSearch(store).search(question)
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    answer = generate_answer(
        question,
        memories,
        api_key=os.getenv("OPENAI_API_KEY") if provider == "openai" else None,
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
    await update.message.reply_text(answer)


def build_application(token: str, store: MemoryStore) -> Application:
    """Build a Telegram application without starting the network loop."""
    application = Application.builder().token(token).build()
    application.bot_data["store"] = store
    application.add_handler(CommandHandler("save", save_command))
    application.add_handler(CommandHandler("ask", ask_command))
    return application