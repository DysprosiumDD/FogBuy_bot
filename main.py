from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- MENU ----------------

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить Robux", callback_data="shop")],
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data="orders")],
        [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🎫 Тикеты", callback_data="tickets")],
        [InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")]
    ])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "🏖️ FogBuy Shop\n\nДобро пожаловать 💚",
        reply_markup=main_menu()
    )

# ---------------- SHOP ----------------

@dp.callback_query(F.data == "shop")
async def shop(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 40 Robux — 79₽", callback_data="buy_40")],
        [InlineKeyboardButton(text="🟢 80 Robux — 109₽", callback_data="buy_80")],
        [InlineKeyboardButton(text="🎁 200+40 — 249₽", callback_data="buy_200")],
        [InlineKeyboardButton(text="🎁 400+100 — 359₽", callback_data="buy_400")],
        [InlineKeyboardButton(text="🔥 1700 Robux — 1199₽", callback_data="buy_1700")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    await call.message.edit_text(
        "🛒 Магазин Robux\n\nВыберите товар 👇",
        reply_markup=kb
    )

# ---------------- BUY ----------------

@dp.callback_query(F.data.startswith("buy_"))
async def buy(call: types.CallbackQuery):
    product = call.data.replace("buy_", "")

    await call.message.edit_text(
        f"📦 Вы выбрали: {product} Robux\n\n"
        "💰 Напишите: 'я оплатил'\n"
        "⏳ После проверки заказ будет создан"
    )

# ---------------- OTHER ----------------

@dp.callback_query(F.data == "orders")
async def orders(call: types.CallbackQuery):
    await call.message.edit_text("📦 У вас пока нет заказов.")

@dp.callback_query(F.data == "balance")
async def balance(call: types.CallbackQuery):
    await call.message.edit_text("💰 Баланс: 0₽")

@dp.callback_query(F.data == "tickets")
async def tickets(call: types.CallbackQuery):
    await call.message.edit_text("🎫 Тикеты: скоро будет система")

@dp.callback_query(F.data == "info")
async def info(call: types.CallbackQuery):
    await call.message.edit_text("ℹ️ FogBuy Shop — лучший магазин 💚")

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text(
        "🏖️ FogBuy Shop\n\nДобро пожаловать 💚",
        reply_markup=main_menu()
    )

# ---------------- START BOT ----------------

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
