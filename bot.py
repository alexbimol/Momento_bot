import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State

TOKEN = "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class OrderState(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    phone = State()
    address = State()
    name = State()
    confirmation = State()

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
}

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Παραγγελία", callback_data="order")],
    [InlineKeyboardButton(text="📜 Μενού", callback_data="menu")],
    [InlineKeyboardButton(text="📞 Επικοινωνία", callback_data="contact")]
])

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 Καλώς ήρθατε στο **Momento Cafe Bar**! ☕️🍹\n\n"
        "Μπορείτε να κάνετε παραγγελία, να δείτε το μενού ή να επικοινωνήσετε μαζί μας.",
        reply_markup=main_menu
    )

@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    menu_text = "\n\n".join([
        f"🍽 **{cat}**\n" + "\n".join([f"• {name} – {price:.2f}€" for name, price in items])
        for cat, items in menu_items.items()
    ])
    await callback.message.edit_text(f"📜 **Μενού**\n\n{menu_text}", parse_mode="Markdown", reply_markup=main_menu)

@dp.callback_query(lambda c: c.data == "order")
async def order_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(order={})
    category_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"category_{i}")] for i, cat in enumerate(menu_items.keys())
    ] + [[InlineKeyboardButton(text="✅ Επιβεβαίωση Παραγγελίας", callback_data="confirm_order")]])

    await callback.message.edit_text("📌 Επιλέξτε κατηγορία:", reply_markup=category_menu)
    await state.set_state(OrderState.choosing_category)

@dp.callback_query(lambda c: c.data.startswith("category_"))
async def choose_category(callback: types.CallbackQuery, state: FSMContext):
    category_index = int(callback.data.split("_")[1])
    category_name = list(menu_items.keys())[category_index]
    items = menu_items[category_name]

    product_buttons = [
        [InlineKeyboardButton(text=f"{name} - {price:.2f}€", callback_data=f"add_{name}")]
        for name, price in items
    ]

    product_menu = InlineKeyboardMarkup(inline_keyboard=product_buttons + [[InlineKeyboardButton(text="⬅️ Πίσω", callback_data="order")]])
    await callback.message.edit_text(f"🛒 **{category_name}**\n\nΕπιλέξτε προϊόν:", parse_mode="Markdown", reply_markup=product_menu)

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_product(callback: types.CallbackQuery, state: FSMContext):
    product_name = callback.data[4:]
    user_data = await state.get_data()

    order = user_data.get("order", {})
    order[product_name] = order.get(product_name, 0) + 1

    await state.update_data(order=order)
    await callback.answer(f"✅ {product_name} προστέθηκε στην παραγγελία!", show_alert=False)

@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    order = user_data.get("order", {})

    if not order:
        await callback.answer("❌ Η παραγγελία σας είναι άδεια!", show_alert=True)
        return

    order_text = "\n".join([f"• {product} x{count}" for product, count in order.items()])
    
    await callback.message.edit_text(
        f"📝 **Η παραγγελία σας:**\n\n{order_text}\n\n"
        "📌 Παρακαλώ στείλτε το όνομά σας:",
        parse_mode="Markdown"
    )
    await state.set_state(OrderState.name)

@dp.message(OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        "📞 Παρακαλώ στείλτε το τηλέφωνό σας:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📞 Αποστολή τηλεφώνου", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(OrderState.phone)

@dp.message(OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        await message.answer("❌ Στείλτε το τηλέφωνό σας μέσω του κουμπιού!")
        return

    await state.update_data(phone=message.contact.phone_number)

    await message.answer("📍 Παρακαλώ στείλτε τη διεύθυνσή σας:")
    await state.set_state(OrderState.address)

@dp.message(OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    user_data = await state.get_data()

    order_text = "\n".join([f"• {product} x{count}" for product, count in user_data['order'].items()])
    
    await message.answer(
        f"✅ **Η παραγγελία ολοκληρώθηκε!**\n\n"
        f"👤 Όνομα: {user_data['name']}\n"
        f"📞 Τηλέφωνο: {user_data['phone']}\n"
        f"📍 Διεύθυνση: {user_data['address']}\n\n"
        f"📝 **Παραγγελία:**\n{order_text}\n\n"
        "📌 Σύντομα θα επικοινωνήσουμε μαζί σας!",
        reply_markup=main_menu
    )
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())