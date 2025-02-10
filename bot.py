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

# ---- Состояния для заказа ----
class OrderState(StatesGroup):
    name = State()
    phone = State()
    address = State()
    confirm = State()

# ---- Главное меню ----
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Παραγγελία", callback_data="order")],
    [InlineKeyboardButton(text="📜 Μενού", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Επικοινωνία", callback_data="contact")]
])

# ---- Кнопка отправки телефона и адреса ----
contact_request = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Στείλτε το τηλέφωνό σας", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

address_request = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Στείλτε την τοποθεσία σας", request_location=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ---- Полное меню (на греческом) ----
menu_text = (
    "📜 **Πλήρες Μενού Momento Cafe Bar**\n\n"
    "🥤 **Χυμοί & Ροφήματα**\n"
    "• Milkshake (Βανίλια, Σοκολάτα, Φράουλα) – 4.00€\n"
    "• Hell – 3.00€\n"
    "• Monster – 3.50€\n"
    "• Χυμός – 3.00€\n"
    "• Αναψυκτικά – 2.50€\n"
    "• Τσάι – 3.00€\n"
    "• Ice Tea – 2.50€\n\n"
    
    "🍫 **Σοκολάτες & Καφές**\n"
    "• Σοκολάτα απλή – 3.00€\n"
    "• Σοκολάτα γεύση – 3.50€\n"
    "• Σοκολάτα βιενουά – 3.50€\n"
    "• Drosspresso – 3.50€\n"
    "• Τριπλό freddo – 3.50€\n"
    "• Ελληνικός (μονός / διπλός) – 2.00€ / 2.50€\n"
    "• Espresso (μονό / διπλό) – 2.00€ / 2.50€\n\n"

    "🍺 **Μπύρες & Ποτά**\n"
    "• Μπύρες (Fischer, Sol, Corona, Breezer, Kaiser) – 4.00€\n"
    "• Heineken, Μάμος, Löwenbräu – 3.50€\n"
    "• Κρασί ποτήρι – 4.00€\n"
    "• Κρασί ποικιλία – 5.00€\n"
    "• Bianco Nero – 5.00€\n"
    "• Vodka / Gin / Ουίσκι – 6.00€\n"
    "• Μαύρα ρούμια – 7.00€\n"
    "• Special (Chivas, Dimple, Jack Daniels, Black Label, Cardhu) – 8.00€\n\n"

    "🍕 **Φαγητό**\n"
    "• Πίτσα – 5.00€\n"
    "• Club Sandwich – 5.00€\n"
    "• Τοστ – 2.50€\n\n"

    "✨ **Extras**\n"
    "• Σιρόπι σε καφέ (+0.50€)\n"
)

# ---- Обработчик кнопки "📜 Μενού" ----
@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(menu_text, parse_mode="Markdown", reply_markup=main_menu)

# ---- Обработчик кнопки "📞 Επικοινωνία" ----
@dp.callback_query(lambda c: c.data == "contact")
async def contact_handler(callback: types.CallbackQuery):
    contact_text = (
        "📞 **Επικοινωνία Momento Cafe Bar**\n\n"
        "📍 **Διεύθυνση:** Kavala, Greece\n"
        "📱 **Τηλέφωνο:** +30 251 039 1646\n"
        "💬 **Telegram:** @momento_support"
    )
    await callback.message.edit_text(contact_text, parse_mode="Markdown", reply_markup=main_menu)

# ---- Обработчик кнопки "🛍 Παραγγελία" ----
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📌 Πληκτρολογήστε το όνομά σας:")
    await state.set_state(OrderState.name)

# ---- Получение имени ----
@dp.message(OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Στείλτε το τηλέφωνό σας πατώντας το κουμπί παρακάτω:", reply_markup=contact_request)
    await state.set_state(OrderState.phone)

# ---- Получение телефона ----
@dp.message(OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text if message.text else message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer("📍 Στείλτε την τοποθεσία σας πατώντας το κουμπί παρακάτω:", reply_markup=address_request)
    await state.set_state(OrderState.address)

# ---- Получение адреса ----
@dp.message(OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text if message.text else f"📍 Τοποθεσία: {message.location.latitude}, {message.location.longitude}"
    await state.update_data(address=address)
    data = await state.get_data()

    order_summary = (
        "📦 **Νέα Παραγγελία**\n\n"
        f"👤 **Όνομα:** {data['name']}\n"
        f"📞 **Τηλέφωνο:** {data['phone']}\n"
        f"📍 **Διεύθυνση:** {data['address']}\n\n"
        "📌 **Επικοινωνήστε με τον πελάτη για επιβεβαίωση!**"
    )

    await message.answer(order_summary, parse_mode="Markdown", reply_markup=main_menu)
    await state.clear()

# ---- Обработчик кнопки "Επιστροφή" ----
@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Μπορείτε να κάνετε μια παραγγελία, να δείτε το μενού ή να επικοινωνήσετε μαζί μας.",
        reply_markup=main_menu
    )

# ---- Команда /start ----
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Καλώς ήρθατε στο **Momento Cafe Bar**! ☕️🍹\n\n"
        "Μπορείτε να κάνετε παραγγελία, να δείτε το μενού ή να επικοινωνήσετε μαζί μας.",
        reply_markup=main_menu
    )

# ---- Запуск бота ----
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())