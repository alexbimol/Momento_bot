import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=7776292962:AAHQiJNdilk6D6_nNP07E-PfN8gDmm8rD8I)
dp = Dispatcher()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Заказать", callback_data="order")],
    [InlineKeyboardButton(text="📞 Связаться", callback_data="contact")]
])

# Меню заказа
order_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☕ Кофе", callback_data="order_coffee"),
     InlineKeyboardButton(text="🍹 Коктейли", callback_data="order_cocktails")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Momento Cafe Bar! ☕🍹\n\n"
        "Вы можете легко оформить заказ или связаться с нами.",
        reply_markup=main_menu
    )

# Обработчик кнопки "🛍 Заказать"
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Что вы хотите заказать?",
        reply_markup=order_menu
    )

# Обработчик кнопки "📞 Связаться"
@dp.callback_query(lambda c: c.data == "contact")
async def contact_handler(callback: types.CallbackQuery):
    contact_info = (
        "📞 Свяжитесь с нами:\n"
        "📍 Адрес: Kavala, Greece\n"
        "📱 Телефон: +30 251 039 1646\n"
        "💬 Telegram: @momento_support"
    )
    await callback.message.answer(contact_info)

# Обработчик выбора напитков
@dp.callback_query(lambda c: c.data in ["order_coffee", "order_cocktails"])
async def choose_drink(callback: types.CallbackQuery):
    drink_type = "кофе" if callback.data == "order_coffee" else "коктейли"
    await callback.message.answer(
        f"Вы выбрали {drink_type}. Оформить заказ можно по телефону: +30 251 039 1646"
    )

# Кнопка "Назад"
@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Вы можете легко оформить заказ или связаться с нами.",
        reply_markup=main_menu
    )

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())