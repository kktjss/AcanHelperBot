from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
BOT_TOKEN = "7915991395:AAGhALo30oqHNdy1rCFmiL3TW0Sn6Cr8sFY"
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    start_lesson_button = InlineKeyboardButton(text="Начать урок", callback_data="start_lesson")
    ai_assistant_button = InlineKeyboardButton(text="ИИ-ассистент", callback_data="ai_assistant")
    keyboard.add(start_lesson_button, ai_assistant_button)
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Обработчик нажатия на кнопку "Начать урок"
async def start_lesson(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Включение VR...")
    
    # Здесь можно добавить логику для обработки текста и/или фото
    # Например, запросить у пользователя текст или фото
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, отправьте текст или фото для обработки.")

    # В конце урока выводим результат ученика
    await bot.send_message(callback_query.from_user.id, "Результат ученика: [текст ученика]")

# Обработчик нажатия на кнопку "ИИ-ассистент"
async def ai_assistant(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы выбрали ИИ-ассистента. Здесь будет функционал ассистента.")

dp.message.register(send_welcome, Command("start"))
dp.callback_query.register(start_lesson, F.data == "start_lesson")
dp.callback_query.register(ai_assistant, F.data == "ai_assistant")

async def main():
    await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())