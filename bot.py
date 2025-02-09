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

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Заказать", callback_data="order")],
    [InlineKeyboardButton(text="📞 Связаться", callback_data="contact")],
    [InlineKeyboardButton(text="📜 Меню", callback_data="menu")]
])

# Кнопки категорий меню
menu_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☕ Χυμοί & Ροφήματα", callback_data="menu_juices")],
    [InlineKeyboardButton(text="🍫 Σοκολάτες", callback_data="menu_chocolates")],
    [InlineKeyboardButton(text="🍺 Μπύρες & Ποτά", callback_data="menu_drinks")],
    [InlineKeyboardButton(text="🍕 Φαγητό", callback_data="menu_food")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Momento Cafe Bar! ☕🍹\n\n"
        "Вы можете легко оформить заказ, посмотреть меню или связаться с нами.",
        reply_markup=main_menu
    )

# Обработчик кнопки "📜 Меню"
@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию меню:",
        reply_markup=menu_categories
    )

# Меню по категориям
menu_text = {
    "menu_juices": "**Χυμοί & Ροφήματα**\n"
                   "• Milkshake (Βανίλια / Σοκολάτα / Φράουλα) – 4.00€\n"
                   "• Hell – 3.00€\n"
                   "• Monster – 3.50€\n"
                   "• Χυμός – 3.00€\n"
                   "• Αναψυκτικά – 2.50€\n"
                   "• Τσάι – 3.00€\n"
                   "• Ice Tea – 2.50€",

    "menu_chocolates": "**Σοκολάτες**\n"
                       "• Σοκολάτα απλή – 3.00€\n"
                       "• Σοκολάτα γεύση – 3.50€\n"
                       "• Σοκολάτα βιενουά – 3.50€\n"
                       "• Drosspresso – 3.50€\n"
                       "• Τριπλό freddo – 3.50€\n"
                       "• Ελληνικός (μονός / διπλός) – 2.00€ / 2.50€\n"
                       "• Espresso (μονό / διπλό) – 2.00€ / 2.50€",

    "menu_drinks": "**Μπύρες & Ποτά**\n"
                   "• Μπύρες (Fischer, Sol, Corona, Breezer, Kaiser) – 4.00€\n"
                   "• Heineken, Μάμος, Löwenbräu – 3.50€\n"
                   "• Κρασί ποτήρι – 4.00€\n"
                   "• Κρασί ποικιλία – 5.00€\n"
                   "• Bianco Nero – 5.00€\n"
                   "• Vodka / Gin / Ουίσκι – 6.00€\n"
                   "• Μαύρα ρούμια – 7.00€\n"
                   "• Special (Chivas, Dimple, Jack Daniels, Black Label, Cardhu) – 8.00€",

    "menu_food": "**Φαγητό**\n"
                 "• Πίτσα – 5.00€\n"
                 "• Club Sandwich – 5.00€\n"
                 "• Τοστ – 2.50€\n"
                 "\n**Extras**\n"
                 "• Σιρόπι σε καφέ (+0.50€)"
}

# Обработчик выбора категории меню
@dp.callback_query(lambda c: c.data in menu_text.keys())
async def send_menu_category(callback: types.CallbackQuery):
    category = callback.data
    await callback.message.edit_text(
        menu_text[category],
        reply_markup=menu_categories,
        parse_mode="Markdown"
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

# Кнопка "Назад"
@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Вы можете легко оформить заказ, посмотреть меню или связаться с нами.",
        reply_markup=main_menu
    )

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())