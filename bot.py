import asyncio
import json
import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = "8985514206:AAGcI2McxM4mXggd0JdYi7HUefjvmt7kXVQ"

router = Router()
DATA_FILE = "shift_data.json"

DEFAULT_DATA = {
    "categories": {
        "chief": {
            "title": "👤 Керівник служби",
            "employees": {
                "Островий С.Р.": False
            }
        },
        "experts": {
            "title": "🛠 Техексперти",
            "employees": {
                "Хорольський О.В.": False,
                "Мигулько О.О.": False,
                "Склярук А.М.": False,
                "Панкратьєв Є.Ю.": False,
                "Сташко О.В.": False,
                "Рудик Є.М.": False
            }
        },
        "locksmiths": {
            "title": "🔧 Слюсаря тех.",
            "employees": {
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
                "Дробчак М.Р.": False
            }
        },
        "warehouse": {
            "title": "🤖 Роботизований склад",
            "employees": {
                "Вербецький С.І.": False,
                "Незгода А.Д.": False,
                "Пастушенко В.С.": False,
                "Рижавський М.П.": False,
                "Дробчак М.Р.": False
            }
        },
        "emergency": {
            "title": "⚡ Чергові аварійники",
            "employees": {
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
                "Чалий Ю.В.": False
            }
        },
        "eng_op_a": {
            "title": "👷 Інженера+оператори змА",
            "employees": {
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
                "Шумілов В.М.": False
            }
        },
        "eng_op_b": {
            "title": "👷 Інженера+оператори змБ",
            "employees": {
                "Бондаренко М.М.": False,
                "Боченко О.О.": False,
                "Білоус М.В.": False,
                "Вабст П.Л.": False,
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
                "Русс М.О.": False
            }
        }
    },
    "last_updated_by": "Ще ніхто"
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "categories" not in data:
                return DEFAULT_DATA
            return data
    except Exception:
        return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def count_category(cat_data):
    present = sum(1 for status in cat_data["employees"].values() if status)
    total = len(cat_data["employees"])
    return present, total

def get_main_keyboard(data):
    categories = data["categories"]
    keyboard = []
    
    for cat_key, cat_info in categories.items():
        present, total = count_category(cat_info)
        text = f"{cat_info['title']}: {present} / {total}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"open_cat_{cat_key}")])
    
    keyboard.append([InlineKeyboardButton(text="🔄 Оновити дані", callback_data="refresh_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_category_keyboard(cat_key, cat_info):
    keyboard = []
    for name, status in cat_info["employees"].items():
        icon = "✅" if status else "❌"
        btn_text = f"{icon} {name}"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"toggle_{cat_key}_{name}")])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад до списку", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def generate_main_status(data):
    categories = data["categories"]
    total_present = 0
    total_all = 0
    
    lines = ["🚨 АКТУАЛЬНИЙ СКЛАД СЛУЖБИ (ЕВАКУАЦІЯ)\n"]
    for cat_key, cat_info in categories.items():
        present, total = count_category(cat_info)
        total_present += present
        total_all += total
        lines.append(f"• {cat_info['title']}: {present} / {total}")
        
    lines.append(f"\n• 🔴 ВСЬОГО НА ТЕРИТОРІЇ: {total_present} з {total_all} осіб")
    lines.append(f"\n• 🕒 *Останній оновив:* {data['last_updated_by']}")
    return "\n".join(lines)

@router.message(Command("start"))
async def cmd_start(message: Message):
    data = load_data()
    try:
        await message.delete()
    except Exception:
        pass
    
    await message.answer(
        generate_main_status(data),
        reply_markup=get_main_keyboard(data),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "refresh_main")
async def process_refresh(callback: CallbackQuery):
    data = load_data()
    try:
        await callback.message.edit_text(
            generate_main_status(data),
            reply_markup=get_main_keyboard(data),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer("Дані оновлено!")

@router.callback_query(F.data == "back_to_main")
async def process_back(callback: CallbackQuery):
    data = load_data()
    try:
        await callback.message.edit_text(
            generate_main_status(data),
            reply_markup=get_main_keyboard(data),
            parse_mode="Markdown"
        )
