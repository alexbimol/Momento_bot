import logging
import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")  # Должен быть в переменных Railway

if not TOKEN:
    raise ValueError("❌ Ошибка: Токен бота не найден! Проверь переменные окружения.")

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния FSM
class OrderState(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    confirmation = State()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Сделать заказ", callback_data="order")],
    [InlineKeyboardButton(text="📜 Посмотреть меню", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")]
])

# Меню товаров
menu_items = {
    "Кофе ☕": [("Эспрессо", 2.50), ("Американо", 3.00), ("Капучино", 3.50)],
    "Чай 🍵": [("Чёрный чай", 2.00), ("Зелёный чай", 2.00), ("Фруктовый чай", 2.50)],
    "Напитки 🥤": [("Сок апельсиновый", 3.00), ("Кока-Кола", 2.50)]
}

# Команда старт
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logging.info(f"📩 Команда /start от {message.from_user.id}")
    await message.answer(
        "👋 Добро пожаловать в <b>Momento Cafe Bar</b>! ☕🍹\n\n"
        "Вы можете сделать заказ, посмотреть меню или связаться с нами.",
        reply_markup=main_menu
    )

# Обработчик меню
@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    menu_text = "\n\n".join([
        f"🍽 <b>{cat}</b>\n" + "\n".join([f"• {name} — {price:.2f}€" for name, price in items])
        for cat, items in menu_items.items()
    ])
    await callback.message.edit_text(f"📜 <b>Меню</b>\n\n{menu_text}", reply_markup=main_menu)

# Обработчик контактов
@dp.callback_query(lambda c: c.data == "contacts")
async def show_contacts(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📞 <b>Контактная информация</b>\n\n"
        "📍 <b>Адрес:</b> Кавала, Греция\n"
        "📞 <b>Телефон:</b> +30 251 039 1646\n"
        "✉️ <b>Telegram:</b> @momento_support",
        reply_markup=main_menu
    )

# Обработчик заказа (выбор категории)
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    category_buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"category_{i}")]
        for i, cat in enumerate(menu_items.keys())
    ]
    category_menu = InlineKeyboardMarkup(inline_keyboard=category_buttons + [[InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]])

    await callback.message.edit_text("📌 Выберите категорию:", reply_markup=category_menu)
    await state.set_state(OrderState.choosing_category)

# Выбор продукта в категории
@dp.callback_query(lambda c: c.data.startswith("category_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    category_index = int(callback.data.split("_")[1])
    category_name = list(menu_items.keys())[category_index]
    items = menu_items[category_name]

    product_buttons = [
        [InlineKeyboardButton(text=f"{name} - {price:.2f}€", callback_data=f"add_{name}")]
        for name, price in items
    ]

    product_menu = InlineKeyboardMarkup(inline_keyboard=product_buttons + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="order")]])
    await callback.message.edit_text(f"🛒 <b>{category_name}</b>\n\nВыберите продукт:", reply_markup=product_menu)

# Добавление товара в заказ
@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_product(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data[4:]
    user_data = await state.get_data()

    order = user_data.get("order", {})
    order[product_name] = order.get(product_name, 0) + 1

    await state.update_data(order=order)
    await callback.answer(f"✅ {product_name} добавлен в заказ!")

# Запуск бота
async def main():
    logging.info("🔹 Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("❌ Бот остановлен вручную.")