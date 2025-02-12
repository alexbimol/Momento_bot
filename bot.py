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

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ Ошибка: Токен бота не найден! Проверь переменные окружения.")

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
  # Убрал parse_mode из bot = Bot(token=TOKEN, parse_mode="HTML")

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Проверяем токен перед запуском
async def check_token():
    try:
        user = await bot.get_me()
        logging.info(f"✅ Бот запущен: @{user.username}")
    except Exception as e:
        logging.error(f"❌ Ошибка с токеном: {e}")
        exit("Ошибка: Проверь токен в BotFather!")

# Состояния FSM
class OrderState(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    name = State()
    phone = State()
    address = State()
    confirmation = State()

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Παραγγελία", callback_data="order")],
    [InlineKeyboardButton(text="📜 Μενού", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Επικοινωνία", url="tel:+302510391646")]
])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logging.info(f"📩 Команда /start от {message.from_user.id}")
    await message.answer(
        "👋 Καλώς ήρθατε στο <b>Momento Cafe Bar</b>! ☕️🍹\n\n"
        "Μπορείτε να κάνετε παραγγελία, να δείτε το μενού ή να επικοινωνήσετε μαζί μας.",
        reply_markup=main_menu
    )

async def main():
    await check_token()
    dp.include_router(dp)
    logging.info("🔹 Запуск polling...")
    print("🔹 Бот запущен. Ожидаю сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("❌ Бот остановлен вручную.")