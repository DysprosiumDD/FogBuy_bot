import asyncio
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()

# ---------------- DATA ----------------

orders = {}
temp = {}
order_id = 1

ADMINS = [1692196373]  # 👈 ВСТАВЬ СВОЙ TG ID

# ---------------- PRODUCTS ----------------

PRODUCTS = {
    "40": 79,
    "80": 109,
    "200": 249,
    "400": 359,
    "800": 599,
    "1000": 659,
    "1200": 899,
    "1700": 1199,
    "2000": 1319,
    "2500": 1679,
    "4500": 3019,
    "10000": 6379,
    "22500": 14750,
}

# ---------------- UI ----------------

def main_menu():
    kb = [
        [InlineKeyboardButton(text="🛒 Купить Robux", callback_data="shop")],
        [InlineKeyboardButton(text="📦 Мои покупки", callback_data="orders")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")]
    ]

    if ADMINS:
        kb.append([InlineKeyboardButton(text="🛠 Админ панель", callback_data="admin")])

    return InlineKeyboardMarkup(inline_keyboard=kb)


back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(m: types.Message):
    await m.answer("🏪 FOGBUY SHOP\nДобро пожаловать 💚", reply_markup=main_menu())

# ---------------- SHOP ----------------

@dp.callback_query(F.data == "shop")
async def shop(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 40 — 79₽", callback_data="p_40"),
         InlineKeyboardButton(text="🟢 80 — 109₽", callback_data="p_80")],

        [InlineKeyboardButton(text="🎁 200+40 — 249₽", callback_data="p_200"),
         InlineKeyboardButton(text="🎁 400+100 — 359₽", callback_data="p_400")],

        [InlineKeyboardButton(text="🟡 800 — 599₽", callback_data="p_800"),
         InlineKeyboardButton(text="🟡 1000 — 659₽", callback_data="p_1000")],

        [InlineKeyboardButton(text="💎 1200+40 — 899₽", callback_data="p_1200"),
         InlineKeyboardButton(text="🔥 1700 — 1199₽", callback_data="p_1700")],

        [InlineKeyboardButton(text="🔥 2000 — 1319₽", callback_data="p_2000"),
         InlineKeyboardButton(text="🚀 2500 — 1679₽", callback_data="p_2500")],

        [InlineKeyboardButton(text="💎 4500 — 3019₽", callback_data="p_4500"),
         InlineKeyboardButton(text="👑 10000 — 6379₽", callback_data="p_10000")],

        [InlineKeyboardButton(text="👑 22500 — 14750₽", callback_data="p_22500")],

        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await c.message.edit_text("🛒 Выберите пакет:", reply_markup=kb)

# ---------------- PRODUCT ----------------

@dp.callback_query(F.data.startswith("p_"))
async def product(c: types.CallbackQuery):
    code = c.data.split("_")[1]
    price = PRODUCTS[code]

    temp[c.from_user.id] = code

    text = (
        f"📦 {code} R$\n"
        f"💰 {price}₽\n\n"
        "⚠️ Выдача через аккаунт\n"
        "⚡ Гарантия\n\n"
        "Нажмите купить"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy_{code}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="shop")]
    ])

    await c.message.edit_text(text, reply_markup=kb)

# ---------------- BUY ----------------

@dp.callback_query(F.data.startswith("buy_"))
async def buy(c: types.CallbackQuery):
    code = c.data.split("_")[1]
    temp[c.from_user.id] = code

    await c.message.edit_text("👤 Введите игровой ник (ТОЧНЫЙ!)")

# ---------------- CREATE ORDER ----------------

@dp.message()
async def nick(m: types.Message):
    global order_id

    if m.from_user.id not in temp:
        return

    code = temp[m.from_user.id]
    price = PRODUCTS[code]

    orders[order_id] = {
        "user": m.from_user.id,
        "item": code,
        "nick": m.text,
        "status": "🟡 На проверке"
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{order_id}")]
    ])

    await m.answer(
        f"📦 Заказ #{order_id}\n"
        f"🎮 Ник: {m.text}\n"
        f"🛒 {code} R$ — {price}₽\n\n"
        "💳 СБП:\n2202 2068 1662 4501\n\n"
        "После оплаты нажмите кнопку 👇",
        reply_markup=kb
    )

    order_id += 1
    del temp[m.from_user.id]

# ---------------- PAID ----------------

@dp.callback_query(F.data.startswith("paid_"))
async def paid(c: types.CallbackQuery):
    oid = int(c.data.split("_")[1])

    if oid in orders:
        orders[oid]["status"] = "🟡 На проверке"
        await c.message.edit_text(f"📦 Заказ #{oid}\n🟡 Отправлен на проверку")

# ---------------- ORDERS ----------------

@dp.callback_query(F.data == "orders")
async def orders_list(c: types.CallbackQuery):
    data = [
        f"#{i} | {o['item']} R$ | {o['status']}"
        for i, o in orders.items()
        if o["user"] == c.from_user.id
    ]

    await c.message.edit_text("\n".join(data) if data else "📦 Нет заказов", reply_markup=back_kb)

# ---------------- BALANCE ----------------

@dp.callback_query(F.data == "balance")
async def balance(c: types.CallbackQuery):
    await c.message.edit_text("💰 Баланс: 0₽", reply_markup=back_kb)

# ---------------- INFO ----------------

@dp.callback_query(F.data == "info")
async def info(c: types.CallbackQuery):
    await c.message.edit_text("ℹ️ FOGBUY SHOP\nГарантия | Быстро | Надёжно", reply_markup=back_kb)

# ---------------- ADMIN ----------------

@dp.callback_query(F.data == "admin")
async def admin(c: types.CallbackQuery):
    if c.from_user.id not in ADMINS:
        await c.answer("Нет доступа", show_alert=True)
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await c.message.edit_text("🛠 Админ панель", reply_markup=kb)

# ---------------- ADMIN ORDERS ----------------

@dp.callback_query(F.data == "admin_orders")
async def admin_orders(c: types.CallbackQuery):
    if c.from_user.id not in ADMINS:
        return

    kb = []

    text = "📦 ВСЕ ЗАКАЗЫ:\n\n"

    for i, o in orders.items():
        text += f"#{i} | {o['nick']} | {o['item']} | {o['status']}\n"

        kb.append([
            InlineKeyboardButton("🟡", callback_data=f"st_y_{i}"),
            InlineKeyboardButton("🔵", callback_data=f"st_b_{i}"),
            InlineKeyboardButton("🟢", callback_data=f"st_g_{i}")
        ])

    kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin")])

    await c.message.edit_text(text or "Нет заказов", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ---------------- STATUS ----------------

@dp.callback_query(F.data.startswith("st_"))
async def status(c: types.CallbackQuery):
    if c.from_user.id not in ADMINS:
        return

    _, color, oid = c.data.split("_")
    oid = int(oid)

    if oid in orders:
        if color == "y":
            orders[oid]["status"] = "🟡 На проверке"
        elif color == "b":
            orders[oid]["status"] = "🔵 В работе"
        elif color == "g":
            orders[oid]["status"] = "🟢 Выполнен"

    await c.answer("Обновлено")

# ---------------- BACK ----------------

@dp.callback_query(F.data == "back")
async def back(c: types.CallbackQuery):
    await c.message.edit_text("🏪 FOGBUY SHOP", reply_markup=main_menu())

# ---------------- RUN ----------------

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
