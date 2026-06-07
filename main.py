from aiogram import Bot, Dispatcher, types
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

async def main():
    print("FogBuy bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
