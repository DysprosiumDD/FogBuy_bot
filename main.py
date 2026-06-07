from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- DATA ----------------
orders = {}
order_id = 1

ADMINS = [123456789]  # <-- сюда свой Telegram ID

# ---------------- MENU ----------------

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить Robux", callback_data="shop")],
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data="orders")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🎫 Тикеты", callback_data="tickets")],
        [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")]
    ])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("🏖️ FogBuy Shop\nДобро пожаловать 💚", reply_markup=menu())

# ---------------- SHOP ----------------

@dp.callback_query(F.data == "shop")
async def shop(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("40 — 79₽", callback_data="buy_40")],
        [InlineKeyboardButton("80 — 109₽", callback_data="buy_80")],
        [InlineKeyboardButton("200+40 — 249₽", callback_data="buy_200")],
        [InlineKeyboardButton("400+100 — 359₽", callback_data="buy_400")],
        [InlineKeyboardButton("800 — 599₽", callback_data="buy_800")],
        [InlineKeyboardButton("1000 — 659₽", callback_data="buy_1000")],
        [InlineKeyboardButton("1200+40 — 899₽", callback_data="buy_1200")],
        [InlineKeyboardButton("1700 — 1199₽", callback_data="buy_1700")],
        [InlineKeyboardButton("2000 — 1319₽", callback_data="buy_2000")],
        [InlineKeyboardButton("2500 — 1679₽", callback_data="buy_2500")],
        [InlineKeyboardButton("4500 — 3019₽", callback_data="buy_4500")],
        [InlineKeyboardButton("10000 — 6379₽", callback_data="buy_10000")],
        [InlineKeyboardButton("22500 — 14750₽", callback_data="buy_22500")]
    ])

    await call.message.edit_text("🛒 Магазин Robux\nВыберите товар 👇", reply_markup=kb)

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
        "Статус: 🟡 На проверке\n\n"
        "💬 Напишите администратору для оплаты"
    )

    order_id += 1

# ---------------- ORDERS ----------------

@dp.callback_query(F.data == "orders")
async def show_orders(call: types.CallbackQuery):
    user_orders = [f"#{i} - {o['item']} ({o['status']})"
                   for i, o in orders.items()
                   if o["user"] == call.from_user.id]

    text = "\n".join(user_orders) if user_orders else "📦 Заказов нет"

    await call.message.edit_text(text)

# ---------------- BALANCE ----------------

@dp.callback_query(F.data == "balance")
async def balance(call: types.CallbackQuery):
    await call.message.edit_text("💰 Баланс: 0₽")

# ---------------- INFO ----------------

@dp.callback_query(F.data == "info")
async def info(call: types.CallbackQuery):
    await call.message.edit_text("ℹ️ FogBuy — лучший магазин 💚")

# ---------------- TICKETS ----------------

@dp.callback_query(F.data == "tickets")
async def tickets(call: types.CallbackQuery):
    await call.message.edit_text("🎫 Тикеты скоро будут добавлены")

# ---------------- RUN ----------------

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
