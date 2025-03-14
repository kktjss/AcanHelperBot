import os
import time
import asyncio
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

#пууорадлоаоплдывд

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

# Check if required environment variables are set
if not all([BOT_TOKEN, YANDEX_FOLDER_ID, YANDEX_API_KEY]):
    raise ValueError("Missing required environment variables")


async def send_welcome(message: Message):
    """Handler for /start command"""
    await message.answer(
        "Привет! Я могу сгенерировать пример кода на любом языке программирования. "
        "Просто напиши название языка, например, 'Python' или 'F#'."
    )


async def generate_code(message: Message):
    """Handler for generating code examples"""
    try:
        gpt_model = "yandexgpt-lite"
        system_prompt = "Ты ассистент программиста. Напиши короткую программу-пример на указанном языке программирования. В ответе пришли только код."
        user_prompt = message.text

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

        # Check operation status
        status_url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
        while True:
            response = requests.get(status_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("done"):
                break
            await asyncio.sleep(2)  # Use asyncio.sleep instead of time.sleep

        # Get and send the result
        answer = data["response"]["alternatives"][0]["message"]["text"]
        await message.answer(f"```\n{answer}\n```")

    except requests.RequestException as e:
        await message.answer(f"Ошибка при запросе к API: {str(e)}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")


async def main():
    """Main function to start the bot"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(
        generate_code, F.text, ~Command("start")
    )  # Handle all messages except /start

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
