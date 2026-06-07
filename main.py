import asyncio
import os
import aiosqlite

from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

ADMINS = [1692196373]

# ---------------- DB ----------------

DB = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item TEXT,
            nick TEXT,
            status TEXT
        )
        """)
        await db.commit()

# ---------------- MENU ----------------

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", callback_data="shop")],
        [InlineKeyboardButton(text="📦 Мои покупки", callback_data="orders")],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="ℹ️ Инфо", callback_data="info")]
    ])

back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(m: types.Message):
    await m.answer("🏪 FogBuy PRO\nДобро пожаловать 💚", reply_markup=menu())

# ---------------- SHOP ----------------

@dp.callback_query(F.data == "shop")
async def shop(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("40", callback_data="buy_40"),
         InlineKeyboardButton("80", callback_data="buy_80")],
        [InlineKeyboardButton("200", callback_data="buy_200"),
         InlineKeyboardButton("400", callback_data="buy_400")],
        [InlineKeyboardButton("800", callback_data="buy_800"),
         InlineKeyboardButton("1000", callback_data="buy_1000")],
        [InlineKeyboardButton("1700", callback_data="buy_1700"),
         InlineKeyboardButton("2500", callback_data="buy_2500")],
        [InlineKeyboardButton("4500", callback_data="buy_4500"),
         InlineKeyboardButton("10000", callback_data="buy_10000")],
        [InlineKeyboardButton("22500", callback_data="buy_22500")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ])

    await c.message.edit_text("🛒 Выбор товара", reply_markup=kb)

# ---------------- STEP SYSTEM ----------------

temp = {}

@dp.callback_query(F.data.startswith("buy_"))
async def buy(c: types.CallbackQuery):
    temp[c.from_user.id] = c.data.replace("buy_", "")
    await c.message.edit_text("👤 Введи ник (точный)")

# ---------------- CREATE ORDER ----------------

@dp.message()
async def nick(m: types.Message):
    if m.from_user.id not in temp:
        return

    item = temp[m.from_user.id]
    nick = m.text

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id,item,nick,status) VALUES (?,?,?,?)",
            (m.from_user.id, item, nick, "🟡 Проверка")
        )
        await db.commit()
        order_id = cur.lastrowid

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✅ Я оплатил", callback_data=f"paid_{order_id}")]
    ])

    await m.answer(
        f"📦 Заказ #{order_id}\n💳 СБП: 2202206816624501\n\nПосле оплаты нажми кнопку",
        reply_markup=kb
    )

    del temp[m.from_user.id]

    for a in ADMINS:
        await bot.send_message(a, f"🆕 Заказ #{order_id} ждёт проверки")

# ---------------- PAID ----------------

@dp.callback_query(F.data.startswith("paid_"))
async def paid(c: types.CallbackQuery):
    oid = int(c.data.split("_")[1])

    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", ("🟡 Проверка", oid))
        await db.commit()

    await c.message.edit_text(f"📦 #{oid} отправлен на проверку")

# ---------------- ORDERS ----------------

@dp.callback_query(F.data == "orders")
async def orders(c: types.CallbackQuery):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id,item,status FROM orders WHERE user_id=?",
            (c.from_user.id,)
        )
        rows = await cur.fetchall()

    text = "\n".join([f"#{r[0]} | {r[1]} | {r[2]}" for r in rows]) or "Пусто"

    await c.message.edit_text(text, reply_markup=back)

# ---------------- BALANCE ----------------

@dp.callback_query(F.data == "balance")
async def balance(c: types.CallbackQuery):
    await c.message.edit_text("💰 Баланс: 0₽", reply_markup=back)

# ---------------- INFO ----------------

@dp.callback_query(F.data == "info")
async def info(c: types.CallbackQuery):
    await c.message.edit_text("ℹ️ PRO Shop Bot\n🔥 Fast\n🔒 Safe", reply_markup=back)

# ---------------- BACK ----------------

@dp.callback_query(F.data == "back")
async def back_btn(c: types.CallbackQuery):
    await c.message.edit_text("🏪 FogBuy PRO", reply_markup=menu())

# ---------------- ADMIN PANEL ----------------

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📦 Все", callback_data="a_all")],
        [InlineKeyboardButton("🟡 Проверка", callback_data="a_check")],
        [InlineKeyboardButton("🔵 В работе", callback_data="a_work")],
        [InlineKeyboardButton("🟢 Готово", callback_data="a_done")]
    ])

@dp.message(F.text == "/admin")
async def admin(m: types.Message):
    if m.from_user.id not in ADMINS:
        return
    await m.answer("👑 Admin Panel", reply_markup=admin_panel())

# ---------------- ADMIN VIEW ----------------

@dp.callback_query(F.data.startswith("a_"))
async def admin_view(c: types.CallbackQuery):
    if c.from_user.id not in ADMINS:
        return

    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT id,item,status FROM orders")
        rows = await cur.fetchall()

    if c.data == "a_all":
        text = "\n".join([f"#{r[0]} | {r[1]} | {r[2]}" for r in rows])
    else:
        st = {
            "a_check": "🟡 Проверка",
            "a_work": "🔵 В работе",
            "a_done": "🟢 Готово"
        }[c.data]

        text = "\n".join([f"#{r[0]} | {r[1]}" for r in rows if r[2] == st])

    await c.message.edit_text(text or "Пусто")

# ---------------- RUN ----------------

async def main():
    await init_db()
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
