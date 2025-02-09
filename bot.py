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

bot = Bot(token="7776292962:AAHj3yUt0Kpw54AFOP998u3VJd-E1w8KFKA")
dp = Dispatcher()

# ---- Состояния для оформления заказа ----
class OrderState(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()

# ---- Меню с продуктами ----
products = {
    "milkshake": {"name": "Milkshake", "price": 4.00, "count": 0},
    "hell": {"name": "Hell Energy", "price": 3.00, "count": 0},
    "monster": {"name": "Monster", "price": 3.50, "count": 0},
    "juice": {"name": "Χυμός", "price": 3.00, "count": 0},
    "soda": {"name": "Αναψυκτικά", "price": 2.50, "count": 0},
    "tea": {"name": "Τσάι", "price": 3.00, "count": 0},
    "ice_tea": {"name": "Ice Tea", "price": 2.50, "count": 0},
    "simple_chocolate": {"name": "Σοκολάτα απλή", "price": 3.00, "count": 0},
    "flavored_chocolate": {"name": "Σοκολάτα γεύση", "price": 3.50, "count": 0},
    "viennese_chocolate": {"name": "Σοκολάτα βιενουά", "price": 3.50, "count": 0},
    "drosspresso": {"name": "Drosspresso", "price": 3.50, "count": 0},
    "triple_freddo": {"name": "Τριπλό freddo", "price": 3.50, "count": 0},
    "greek_coffee": {"name": "Ελληνικός (μονός / διπλός)", "price": 2.00, "count": 0},
    "espresso": {"name": "Espresso (μονό / διπλό)", "price": 2.00, "count": 0},
    "beer": {"name": "Μπύρες (Fischer, Sol, Corona, Breezer, Kaiser)", "price": 4.00, "count": 0},
    "wine_glass": {"name": "Κρασί ποτήρι", "price": 4.00, "count": 0},
    "special_wine": {"name": "Κρασί ποικιλία", "price": 5.00, "count": 0},
    "bianco_nero": {"name": "Bianco Nero", "price": 5.00, "count": 0},
    "vodka_gin_whiskey": {"name": "Vodka / Gin / Ουίσκι", "price": 6.00, "count": 0},
    "dark_rum": {"name": "Μαύρα ρούμια", "price": 7.00, "count": 0},
    "special_drinks": {"name": "Special (Chivas, Dimple, Jack Daniels, Black Label, Cardhu)", "price": 8.00, "count": 0},
    "pizza": {"name": "Πίτσα", "price": 5.00, "count": 0},
    "sandwich": {"name": "Club Sandwich", "price": 5.00, "count": 0},
    "toast": {"name": "Τοστ", "price": 2.50, "count": 0},
    "coffee_syrup": {"name": "Σιρόπι σε καφέ", "price": 0.50, "count": 0}
}

def generate_product_menu():
    """Создаёт кнопки с продуктами и кнопками + / -"""
    buttons = []
    for key, product in products.items():
        buttons.append([
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{key}"),
            InlineKeyboardButton(text=f"{product['name']} ({product['count']})", callback_data="none"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{key}")
        ])
    buttons.append([InlineKeyboardButton(text="✅ Оформить заказ", callback_data="confirm_order")])
    buttons.append([InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ---- Главное меню ----
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Заказать", callback_data="order"),
     InlineKeyboardButton(text="📜 Меню", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Связаться", callback_data="contact")]
])

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
    await callback.answer()
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

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=generate_product_menu())

# ---- Очистка корзины ----
@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    for key in products:
        products[key]["count"] = 0
    await callback.answer("Корзина очищена!")
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

# ---- Запуск бота ----
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())