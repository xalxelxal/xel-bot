
import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))


def is_owner(update):
    return (
        OWNER_ID != 0
        and update.effective_user
        and update.effective_user.id == OWNER_ID
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text(
            "⛔ Bot ini khusus pemilik."
        )
        return

    keyboard = [
        [InlineKeyboardButton("🔍 Cek Nomor", callback_data="nomor")],
        [InlineKeyboardButton("📶 Cek Kuota", callback_data="kuota")],
        [InlineKeyboardButton("💰 Cek Saldo", callback_data="saldo")],
        [InlineKeyboardButton("📦 Daftar Paket", callback_data="paket")]
    ]

    await update.message.reply_text(
        "🔥 SIDOMPUL PRIVATE BOT\n\n"
        "Selamat datang, Sal!\n"
        "Silakan pilih layanan:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Telegram ID kamu: {update.effective_user.id}"
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_owner(update):
        await query.message.reply_text("⛔ Akses ditolak.")
        return

    messages = {
        "nomor": "🔍 Cek nomor\n\nIntegrasi API Sidompul belum tersedia.",
        "kuota": "📶 Cek kuota\n\nMenunggu akses API resmi.",
        "saldo": "💰 Cek saldo\n\nMenunggu akses API resmi.",
        "paket": "📦 Daftar paket\n\nMenunggu akses API resmi."
    }

    await query.message.reply_text(
        messages.get(query.data, "Menu tidak ditemukan.")
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN belum diatur!")

    if OWNER_ID == 0:
        raise RuntimeError("OWNER_ID belum diatur!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", myid))
    app.add_handler(CallbackQueryHandler(menu))

    app.run_polling()


if __name__ == "__main__":
    main()
