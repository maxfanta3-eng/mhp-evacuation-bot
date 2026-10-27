import asyncio
import json
import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")

router = Router()
DATA_FILE = "shift_data.json"

DEFAULT_DATA = {
    "shift_data": {
        "chief": 0,
        "experts": 0,
        "warehouse": 0,
        "emergency": 0,
        "eng_op": 0
    },
    "last_updated_by": "Ще ніхто"
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_main_keyboard(shift_data):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👤 Керівник служби: {shift_data['chief']}", callback_data="ignore_chief")],
        [
            InlineKeyboardButton(text="➖", callback_data="dec_chief"),
            InlineKeyboardButton(text="➕", callback_data="inc_chief")
        ],
        [InlineKeyboardButton(text=f"🛠 Техесперти + слюсаря: {shift_data['experts']}", callback_data="ignore_experts")],
        [
            InlineKeyboardButton(text="➖", callback_data="dec_experts"),
            InlineKeyboardButton(text="➕", callback_data="inc_experts")
        ],
        [InlineKeyboardButton(text=f"🤖 Роботизований склад: {shift_data['warehouse']}", callback_data="ignore_warehouse")],
        [
            InlineKeyboardButton(text="➖", callback_data="dec_warehouse"),
            InlineKeyboardButton(text="➕", callback_data="inc_warehouse")
        ],
        [InlineKeyboardButton(text=f"⚡ Чергові аварійники: {shift_data['emergency']}", callback_data="ignore_emergency")],
        [
            InlineKeyboardButton(text="➖", callback_data="dec_emergency"),
            InlineKeyboardButton(text="➕", callback_data="inc_emergency")
        ],
        [InlineKeyboardButton(text=f"👷 Інженер + оператор: {shift_data['eng_op']}", callback_data="ignore_eng_op")],
        [
            InlineKeyboardButton(text="➖", callback_data="dec_eng_op"),
            InlineKeyboardButton(text="➕", callback_data="inc_eng_op")
        ],
        [InlineKeyboardButton(text="🔄 Оновити дані", callback_data="refresh_view")]
    ])

def generate_status_text():
    data = load_data()
    shift_data = data["shift_data"]
    total = sum(shift_data.values())
    return (
        f"🚨 АКТУАЛЬНИЙ СКЛАД СЛУЖБИ (ЕВАКУАЦІЯ)\n\n"
        f"• 👤 Керівник служби: {shift_data['chief']}\n"
        f"• 🛠 Техесперти + слюсаря: {shift_data['experts']}\n"
        f"• 🤖 Роботизований склад: {shift_data['warehouse']}\n"
        f"• ⚡ Чергові аварійники: {shift_data['emergency']}\n"
        f"• 👷 Інженер + оператор: {shift_data['eng_op']}\n\n"
        f"• 🔴 ВСЬОГО НА ТЕРИТОРІЇ: {total} осіб\n\n"
        f"• 🕒 *Останній оновив:* {data['last_updated_by']}"
    )

@router.message(Command("start"))
async def cmd_start(message: Message):
    data = load_data()
    # Удаляем старое сообщение пользователя с командой /start для чистоты чата
    try:
        await message.delete()
    except Exception:
        pass
    
    await message.answer(
        generate_status_text(),
        reply_markup=get_main_keyboard(data["shift_data"]),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith(("inc_", "dec_", "refresh_", "ignore_")))
async def process_buttons(callback: CallbackQuery):
    data = load_data()
    shift_data = data["shift_data"]
    action = callback.data
    user_name = callback.from_user.full_name
    if action.startswith("inc_"):
        key = action.replace("inc_", "")
        if key in shift_data:
            shift_data[key] += 1
            data["last_updated_by"] = user_name
    elif action.startswith("dec_"):
        key = action.replace("dec_", "")
        if key in shift_data and shift_data[key] > 0:
            shift_data[key] -= 1
            data["last_updated_by"] = user_name
    elif action == "refresh_view":
        data["last_updated_by"] = f"{user_name} (оновлено)"

    save_data(data)

    try:
        await callback.message.edit_text(
            generate_status_text(),
            reply_markup=get_main_keyboard(shift_data),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", 10000), SimpleHandler)
    server.serve_forever()

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if name == "main":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    asyncio.run(main())
