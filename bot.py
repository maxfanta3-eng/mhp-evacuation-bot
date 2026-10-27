import asyncio
import logging
import threading
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = "8985514206:AAGcI2McxM4mXggd0JdYi7HUefjvmt7kXVQ"
DATA_FILE = "shift_data.json"

# Загрузка данных
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "shift_data": {
            "chief": 1,
            "experts": 2,
            "robots_crew": 4,
            "eng_op": 12,
        },
        "last_updated_by": "Ще не оновлювалось"
    }

# Сохранение данных
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

router = Router()

# Кнопки с быстрым изменением (+1 / -1) прямо в меню для каждой категории
def get_main_keyboard(shift_data):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"👨‍✈️ Керівник служби: {shift_data['chief']}", callback_data="menu_chief")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data="dec_chief"),
                InlineKeyboardButton(text="➕", callback_data="inc_chief")
            ],
            [
                InlineKeyboardButton(text=f"🛠 Техесперти+слюсаря: {shift_data['experts']}", callback_data="menu_experts")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data="dec_experts"),
                InlineKeyboardButton(text="➕", callback_data="inc_experts")
            ],
            [
                InlineKeyboardButton(text=f"🤖 Роботизований склад: {shift_data['robots_crew']}", callback_data="menu_robots_crew")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data="dec_robots_crew"),
                InlineKeyboardButton(text="➕", callback_data="inc_robots_crew")
            ],
            [
                InlineKeyboardButton(text=f"🤖 Аварійники: {shift_data['robots_crew']}", callback_data="menu_robots_crew")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data="dec_robots_crew"),
                InlineKeyboardButton(text="➕", callback_data="inc_robots_crew")
            ],
            [
                InlineKeyboardButton(text=f"👷‍♂️ Інженер + оператор: {shift_data['eng_op']}", callback_data="menu_eng_op")
            ],
            [
                InlineKeyboardButton(text="➖", callback_data="dec_eng_op"),
                InlineKeyboardButton(text="➕", callback_data="inc_eng_op")
            ],
            [
                InlineKeyboardButton(text="🔄 Оновити / Скинути кеш", callback_data="refresh_view")
            ]
        ]
    )

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
    await message.answer(
        generate_status_text(),
        reply_markup=get_main_keyboard(data["shift_data"]),
        parse_mode="Markdown"
    )

# Обработка нажатий на плюсы и минусы
@router.callback_query(F.data.startswith(("inc_", "dec_", "menu_")))
async def process_buttons(callback: CallbackQuery):
    action = callback.data
    data = load_data()
    shift_data = data["shift_data"]
    
    # Определяем категорию
    if "chief" in action:
        key = "chief"
    elif "experts" in action:
        key = "experts"
    elif "robots_crew" in action:
        key = "robots_crew"
    elif "eng_op" in action:
        key = "eng_op"
    else:
        await callback.answer("Готово")
        # Просто обновляем текст для refresh_view
        try:
            await callback.message.edit_text(
                generate_status_text(),
                reply_markup=get_main_keyboard(shift_data),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        return

    # Меняем значение по кнопке плюс/минус
    if action.startswith("inc_"):
        shift_data[key] += 1
        data["last_updated_by"] = callback.from_user.full_name or callback.from_user.username or "Співробітник"
        save_data(data)
    elif action.startswith("dec_"):
        if shift_data[key] > 0:
            shift_data[key] -= 1
            data["last_updated_by"] = callback.from_user.full_name or callback.from_user.username or "Співробітник"
            save_data(data)

    # Мгновенно обновляем сообщение у всех в чате без спама и новых строк!
    try:
        await callback.message.edit_text(
            generate_status_text(),
            reply_markup=get_main_keyboard(shift_data),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    
    await callback.answer(f"Змінено!")

# Веб-сервер для Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    asyncio.run(main())
