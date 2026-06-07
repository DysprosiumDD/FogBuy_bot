import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- DATA ----------------

orders = {}
temp = {}
order_id = 1

ADMINS = [1692196373]  

# ---------------- STATUS COLORS ----------------

STATUS = {
    "check": "🟡 На проверке",
    "work": "🔵 В работе",
    "done": "🟢 Выполнен"
}

# ---------------- MENU ----------------

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🛒 Купить Robux", callback_data="shop")],
        [InlineKeyboardButton("📦 Мои покупки", callback_data="orders")],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="info")]
    ])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("🏖️ FogBuy Shop\nДобро пожаловать 💚", reply_markup=main_menu())

# ---------------- SHOP ----------------

@dp.callback_query(F.data == "shop")
async def shop(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("40 - 79₽", callback_data="buy_40"),
         InlineKeyboardButton("80 - 109₽", callback_data="buy_80")],

        [InlineKeyboardButton("200+40 - 249₽", callback_data="buy_200"),
         InlineKeyboardButton("400+100 - 359₽", callback_data="buy_400")],

        [InlineKeyboardButton("800 - 599₽", callback_data="buy_800"),
         InlineKeyboardButton("1000 - 659₽", callback_data="buy_1000")],

        [InlineKeyboardButton("1200+40 - 899₽", callback_data="buy_1200"),
         InlineKeyboardButton("1700 - 1199₽", callback_data="buy_1700")],

        [InlineKeyboardButton("2000 - 1319₽", callback_data="buy_2000"),
         InlineKeyboardButton("2500 - 1679₽", callback_data="buy_2500")],

        [InlineKeyboardButton("4500 - 3019₽", callback_data="buy_4500"),
         InlineKeyboardButton("10000 - 6379₽", callback_data="buy_10000")],

        [InlineKeyboardButton("22500 - 14750₽", callback_data="buy_22500")],

        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ])

    await call.message.edit_text("🛒 Выберите пакет:", reply_markup=kb)

# ---------------- BUY ----------------

@dp.callback_query(F.data.startswith("buy_"))
async def buy(call: types.CallbackQuery):
    temp[call.from_user.id] = call.data.replace("buy_", "")
    await call.message.edit_text("👤 Введите ваш НИК (точный!)")

# ---------------- GET NICK ----------------

@dp.message()
async def get_nick(message: types.Message):
    global order_id

    if message.from_user.id not in temp:
        return

    item = temp[message.from_user.id]
    nick = message.text

    orders[order_id] = {
        "user": message.from_user.id,
        "item": item,
        "nick": nick,
        "status": STATUS["check"]
    }

    # уведомление админу
    for admin in ADMINS:
        await bot.send_message(
            admin,
            f"🆕 Новый заказ #{order_id}\n"
            f"🎮 Ник: {nick}\n"
            f"🛒 Товар: {item}"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{order_id}")]
    ])

    await message.answer(
        f"📦 Заказ #{order_id}\n\n"
        f"🎮 Ник: {nick}\n"
        f"🛒 Товар: {item}\n\n"
        "💳 СБП: 2202 2068 1662 4501\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=kb
    )

    order_id += 1
    del temp[message.from_user.id]

# ---------------- PAID ----------------

@dp.callback_query(F.data.startswith("paid_"))
async def paid(call: types.CallbackQuery):
    oid = int(call.data.replace("paid_", ""))

    if oid in orders:
        orders[oid]["status"] = STATUS["check"]

        # уведомление админу
        for admin in ADMINS:
            await bot.send_message(admin, f"💳 Оплата подтверждена #{oid}\n🟡 На проверке")

        await call.message.edit_text(
            f"📦 Заказ #{oid}\n🟡 Отправлен на проверку"
        )

# ---------------- ORDERS ----------------

@dp.callback_query(F.data == "orders")
async def orders_list(call: types.CallbackQuery):
    data = [
        f"#{i} | {o['item']} | {o['status']}"
        for i, o in orders.items()
        if o["user"] == call.from_user.id
    ]

    text = "\n".join(data) if data else "📦 Нет заказов"
    await call.message.edit_text(text, reply_markup=main_menu())

# ---------------- BALANCE ----------------

@dp.callback_query(F.data == "balance")
async def balance(call: types.CallbackQuery):
    await call.message.edit_text(
        "💰 Баланс: 0₽",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
        ])
    )

# ---------------- INFO ----------------

@dp.callback_query(F.data == "info")
async def info(call: types.CallbackQuery):
    await call.message.edit_text(
        "ℹ️ FogBuy Shop\n🔥 Лучшие цены\n⚡ Быстро\n🔒 Гарантия",
        reply_markup=main_menu()
    )

# ---------------- BACK ----------------

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text("🏖️ FogBuy Shop", reply_markup=main_menu())

# ---------------- ADMIN PANEL ----------------

@dp.message(F.text == "/admin")
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📦 Все заказы", callback_data="admin_orders")],
        [InlineKeyboardButton("🟡 На проверке", callback_data="admin_check")],
        [InlineKeyboardButton("🔵 В работе", callback_data="admin_work")],
        [InlineKeyboardButton("🟢 Выполненные", callback_data="admin_done")]
    ])

    await message.answer("👑 Админ панель", reply_markup=kb)

# ---------------- ADMIN VIEW ----------------

@dp.callback_query(F.data.startswith("admin_"))
async def admin(call: types.CallbackQuery):
    if call.from_user.id not in ADMINS:
        return

    if call.data == "admin_orders":
        text = "\n".join([f"#{i} | {o['status']}" for i, o in orders.items()])
    elif call.data == "admin_check":
        text = "\n".join([f"#{i}" for i, o in orders.items() if o["status"] == STATUS["check"]])
    elif call.data == "admin_work":
        text = "\n".join([f"#{i}" for i, o in orders.items() if o["status"] == STATUS["work"]])
    else:
        text = "\n".join([f"#{i}" for i, o in orders.items() if o["status"] == STATUS["done"]])

    await call.message.edit_text(text or "Пусто")

# ---------------- RUN ----------------

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
