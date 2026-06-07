import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- DATA ----------------

orders = {}
tickets = {}
order_id = 1
ticket_id = 1

ADMINS = [123456789]  # <-- свой ID
MODERATORS = [111111111, 222222222]

balances = {}

# ---------------- MAIN MENU ----------------

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить Robux", callback_data="shop")],
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data="orders")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🎫 Тикеты", callback_data="tickets")],
        [InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")]
    ])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(message: types.Message):
    if message.from_user.id not in balances:
        balances[message.from_user.id] = 0

    await message.answer(
        "🏖️ FogBuy Shop\n\nДобро пожаловать 💚",
        reply_markup=main_menu()
    )

# ---------------- SHOP ----------------

@dp.callback_query(F.data == "shop")
async def shop(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="40R$ — 79₽", callback_data="buy_40"),
         InlineKeyboardButton(text="80R$ — 109₽", callback_data="buy_80")],

        [InlineKeyboardButton(text="240R$ — 249₽", callback_data="buy_200"),
         InlineKeyboardButton(text="500R$ — 359₽", callback_data="buy_400")],

        [InlineKeyboardButton(text="800R$ — 599₽", callback_data="buy_800"),
         InlineKeyboardButton(text="1000R$ — 659₽", callback_data="buy_1000")],

        [InlineKeyboardButton(text="1240R$ — 899₽", callback_data="buy_1200"),
         InlineKeyboardButton(text="1700R$ — 1199₽", callback_data="buy_1700")],

        [InlineKeyboardButton(text="2000R$ — 1319₽", callback_data="buy_2000"),
         InlineKeyboardButton(text="2500R$ — 1679₽", callback_data="buy_2500")],

        [InlineKeyboardButton(text="4500R$ — 3019₽", callback_data="buy_4500"),
         InlineKeyboardButton(text="10000R$ — 6379₽", callback_data="buy_10000")],

        [InlineKeyboardButton(text="22500R$ — 14750₽", callback_data="buy_22500")],

        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await call.message.edit_text("🛒 Магазин Robux\nВыберите пакет 👇", reply_markup=kb)

# ---------------- BUY ----------------

@dp.callback_query(F.data.startswith("buy_"))
async def buy(call: types.CallbackQuery):
    global order_id

    item = call.data.replace("buy_", "")

    orders[order_id] = {
        "user": call.from_user.id,
        "item": item,
        "status": "🟡 На проверке"
    }

    await call.message.edit_text(
        f"📦 Заказ #{order_id}\n\n"
        f"Товар: {item}\n"
        f"Статус: 🟡 На проверке\n\n"
        "💬 Напишите администратору для оплаты",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ В магазин", callback_data="shop")]
        ])
    )

    order_id += 1

# ---------------- ORDERS ----------------

@dp.callback_query(F.data == "orders")
async def orders_list(call: types.CallbackQuery):
    user_orders = [
        f"#{i} - {o['item']} ({o['status']})"
        for i, o in orders.items()
        if o["user"] == call.from_user.id
    ]

    text = "\n".join(user_orders) if user_orders else "📦 Заказов нет"

    await call.message.edit_text(text, reply_markup=main_menu())

# ---------------- BALANCE ----------------

@dp.callback_query(F.data == "balance")
async def balance(call: types.CallbackQuery):
    bal = balances.get(call.from_user.id, 0)
    await call.message.edit_text(f"💰 Баланс: {bal}₽", reply_markup=main_menu())

# ---------------- INFO ----------------

@dp.callback_query(F.data == "info")
async def info(call: types.CallbackQuery):
    await call.message.edit_text(
        "ℹ️ FogBuy Shop\n\n💚 Лучшие цены\n⚡ Быстрая выдача\n🔒 Гарантия",
        reply_markup=main_menu()
    )

# ---------------- TICKETS ----------------

@dp.callback_query(F.data == "tickets")
async def tickets_menu(call: types.CallbackQuery):
    await call.message.edit_text(
        "🎫 Тикеты\n\nНапишите проблему сюда 👇\n(функция упрощена)",
        reply_markup=main_menu()
    )

# ---------------- ADMIN (simple view) ----------------

@dp.message(F.text.startswith("/admin"))
async def admin(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    await message.answer("👑 Админ панель\n\n📦 Заказы: {}\n🎫 Тикеты: {}".format(len(orders), len(tickets)))

# ---------------- BACK ----------------

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text(
        "🏖️ FogBuy Shop\n\nДобро пожаловать 💚",
        reply_markup=main_menu()
    )

# ---------------- RUN ----------------

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
