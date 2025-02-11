import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = "7640783920:AAFktcYES5xv_-OLHR2CVwOq2jDL968SqxY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    choosing_category = State()
    phone = State()
    address = State()

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
    "🍫 Σοκολάτες & Καφές": [
        ("Σοκολάτα απλή", 3.00),
        ("Σοκολάτα γεύση", 3.50),
        ("Σοκολάτα βιενουά", 3.50),
        ("Drosspresso", 3.50),
        ("Τριπλό freddo", 3.50),
        ("Ελληνικός (μονός / διπλός)", 2.00),
        ("Espresso (μονό / διπλό)", 2.00),
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

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Παραγγελία", callback_data="order")],
    [InlineKeyboardButton(text="📜 Μενού", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Επικοινωνία", callback_data="contact")]
])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 Καλώς ήρθατε στο **Momento Cafe Bar**! ☕️🍹",
        reply_markup=main_menu
    )

@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    menu_text = "\n\n".join([
        f"🍽 **{cat}**\n" + "\n".join([f"• {name} – {price:.2f}€" for name, price in items])
        for cat, items in menu_items.items()
    ])
    await callback.message.answer(f"📜 **Μενού**\n\n{menu_text}", parse_mode="Markdown", reply_markup=main_menu)

@dp.callback_query(lambda c: c.data == "contact")
async def contact_handler(callback: types.CallbackQuery):
    contact_text = (
        "📞 **Επικοινωνία Momento Cafe Bar**\n\n"
        "📍 **Διεύθυνση:** Kavala, Greece\n"
        "📱 **Τηλέφωνο:** +30 251 039 1646\n"
        "💬 **Telegram:** @momento_support"
    )
    await callback.message.answer(contact_text, parse_mode="Markdown", reply_markup=main_menu)

@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(order={})
    category_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}")] for cat in menu_items.keys()
    ] + [[InlineKeyboardButton(text="✅ Επιβεβαίωση Παραγγελίας", callback_data="confirm_order")]])

    await callback.message.answer("📌 Επιλέξτε κατηγορία:", reply_markup=category_menu)
    await state.set_state(OrderState.choosing_category)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())