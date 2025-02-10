import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token="7776292962:AAHj3yUt0Kpw54AFOP998u3VJd-E1w8KFKA")
dp = Dispatcher()

# ---- Состояния для заказа ----
class OrderState(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    confirming_order = State()
    phone = State()
    address = State()

# ---- Меню товаров ----
menu_items = {
    "🥤 Ροφήματα": [
        ("Milkshake", 4.00),
        ("Hell", 3.00),
        ("Monster", 3.50),
        ("Χυμός", 3.00),
    ],
    "🍫 Καφές & Σοκολάτες": [
        ("Σοκολάτα απλή", 3.00),
        ("Espresso", 2.50),
        ("Freddo Cappuccino", 3.50),
    ],
    "🍺 Ποτά": [
        ("Heineken", 3.50),
        ("Corona", 4.00),
        ("Vodka", 6.00),
    ],
    "🍕 Φαγητό": [
        ("Πίτσα", 5.00),
        ("Club Sandwich", 5.00),
        ("Τοστ", 2.50),
    ]
}

# ---- Главное меню ----
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Παραγγελία", callback_data="order")],
    [InlineKeyboardButton(text="📜 Μενού", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Επικοινωνία", callback_data="contact")]
])

# ---- Выбор категории ----
category_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}")] for cat in menu_items.keys()
    ] + [[InlineKeyboardButton(text="✅ Επιβεβαίωση Παραγγελίας", callback_data="confirm_order")]]
)

# ---- Обработчик кнопки "🛍 Παραγγελία" ----
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(order={})  # Обнуляем заказ
    await callback.message.answer("📌 Επιλέξτε κατηγορία:", reply_markup=category_menu)
    await state.set_state(OrderState.choosing_category)

# ---- Выбор категории ----
@dp.callback_query(lambda c: c.data.startswith("category_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.replace("category_", "")
    items = menu_items.get(category, [])
    
    # Формируем кнопки для выбора товаров
    product_buttons = [
        [
            InlineKeyboardButton(text=f"{name} - {price:.2f}€", callback_data=f"product_{name}"),
            InlineKeyboardButton(text="➕", callback_data=f"add_{name}")
        ]
        for name, price in items
    ]

    product_menu = InlineKeyboardMarkup(inline_keyboard=product_buttons + [[InlineKeyboardButton(text="⬅️ Πίσω", callback_data="back_to_categories")]])
    await callback.message.edit_text(f"🛒 **{category}**\n\nΕπιλέξτε προϊόν:", parse_mode="Markdown", reply_markup=product_menu)

# ---- Добавление товара ----
@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_product(callback: types.CallbackQuery, state: FSMContext):
    product = callback.data.replace("add_", "")
    data = await state.get_data()
    order = data.get("order", {})

    if product in order:
        order[product] += 1
    else:
        order[product] = 1

    await state.update_data(order=order)
    await callback.answer(f"✅ Προστέθηκε {product} (Σύνολο: {order[product]})")

# ---- Возврат к категориям ----
@dp.callback_query(lambda c: c.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery):
    await callback.message.edit_text("📌 Επιλέξτε κατηγορία:", reply_markup=category_menu)

# ---- Подтверждение заказа ----
@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order = data.get("order", {})

    if not order:
        await callback.answer("🚫 Δεν έχετε προσθέσει προϊόντα!", show_alert=True)
        return

    order_text = "\n".join([f"• {item} x{count}" for item, count in order.items()])
    total_price = sum(menu_items[cat][[i[0] for i in menu_items[cat]].index(item)][1] * count for cat in menu_items for item, count in order.items())

    await callback.message.answer(f"🛒 **Η παραγγελία σας**:\n\n{order_text}\n\n💰 **Σύνολο: {total_price:.2f}€**\n\n📱 Στείλτε το τηλέφωνό σας:", reply_markup=contact_request)
    await state.set_state(OrderState.phone)

# ---- Получение телефона ----
@dp.message(OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text if message.text else message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer("📍 Στείλτε την τοποθεσία σας:", reply_markup=address_request)
    await state.set_state(OrderState.address)

# ---- Получение адреса ----
@dp.message(OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text if message.text else f"📍 Τοποθεσία: {message.location.latitude}, {message.location.longitude}"
    data = await state.get_data()

    order_summary = (
        "📦 **Νέα Παραγγελία**\n\n"
        f"📞 **Τηλέφωνο:** {data['phone']}\n"
        f"📍 **Διεύθυνση:** {address}\n\n"
        "🛒 **Παραγγελία:**\n"
        + "\n".join([f"• {item} x{count}" for item, count in data["order"].items()])
        + f"\n💰 **Σύνολο: {sum(menu_items[cat][[i[0] for i in menu_items[cat]].index(item)][1] * count for cat in menu_items for item, count in data['order'].items()):.2f}€**\n\n"
        "📌 **Επικοινωνήστε με τον πελάτη για επιβεβαίωση!**"
    )

    await message.answer(order_summary, parse_mode="Markdown", reply_markup=main_menu)
    await state.clear()

# ---- Команда /start ----
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Καλώς ήρθατε στο **Momento Cafe Bar**! ☕️🍹", reply_markup=main_menu)

# ---- Запуск бота ----
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())