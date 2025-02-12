import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Проверка токена
if not TOKEN:
    raise ValueError("❌ Ошибка: Токен бота не найден! Проверь переменные окружения.")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Классы состояний FSM
class OrderState(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    name = State()
    phone = State()
    address = State()
    confirmation = State()

# Полное меню Momento Cafe Bar
menu_items = {
    "🥤 Χυμοί & Ροφήματα": [
        ("Milkshake (Βανίλια / Σοκολάτα / Φράουλα)", 4.00),
        ("Hell", 3.00),
        ("Monster", 3.50),
        ("Χυμός", 3.00),
        ("Αναψυκτικά", 2.50),
        ("Τσάι", 3.00),
        ("Ice Tea", 2.50),
    ],
    "🍫 Σοκολάτες": [
        ("Σοκολάτα απλή", 3.00),
        ("Σοκολάτα γεύση", 3.50),
        ("Σοκολάτα βιενουά", 3.50),
        ("Drosspresso", 3.50),
        ("Τριπλό freddo", 3.50),
        ("Ελληνικός (μονός)", 2.00),
        ("Ελληνικός (διπλός)", 2.50),
        ("Espresso (μονό)", 2.00),
        ("Espresso (διπλό)", 2.50),
    ],
    "🍺 Μπύρες & Ποτά": [
        ("Μπύρες (Fischer, Sol, Corona, Breezer, Kaiser)", 4.00),
        ("Heineken, Μάμος, Löwenbräu", 3.50),
        ("Κρασί ποτήρι", 4.00),
        ("Κρασί ποικιλία", 5.00),
        ("Bianco Nero", 5.00),
        ("Vodka / Gin / Ουίσκι", 6.00),
        ("Μαύρα ρούμια", 7.00),
        ("Special (Chivas, Dimple, Jack Daniels, Black Label, Cardhu)", 8.00),
    ],
    "🍕 Φαγητό": [
        ("Πίτσα", 5.00),
        ("Club Sandwich", 5.00),
        ("Τοστ", 2.50),
    ],
    "✨ Extras": [
        ("Σιρόπι σε καφέ", 0.50),
    ]
}

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Παραγγελία", callback_data="order")],
    [InlineKeyboardButton(text="📜 Μενού", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Επικοινωνία", url="tel:+302510391646")]  # Кнопка с телефоном
])

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logging.info(f"📩 Команда /start от {message.from_user.id}")
    await message.answer(
        "👋 Καλώς ήρθατε στο <b>Momento Cafe Bar</b>! ☕️🍹\n\n"
        "Μπορείτε να κάνετε παραγγελία, να δείτε το μενού ή να επικοινωνήσετε μαζί μας.",
        reply_markup=main_menu
    )

# Обработчик меню
@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    menu_text = "\n\n".join([
        f"🍽 <b>{cat}</b>\n" + "\n".join([f"• {name} – {price:.2f}€" for name, price in items])
        for cat, items in menu_items.items()
    ])
    await callback.message.edit_text(f"📜 <b>Μενού</b>\n\n{menu_text}", parse_mode="HTML", reply_markup=main_menu)

# Обработчик заказа
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(order={})
    category_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"category_{i}")] for i, cat in enumerate(menu_items.keys())
    ] + [[InlineKeyboardButton(text="✅ Επιβεβαίωση Παραγγελίας", callback_data="confirm_order")]])

    await callback.message.edit_text("📌 Επιλέξτε κατηγορία:", reply_markup=category_menu)
    await state.set_state(OrderState.choosing_category)

# Обработчик выбора категории
@dp.callback_query(lambda c: c.data.startswith("category_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    category_index = int(callback.data.split("_")[1])
    category_name = list(menu_items.keys())[category_index]
    items = menu_items[category_name]

    product_buttons = [
        [InlineKeyboardButton(text=f"{name} - {price:.2f}€", callback_data=f"add_{name}")]
        for name, price in items
    ]

    product_menu = InlineKeyboardMarkup(inline_keyboard=product_buttons + [[InlineKeyboardButton(text="⬅️ Πίσω", callback_data="order")]])
    await callback.message.edit_text(f"🛒 <b>{category_name}</b>\n\nΕπιλέξτε προϊόν:", parse_mode="HTML", reply_markup=product_menu)

# Обработчик добавления продукта
@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_product(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data[4:]
    user_data = await state.get_data()

    order = user_data.get("order", {})
    order[product_name] = order.get(product_name, 0) + 1

    await state.update_data(order=order)
    await callback.answer(f"✅ {product_name} προστέθηκε στην παραγγελία!", show_alert=False)

# Функция запуска бота
async def main():
    logging.info("🔹 Бот запускается...")
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("❌ Бот остановлен вручную.")