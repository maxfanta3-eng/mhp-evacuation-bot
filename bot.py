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
DATA_FILE = "shift_data_v3.json"

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
            }
        },
        "warehouse": {
            "title": "🤖 Роботизований склад",
            "employees": {
                "Вербецький С.І.": False,
                "Незгода А.Д.": False,
                "Пастушенко В.С.": False,
                "Рижавський М.П.": False,
                "Дробчак М.Р.": False,
                "Вабст П.Л.": False,
            }
        },
        "emergency": {
            "title": "⚡ Чергові аварійники",
            "employees": {
                "Король А.І.": False,
                "Гарник О.Г.": False,
                "Коваленко М.С.": False,
                "Олійник Ю.В.": False,
                "Ладанюк С.М.": False,
                "Петровський Д.О.": False,
                "Кольцов О.Д.": False,
                "Стороженко В.С.": False,
                "Степаненко Д.А.": False,
                "Мисько І.І.": False,
                "Мельник В.В.": False,
                "Чалий Ю.В.": False
            }
        },
        "eng_op_a": {
            "title": "👷 Інженера+оператори змА",
            "employees": {
                "Баланюк В.Ю.": False,
                "Барков Ю.М.": False,
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
                "Денисюк С.В.": False,
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
                "Пшеничний В.О.": False,
                "Русецький С.С.": False,
                "Русяновський Р.О.": False,
                "Сасюк Д.Ю.": False,
                "Томашевський О.П.": False,
                "Торішній О.Г.": False,
                "Федічев М.В.": False,
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
                "Гуцол І.Д.": False,
                "Головащенко О.М.": False,
                "Грушовий О.В.": False,
                "Грицик А.В.": False,
                "Давидюк Д.А.": False,
                "Дубенко С.О.": False,
                "Єпанчинцев В.В.": False,
                "Ільїнов Д.": False,
                "Клещ В.А.": False,
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
                "Боднар А.С.": False,
                "Лещенко В.В.": False,
                "Колодій А.Г.": False,
                "Цурман О.О.": False,
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

import os
import json

DATA_FILE = "shift_data_v3.json"

def load_data():
    # Якщо файл існує, спробуємо його прочитати
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "categories" in data and "eng_op_a" in data["categories"]:
                    return data
        except Exception:
            pass
    
    # Якщо файлу немає або він битий — повертаємо копію базових даних і одразу зберігаємо
    data = DEFAULT_DATA.copy()
    save_data(data)
    return data

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Save error: {e}")

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
    for i, (name, status) in enumerate(cat_info["employees"].items()):
        icon = "✅" if status else "❌"
        btn_text = f"{icon} {name}"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"tog_{cat_key}_{i}")])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад до списку", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data.startswith("tog_"))
async def process_toggle_employee(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    if len(parts) == 3:
        cat_key = parts[1]
        try:
            emp_index = int(parts[2])
            data = load_data()
            user_name = callback.from_user.full_name
            
            if cat_key in data["categories"]:
                employees = data["categories"][cat_key]["employees"]
                names_list = list(employees.keys())
                
                if 0 <= emp_index < len(names_list):
                    name = names_list[emp_index]
                    current_status = employees[name]
                    employees[name] = not current_status
                    data["last_updated_by"] = user_name
                    save_data(data)
                    
                    cat_info = data["categories"][cat_key]
                    try:
                        await callback.message.edit_text(
                            f"📋 Список: {cat_info['title']}\nНатисніть на прізвище, щоб змінити статус (✅ / ❌):",
                            reply_markup=get_category_keyboard(cat_key, cat_info),
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Edit error: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
            pass
    try:
        await callback.answer("Статус змінено!")
    except Exception:
        pass

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
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("open_cat_"))
async def process_open_category(callback: CallbackQuery):
    cat_key = callback.data.replace("open_cat_", "")
    data = load_data()
    if cat_key in data["categories"]:
        cat_info = data["categories"][cat_key]
        try:
            await callback.message.edit_text(
                f"📋 Список: {cat_info['title']}\nНатисніть на прізвище, щоб змінити статус (✅ / ❌):",
                reply_markup=get_category_keyboard(cat_key, cat_info),
                parse_mode="Markdown"
            )
        except Exception:
            pass
    await callback.answer()

def get_category_keyboard(cat_key, cat_info):
    keyboard = []
    for i, (name, status) in enumerate(cat_info["employees"].items()):
        icon = "✅" if status else "❌"
        btn_text = f"{icon} {name}"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"tog_{cat_key}_{i}")])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад до списку", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data.startswith("tog_"))
async def process_toggle_employee(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    if len(parts) == 3:
        cat_key = parts[1]
        emp_index = int(parts[2])
        data = load_data()
        user_name = callback.from_user.full_name
        
        if cat_key in data["categories"]:
            employees = data["categories"][cat_key]["employees"]
            names_list = list(employees.keys())
            
            if 0 <= emp_index < len(names_list):
                name = names_list[emp_index]
                current_status = employees[name]
                employees[name] = not current_status
                data["last_updated_by"] = user_name
                save_data(data)
                
           cat_info = data["categories"][cat_key]
                
                # Завантажуємо свіжі дані для генератора клавіатури
                fresh_data = load_data()
                fresh_cat_info = fresh_data["categories"][cat_key]
                
                try:
                    await callback.message.edit_text(
                        f"📋 Список: {cat_info['title']}\nНатисніть на прізвище, щоб змінити статус (✅ / ❌):\n⏱ {time.time()}",
                        reply_markup=get_category_keyboard(cat_key, fresh_cat_info),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Edit error: {e}")

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

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    asyncio.run(main())
