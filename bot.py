import asyncio
import json
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = "8985514206:AAGcI2McxM4mXggd0JdYi7HUefjvmt7kXVQ"
DATA_FILE = "shift_data_v3.json"

RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://mhp-evacuation-bot.onrender.com")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 10000))

router = Router()

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
        "Білик С.В.": False,
        "Білоус О.В.": False,
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

CAT_KEYS = list(DEFAULT_DATA.keys())

LAST_UPDATE_FILE = "last_update_v3.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
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

def load_last_user():
    if os.path.exists(LAST_UPDATE_FILE):
        try:
            with open(LAST_UPDATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("user", "Невідомо")
        except Exception:
            pass
    return "Ще ніхто не оновлював"

def save_last_user(name):
    with open(LAST_UPDATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"user": name}, f, ensure_ascii=False, indent=4)

if not os.path.exists(DATA_FILE):
    save_data(DEFAULT_DATA)

ICONS = {
    "Керівник служби": "👤",
    "Техексперти": "🛠",
    "Слюсаря тех.": "🔧",
    "Роботизований склад": "🤖",
    "Чергові аварійники": "⚡",
    "Інженера+оператори змА": "👷‍♂️",
    "Інженера+оператори змБ": "👷‍♂️"
}

def get_main_text_and_keyboard():
    data = load_data()
    total_checked = 0
    total_all = 0
    
    keyboard = []
    for idx, cat_name in enumerate(CAT_KEYS):
        emps = data.get(cat_name, {})
        cat_total = len(emps)
        cat_checked = sum(1 for status in emps.values() if status)
        total_all += cat_total
        total_checked += cat_checked
        
        icon = ICONS.get(cat_name, "📋")
        btn_text = f"{icon} {cat_name}: {cat_checked} / {cat_total}"
        # Используем короткий индекс вместо полного названия в callback_data
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"cat:{idx}")])
    
    keyboard.append([InlineKeyboardButton(text="🔄 Оновити дані", callback_data="refresh_main")])
    
    last_user = load_last_user()
    text = (
        "🚨 АКТУАЛЬНИЙ СКЛАД СЛУЖБИ (ЕВАКУАЦІЯ)\n\n"
        f"🔴 ВСЬОГО НА ТЕРИТОРІЇ: {total_checked} з {total_all} осіб\n"
        f"⏱ Останній оновив: {last_user}\n\n"
        "Натисніть на відділ, щоб переглянути список:"
    )
    return text, InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_category_keyboard(cat_index):
    cat_name = CAT_KEYS[cat_index]
    data = load_data()
    category_data = data.get(cat_name, {})
    
    keyboard = []
    if not category_data:
        keyboard.append([InlineKeyboardButton(text="Список порожній", callback_data="none")])
    else:
        for name, status in category_data.items():
            icon = "✅" if status else "❌"
            btn_text = f"{icon} {name}"
            # Короткий формат для безопасного прохождения лимита байтов
            keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"tgl:{cat_index}:{name}")])
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад до списку", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(Command("start"))
async def cmd_start(message: Message):
    text, markup = get_main_text_and_keyboard()
    await message.answer(text, reply_markup=markup)

@router.callback_query(F.data == "refresh_main")
async def refresh_main(callback: CallbackQuery):
    text, markup = get_main_text_and_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass
    await callback.answer("Дані оновлено!")

@router.callback_query(F.data.startswith("cat:"))
async def open_category(callback: CallbackQuery):
    try:
        cat_idx = int(callback.data.split(":")[1])
        cat_name = CAT_KEYS[cat_idx]
    except Exception:
        await callback.answer("Помилка відкриття")
        return

    keyboard = get_category_keyboard(cat_idx)
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
    text, markup = get_main_text_and_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("tgl:"))
async def toggle_status(callback: CallbackQuery):
    parts = callback.data.split(":", 2)
    if len(parts) < 3:
        await callback.answer()
        return
    
    try:
        cat_idx = int(parts[1])
        cat_name = CAT_KEYS[cat_idx]
    except Exception:
        await callback.answer()
        return

    emp_name = parts[2]
    
    data = load_data()
    if cat_name in data and emp_name in data[cat_name]:
        data[cat_name][emp_name] = not data[cat_name][emp_name]
        save_data(data)
        
        user = callback.from_user
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        if not full_name:
            full_name = user.username or "Користувач"
        save_last_user(full_name)
    
    keyboard = get_category_keyboard(cat_idx)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception:
        pass
    
    await callback.answer("Статус змінено!")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    dp.startup.register(on_startup)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    async def index(request):
        return web.Response(text="Bot is running via Webhooks!")
    app.router.add_get("/", index)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
