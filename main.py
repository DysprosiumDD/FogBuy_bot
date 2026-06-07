import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

ADMINS = [1692196373]  # твой ID

# ================= DB =================

db = sqlite3.connect("bot.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    nick TEXT,
    item TEXT,
    price INTEGER,
    status TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS balances (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

db.commit()

# ================= PRODUCTS =================

PRODUCTS = {
    "40": 79, "80": 109, "200": 249, "400": 359,
    "800": 599, "1000": 659, "1200": 899,
    "1700": 1199, "2000": 1319, "2500": 1679,
    "4500": 3019, "10000": 6379, "22500": 14750
}

user_state = {}  # FSM-lite (user -> product)


# ================= HELPERS =================

def balance_get(uid):
    cur.execute("SELECT balance FROM balances WHERE user_id=?", (uid,))
    r = cur.fetchone()
    return r[0] if r else 0


def balance_add(uid, amount):
    cur.execute("INSERT OR IGNORE INTO balances VALUES (?, 0)", (uid,))
    cur.execute("UPDATE balances SET balance = balance + ? WHERE user_id=?", (amount, uid))
    db.commit()


def order_create(uid, nick, item, price):
    cur.execute(
        "INSERT INTO orders (user_id,nick,item,price,status) VALUES (?,?,?,?,?)",
        (uid, nick, item, price, "🟡 На проверке")
    )
    db.commit()
    return cur.lastrowid


def order_update(oid, status):
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))
    db.commit()


def order_get_user(uid):
    cur.execute("SELECT id,item,status FROM orders WHERE user_id=?", (uid,))
    return cur.fetchall()


def order_get_all():
    cur.execute("SELECT id,user_id,item,status FROM orders")
    return cur.fetchall()


# ================= UI =================

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить Robux", callback_data="shop")],
        [InlineKeyboardButton(text="📦 Заказы", callback_data="orders")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🎫 Тикеты", callback_data="tickets")],
        [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")]
    ])


def back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])


# ================= START =================

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("🏪 ULTRA PRO SHOP\nДобро пожаловать 💚", reply_markup=menu())


# ================= SHOP =================

@dp.callback_query(F.data == "shop")
async def shop(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="40 — 79₽", callback_data="p_40"),
         InlineKeyboardButton(text="80 — 109₽", callback_data="p_80")],

        [InlineKeyboardButton(text="240 — 249₽", callback_data="p_200"),
         InlineKeyboardButton(text="500 — 359₽", callback_data="p_400")],

        [InlineKeyboardButton(text="800 — 599₽", callback_data="p_800"),
         InlineKeyboardButton(text="1000 — 659₽", callback_data="p_1000")],

        [InlineKeyboardButton(text="1240 — 899₽", callback_data="p_1200"),
         InlineKeyboardButton(text="1700 — 1199₽", callback_data="p_1700")],

        [InlineKeyboardButton(text="2000 — 1319₽", callback_data="p_2000"),
         InlineKeyboardButton(text="2500 — 1679₽", callback_data="p_2500")],

        [InlineKeyboardButton(text="4500 — 3019₽", callback_data="p_4500"),
         InlineKeyboardButton(text="10000 — 6379₽", callback_data="p_10000")],

        [InlineKeyboardButton(text="22500 — 14750₽", callback_data="p_22500")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await c.message.edit_text("🛒 Выберите товар:", reply_markup=kb)


# ================= PRODUCT =================

@dp.callback_query(F.data.startswith("p_"))
async def product(c: types.CallbackQuery):
    code = c.data.split("_")[1]
    user_state[c.from_user.id] = code

    await c.message.edit_text(f"📦 {code} R$\n\n👤 Введите игровой ник:")


# ================= NICK (FSM SAFE) =================

@dp.message()
async def nick(m: types.Message):
    if m.from_user.id not in user_state:
        return

    code = user_state[m.from_user.id]
    price = PRODUCTS[code]

    oid = order_create(m.from_user.id, m.text, code, price)

    del user_state[m.from_user.id]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{oid}")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back")]
    ])

    await m.answer(
        f"📦 Заказ #{oid}\n"
        f"🎮 Ник: {m.text}\n"
        f"💰 {price}₽\n\n"
        "💳 СБП: 2202 2068 1662 4501",
        reply_markup=kb
    )


# ================= PAID =================

@dp.callback_query(F.data.startswith("paid_"))
async def paid(c: types.CallbackQuery):
    oid = int(c.data.split("_")[1])

    order_update(oid, "🟡 На проверке")

    await c.message.edit_text(
        f"📦 Заказ #{oid}\n"
        "⏳ Ожидайте проверки\n"
        "📦 Статус можно смотреть в заказах"
    )


# ================= ORDERS =================

@dp.callback_query(F.data == "orders")
async def orders(c: types.CallbackQuery):
    data = order_get_user(c.from_user.id)

    if not data:
        await c.message.edit_text("📦 Нет заказов", reply_markup=back())
        return

    text = "\n".join([f"#{i} | {item} | {status}" for i, item, status in data])
    await c.message.edit_text(text, reply_markup=back())


# ================= BALANCE =================

@dp.callback_query(F.data == "balance")
async def balance(c: types.CallbackQuery):
    await c.message.edit_text(
        f"💰 Баланс: {balance_get(c.from_user.id)}₽",
        reply_markup=back()
    )


# ================= INFO =================

@dp.callback_query(F.data == "info")
async def info(c: types.CallbackQuery):
    await c.message.edit_text("ℹ️ ULTRA PRO SHOP", reply_markup=back())


# ================= TICKETS =================

@dp.callback_query(F.data == "tickets")
async def tickets(c: types.CallbackQuery):
    await c.message.edit_text("🎫 Тикеты: в разработке", reply_markup=back())


# ================= ADMIN PANEL =================

@dp.callback_query(F.data == "admin")
async def admin(c: types.CallbackQuery):
    if c.from_user.id not in ADMINS:
        return

    data = order_get_all()

    text = "🛠 ADMIN PANEL\n\n"
    kb = []

    for oid, uid, item, status in data:
        text += f"#{oid} | {uid} | {item} | {status}\n"

        kb.append([
            InlineKeyboardButton("🟡", callback_data=f"st_y_{oid}"),
            InlineKeyboardButton("🔵", callback_data=f"st_b_{oid}"),
            InlineKeyboardButton("🟢", callback_data=f"st_g_{oid}")
        ])

    await c.message.edit_text(text or "Нет заказов", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


# ================= STATUS + NOTIFY =================

@dp.callback_query(F.data.startswith("st_"))
async def status(c: types.CallbackQuery):
    if c.from_user.id not in ADMINS:
        return

    _, color, oid = c.data.split("_")
    oid = int(oid)

    if color == "y":
        order_update(oid, "🟡 На проверке")

    elif color == "b":
        order_update(oid, "🔵 В работе")

    elif color == "g":
        order_update(oid, "🟢 Выполнен")

        cur.execute("SELECT user_id FROM orders WHERE id=?", (oid,))
        uid = cur.fetchone()[0]

        await bot.send_message(uid, f"🎉 Заказ #{oid} выполнен!")

    await c.answer("OK")


# ================= BACK =================

@dp.callback_query(F.data == "back")
async def back(c: types.CallbackQuery):
    await c.message.edit_text("🏪 ULTRA PRO SHOP", reply_markup=menu())


# ================= RUN =================

async def main():
    print("ULTRA PRO 2 STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
