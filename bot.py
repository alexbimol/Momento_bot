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

# Проверяем, загружен ли токен
if not TOKEN:
    raise ValueError("Ошибка: Токен не загружен! Проверь .env или переменные окружения.")

bot = Bot(token="7776292962:AAHQiJNdilk6D6_nNP07E-PfN8gDmm8rD8I")
dp = Dispatcher()

# Состояния для заказа
class OrderState(StatesGroup):
    name = State()
    address = State()
    order = State()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Заказать", callback_data="order")],
    [InlineKeyboardButton(text="📞 Связаться", callback_data="contact")],
    [InlineKeyboardButton(text="📜 Меню", callback_data="menu")]
])

# Меню заказа
order_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☕ Кофе", callback_data="order_coffee"),
     InlineKeyboardButton(text="🍹 Коктейли", callback_data="order_cocktails")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
])

# Кнопки для ввода данных клиента
request_contact = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Отправить адрес", request_location=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Добро пожаловать в Momento Cafe Bar! ☕️🍹\n\n"
        "Вы можете легко оформить заказ, посмотреть меню или связаться с нами.",
        reply_markup=main_menu
    )

# Обработчик кнопки "🛍 Заказать"
@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(OrderState.name)

# Получение имени клиента
@dp.message(OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш адрес доставки:", reply_markup=request_contact)
    await state.set_state(OrderState.address)

# Получение адреса клиента
@dp.message(OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    address = message.text if message.text else f"📍 Локация: {message.location.latitude}, {message.location.longitude}"
    await state.update_data(address=address)
    await message.answer("Введите, что вы хотите заказать:")
    await state.set_state(OrderState.order)

# Получение заказа клиента
@dp.message(OrderState.order)
async def get_order(message: types.Message, state: FSMContext):
    await state.update_data(order=message.text)
    data = await state.get_data()

    order_info = (f"📝 **Новый заказ:**\n\n"
                  f"👤 Имя: {data['name']}\n"
                  f"📍 Адрес: {data['address']}\n"
                  f"🍽 Заказ: {data['order']}\n\n"
                  f"📞 Свяжитесь с клиентом для подтверждения!")

    await message.answer(order_info, parse_mode="Markdown", reply_markup=main_menu)
    await state.clear()

# Обработчик кнопки "📜 Меню"
@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите категорию меню:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="☕ Χυμοί & Ροφήματα", callback_data="menu_juices")],
            [InlineKeyboardButton(text="🍫 Σοκολάτες", callback_data="menu_chocolates")],
            [InlineKeyboardButton(text="🍺 Μπύρες & Ποτά", callback_data="menu_drinks")],
            [InlineKeyboardButton(text="🍕 Φαγητό", callback_data="menu_food")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )

# Меню с ценами
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
    await callback.message.edit_text(
        menu_text[callback.data],
        parse_mode="Markdown"
    )

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())