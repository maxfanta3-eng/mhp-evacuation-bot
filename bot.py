import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

# Твой токен от @evacuation_mhp_bot
TOKEN = "8985514206:AAGcI2McxM4mXggd0JdYi7HUefjvmt7kXVQ"

# Данные о количестве людей по категориям
shift_data = {
    "chief": 1,
    "experts": 2,
    "locksmiths": 4,
    "operators": 12,
}

last_updated_by = "Ще не оновлювалось"

router = Router()

class ShiftState(StatesGroup):
    waiting_for_count = State()
    current_category = State()

def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍✈️ Начальник служби", callback_data="set_chief")],
            [InlineKeyboardButton(text="🛠 Техексперти", callback_data="set_experts")],
            [InlineKeyboardButton(text="⚙️ Слюсарі", callback_data="set_locksmiths")],
            [InlineKeyboardButton(text="👷‍♂️ Оператори + Інженери", callback_data="set_operators")],
        ]
    )

def generate_status_text():
    total = sum(shift_data.values())
    return (
        f"🚨 АКТУАЛЬНИЙ СКЛАД СЛУЖБИ (ЕВАКУАЦІЯ)\n\n"
        f"• 👨‍✈️ Начальник служби: {shift_data['chief']}\n"
        f"• 🛠 Техексперти: {shift_data['experts']}\n"
        f"• ⚙️ Слюсарі: {shift_data['locksmiths']}\n"
        f"• 👷‍♂️ Оператори + Інженери: {shift_data['operators']}\n\n"
        f"🔴 ВСЬОГО НА ТЕРИТОРІЇ: {total} осіб\n\n"
        f"✍️ *Останній оновив:* {last_updated_by}"
    )

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Це бот обліку складу служби для евакуації.\n\n"
        "Ось поточний звіт:",
        reply_markup=get_main_keyboard()
    )
    await message.answer(generate_status_text(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("set_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    category_map = {
        "set_chief": ("chief", "Начальник служби"),
        "set_experts": ("experts", "Техексперти"),
        "set_locksmiths": ("locksmiths", "Слюсарі"),
        "set_operators": ("operators", "Оператори + Інженери"),
    }
    
    action = callback.data
    if action in category_map:
        cat_key, cat_name = category_map[action]
        await state.update_data(category=cat_key, category_name=cat_name)
        await state.set_state(ShiftState.waiting_for_count)
        await callback.message.answer(
            f"Введіть актуальну кількість для категорії: {cat_name} (цифрою):",
            parse_mode="Markdown"
        )
        await callback.answer()

@router.message(ShiftState.waiting_for_count)
async def process_count_input(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Будь ласка, введіть число (тільки цифри). Спробуйте ще раз:")
        return
    
    count = int(message.text)
    user_data = await state.get_data()
    cat_key = user_data["category"]
    
    shift_data[cat_key] = count
    global last_updated_by
    last_updated_by = message.from_user.full_name or message.from_user.username or "Співробітник"
    
    await state.clear()
    
    await message.answer("✅ Дані оновлено!", reply_markup=get_main_keyboard())
    await message.answer(generate_status_text(), parse_mode="Markdown")

# Заглушка веб-сервера для Render (чтобы веб-сервис успешно запускался)
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
    # Запускаем веб-сервер в отдельном потоке, чтобы Render видел активность
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    # Запускаем самого бота
    asyncio.run(main())
