import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

# Загружаем токен
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token="7776292962:AAHM5hxD-jHPHrAxdI5SumSD4EQpWOlmIC8")
dp = Dispatcher()

# ---- Состояния для оформления заказа ----
class OrderState(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()

# ---- Меню с продуктами ----
products = {
    "coffee": {"name": "☕ Кофе", "price": 3.50, "count": 0},
    "cocktail": {"name": "🍹 Коктейль", "price": 5.00, "count": 0},
    "pizza": {"name": "🍕 Пицца", "price": 7.00, "count": 0}
}

def generate_product_menu():
    """Создаёт кнопки с продуктами и кнопками + / -"""
    buttons = []
    for key, product in products.items():
        buttons.append([
            InlineKeyboardButton(text=f"➖", callback_data=f"decrease_{key}"),
            InlineKeyboardButton(text=f"{product['name']} ({product['count']})", callback_data=f"none"),
            InlineKeyboardButton(text=f"➕", callback_data=f"increase_{key}")
        ])
    buttons.append([InlineKeyboardButton(text="✅ Оформить заказ", callback_data="confirm_order")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ---- Главное меню ----
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Заказать", callback_data="order"),
     InlineKeyboardButton(text="📜 Меню", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Связаться", callback_data="contact")]
])

# ---- Кнопки для отправки контакта и адреса ----
contact_request = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Отправить телефон", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

address_request = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Отправить адрес", request_location=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ---- Команда /start ----
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Momento Cafe Bar! ☕️🍹\n\n"
        "Вы можете оформить заказ, посмотреть меню или связаться с нами.",
        reply_markup=main_menu
    )

# ---- Обработчик кнопки "🛍 Заказать" ----
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите продукты:", reply_markup=generate_product_menu())

# ---- Увеличение и уменьшение количества ----
@dp.callback_query(lambda c: c.data.startswith("increase_") or c.data.startswith("decrease_"))
async def modify_product_count(callback: types.CallbackQuery):
    action, product_key = callback.data.split("_")
    if product_key in products:
        if action == "increase":
            products[product_key]["count"] += 1
        elif action == "decrease" and products[product_key]["count"] > 0:
            products[product_key]["count"] -= 1

    await callback.message.edit_reply_markup(reply_markup=generate_product_menu())

# ---- Подтверждение заказа ----
@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    total_price = sum(p["count"] * p["price"] for p in products.values())
    if total_price == 0:
        await callback.answer("Выберите хотя бы один продукт!", show_alert=True)
        return

    order_text = "🛒 **Ваш заказ:**\n\n"
    for product in products.values():
        if product["count"] > 0:
            order_text += f"• {product['name']} x {product['count']} = {product['count'] * product['price']}€\n"

    order_text += f"\n💰 **Итого:** {total_price}€\n\nВведите ваше имя:"
    await callback.message.answer(order_text, parse_mode="Markdown")
    await state.set_state(OrderState.name)

# ---- Получение имени ----
@dp.message(OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введите ваш номер телефона или отправьте его кнопкой ниже:", reply_markup=contact_request)
    await state.set_state(OrderState.phone)

# ---- Получение телефона ----
@dp.message(OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text if message.text else message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer("📍 Введите ваш адрес или отправьте геолокацию кнопкой ниже:", reply_markup=address_request)
    await state.set_state(OrderState.address)

# ---- Получение адреса и подтверждение ----
@dp.message(OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text if message.text else f"📍 Локация: {message.location.latitude}, {message.location.longitude}"
    await state.update_data(address=address)
    data = await state.get_data()

    order_summary = (f"📝 **Новый заказ:**\n\n"
                     f"👤 Имя: {data['name']}\n"
                     f"📞 Телефон: {data['phone']}\n"
                     f"📍 Адрес: {data['address']}\n\n"
                     f"🛍 **Детали заказа:**\n")

    for product in products.values():
        if product["count"] > 0:
            order_summary += f"• {product['name']} x {product['count']} = {product['count'] * product['price']}€\n"

    order_summary += "\n📞 Свяжитесь с клиентом для подтверждения!"

    await message.answer(order_summary, parse_mode="Markdown", reply_markup=main_menu)
    await state.clear()

# ---- Обработчик кнопки "📞 Связаться" ----
@dp.callback_query(lambda c: c.data == "contact")
async def contact_handler(callback: types.CallbackQuery):
    await callback.message.answer(
        "📞 Свяжитесь с нами:\n📍 Адрес: Kavala, Greece\n📱 Телефон: +30 251 039 1646\n💬 Telegram: @momento_support"
    )

# ---- Запуск бота ----
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())