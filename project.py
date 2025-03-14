from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

import os
import asyncio
import requests

class AIAssistantState(StatesGroup):
    waiting_for_ai_input = State()

load_dotenv()
BOT_TOKEN = "7915991395:AAGhALo30oqHNdy1rCFmiL3TW0Sn6Cr8sFY"
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=2)
    #start_lesson_button = InlineKeyboardButton(text="Начать урок", callback_data="start_lesson")
    ai_assistant_button = InlineKeyboardButton(text="ИИ-ассистент", callback_data="ai_assistant")
    keyboard.inline_keyboard.append([ai_assistant_button]) #start_lesson_button
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Обработчик нажатия на кнопку "Начать урок"
async def start_lesson(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Включение AR...")

    # Здесь происходит взаимодействие с AR
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, отправьте текст или фото для обработки.")

    # В конце урока выводим результат ученика
    await bot.send_message(callback_query.from_user.id, "Результат ученика: [текст ученика]")

# Обработчик нажатия на кнопку "ИИ-ассистент"
async def ai_assistant(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы выбрали ИИ-ассистента. Пожалуйста, задайте вопрос по теме урока.")
    await state.set_state(AIAssistantState.waiting_for_ai_input)

async def handle_ai_input(message: types.Message, state: FSMContext):
    user_prompt = message.text
    print(user_prompt)
    try:
        is_exit = False
        while not is_exit:
            gpt_model = "yandexgpt-lite"
            system_prompt = "Ты ассистент учителя физики. Дай пояснения по теме, которую тебе пришлет ученик"
            body = {
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/{gpt_model}",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.3,
                    "maxTokens": 2000,
                },
                "messages": [
                    {"role": "system", "text": system_prompt},
                    {"role": "user", "text": user_prompt},
                ],
            }

            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
            }

            # Send async request
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            operation_id = response.json().get("id")

            status_url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
            while True:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                if data.get("done"):
                    break
                await asyncio.sleep(2) 

            answer = data["response"]["alternatives"][0]["message"]["text"]
            await message.answer(f"\n{answer}\n")
            print(answer)
            await state.clear()
    # except requests.RequestException as e:
    #     await message.answer(f"Ошибка при запросе к API: {str(e)}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

dp.message.register(send_welcome, Command("start"))
dp.callback_query.register(start_lesson, F.data == "start_lesson")
dp.callback_query.register(ai_assistant, F.data == "ai_assistant")
dp.message.register(handle_ai_input, AIAssistantState.waiting_for_ai_input)

async def main():

    await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())