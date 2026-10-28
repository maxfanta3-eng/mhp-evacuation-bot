import asyncio
import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = os.getenv("BOT_TOKEN", "8985514206:AAGcI2McxM4mXggd0JdYi7HUefjvmt7kXVQ")
DATA_FILE = "shift_data_v3.json"

router = Router()

# Полный и точный словарь со всеми вашими категориями и сотрудниками
DEFAULT_DATA = {
    "Керівник служби": {
        "Островий С.Р.": False,
    },
    "Техексперти": {
        "Хорольський О.В.": False,
        "Мигулько О.О.": False,
        "Склярук А.М.": False,
        "Панкратьєв Є.Ю.": False,
        "Сташко О.В.": False,
        "Рудик Є.М.": False,
    },
    "Слюсаря тех.": {
        "Забукін А.В.": False,
        "Колпаков О.В.": False,
        "Матюша М.М.": False,
        "Іванін Д.В.": False,
        "Лалак Я.А.": False,
        "Щуренко О.М.": False,
        "Провільський Ю.М.": False,
        "Жаріков С.О.": False,
        "Горобець М.М.": False,
        "Денисюк С.П.": False,
        "Луговий С.В.": False,
        "Мурзак Б.Ю.": False,
    },
    "Чергові аварійники": {
        "Король А.І. інж з мех.": False,
        "Гарник О.Г. інж ІІ": False,
        "Коваленко М.С.": False,
        "Олійник Ю.В. інж з мех.": False,
        "Ладанюк С.М.": False,
        "Петровський Д.О. інж з мех.": False,
        "Кольцов О.Д. інж ІІ": False,
        "Стороженко В.С.": False,
        "Степаненко Д.А. інж з мех.": False,
        "Мисько І.І. інж ІІ": False,
        "Мельник В.В.": False,
        "Чалий Ю.В.": False,
    },
    "Роботизований склад": {
        "Вербецький С.І.": False,
        "Незгода А.Д.": False,
        "Пастушенко В.С.": False,
        "Рижавський М.П.": False,
        "Дробчак М.Р.": False,
        "Вабст П.Л.": False,
    },
    "Інженера+оператори змА": {
        "Баланюк В.Ю.": False,
        "Барков Ю.М. інж ІІ": False,
        "Богданов О.С.": False,
        "Боднар О.С.": False,
        "Бугара О.О.": False,
        "Вельган В.А.": False,
        "Гладир М.В.": False,
        "Головко М.О.": False,
        "Гончарук О.М.": False,
        "Гринчик О.В.": False,
        "Денисюк С.В. інж ІІ": False,
        "Диченко А.О.": False,
        "Дремух Д.А.": False,
        "Захаров О.С.": False,
        "Калашнік М.С.": False,
        "Камінський В.О.": False,
        "Керн Н.В.": False,
        "Кізман О.В.": False,
        "Кульчицький В.В.": False,
        "Лазаренко Д.В.": False,
        "Марчук О.П.": False,
        "Онуфрієнко О.М.": False,
        "Полянський В.В.": False,
        "Похилюк І.М.": False,
        "Прибила А.С.": False,
        "Пшеничний В.О. інж з нал.": False,
        "Русецький С.С.": False,
        "Русяновський Р.О.": False,
        "Сасюк Д.Ю.": False,
        "Томашевський О.П.": False,
        "Торішній О.Г.": False,
        "Федічев М.В. інж ІІ": False,
        "Фірсов Р.І.": False,
        "Фірсова Я.І.": False,
        "Чухало О.О.": False,
        "Шрамко В.С.": False,
        "Шумілов В.М.": False,
    },
    "Інженера+оператори змБ": {
        "Бондаренко М.М.": False,
        "Боченко О.О.": False,
        "Білоус М.В.": False,
        "Гуцол І.Д.": False,
        "Головащенко О.М.": False,
        "Грушовий О.В.": False,
        "Грицик А.В.": False,
        "Давидюк Д.А.": False,
        "Дубенко С.О.": False,
        "Єпанчинцев В.В.": False,
        "Ільїнов Д.": False,
        "Клещ В.А. інж з нал.": False,
        "Коваленко О.В.": False,
        "Лаврук К.М.": False,
        "Ліщенюк В.М.": False,
        "Магдич О.О.": False,
        "Малка О.М.": False,
        "Півторак О.М.": False,
        "Романов В.В.": False,
        "Сердюк Д.В.": False,
        "Склярук І.О.": False,
        "Сірий А.С.": False,
        "Темрієнко В.І.": False,
        "Требенко П.М.": False,
        "Хацько Є.В.": False,
        "Хмарук Я.І.": False,
        "Шумейко А.В.": False,
        "Ясько Д.В.": False,
        "Яремко В.Я.": False,
        "Боднар А.С. інж ІІ": False,
        "Лещенко В.В. інж ІІ": False,
        "Колодій А.Г. інж ІІ": False,
        "Цурман О.О. інж ІІ": False,
        "Горущенко П.В.": False,
        "Нароган С.В.": False,
        "Паламарчук О.І.": False,
        "Попов В.С.": False,
        "Русс М.О.": False,
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Объединяем, чтобы новые ключи/сотрудники не терялись, если файл уже существовал
                for cat, emps in DEFAULT_DATA.items():
                    if cat not in saved:
                        saved[cat] = emps
                    else:
                        for emp, status in emps.items():
                            if emp not in saved[cat]:
                                saved[cat][emp] = status
                return saved
        except Exception:
            pass
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if not os.path.exists(DATA_FILE):
    save_data(DEFAULT_DATA)

def get_keyboard(category_name):
    data = load_data()
    category_data = data.get(category_name, {})
    
    keyboard = []
    if not category_data:
        keyboard.append([InlineKeyboardButton(text="Список порожній", callback_data="none")])
    else:
        for name, status in category_data.items():
            icon = "✅" if status else "❌"
            btn_text = f"{icon} {name}"
            callback_data = f"toggle:{category_name}:{name}"
            keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад до списку", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_keyboard():
    data = load_data()
    keyboard = []
    for cat_name in data.keys():
        keyboard.append([InlineKeyboardButton(text=cat_name, callback_data=f"cat:{cat_name}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "📋 Актуальний склад служби (евакуація)\nНатисніть на прізвище, щоб змінити статус (✔️/❌):",
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data.startswith("cat:"))
async def open_category(callback: CallbackQuery):
    cat_name = callback.data.split(":", 1)[1]
    keyboard = get_keyboard(cat_name)
    try:
        await callback.message.edit_text(
            f"📋 Список: {cat_name}\nНатисніть на прізвище, щоб змінити статус (✔️/❌):",
            reply_markup=keyboard
        )
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "📋 Актуальний склад служби (евакуація)\nНатисніть на прізвище, щоб змінити статус (✔️/❌):",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("toggle:"))
async def toggle_status(callback: CallbackQuery):
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    
    cat_name = parts[1]
    emp_name = parts[2]
    
    data = load_data()
    if cat_name in data and emp_name in data[cat_name]:
        data[cat_name][emp_name] = not data[cat_name][emp_name]
        save_data(data)
    
    keyboard = get_keyboard(cat_name)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception:
        pass
    
    try:
        await callback.answer("Статус змінено!")
    except Exception:
        pass

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
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
    
    await dp.start_polling(bot)

if _name_ == "_main_":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    asyncio.run(main())
