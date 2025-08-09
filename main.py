import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import subprocess
import os

BOT_TOKEN = "ВАШ ТОКЕН"  # Замени на свой токен

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Этот бот позволит искать аккаунты на сайтах в которых был зарегестрирован пользователь, более 300 сайтов!\nИспользуй команду /search username для поиска где username никнейм вашего пользователя!."
    )


@dp.message(Command("search"))
async def search_user(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Используй: /search username")
        return

    username = args[1]

    # Отправляем сообщение о задержке
    wait_msg = await message.reply(
        "⏳ Поиск информации... Примерное время ожидания: 30 сек.")

    try:
        # Запускаем Sherlock
        result = subprocess.run(
            ["sherlock", username, "--timeout", "1", "--print-found"],
            capture_output=True,
            text=True,
            check=True)

        # Удаляем сообщение "Поиск информации..."
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=wait_msg.message_id)

        if result.stdout:
            response = f"🔎 Результаты для {username}:\n\n{result.stdout}"
        else:
            response = f"❌ Аккаунты {username} не найдены."

        # Если результат слишком длинный, отправляем файлом
        if len(response) > 4096:
            with open(f"{username}_results.txt", "w") as f:
                f.write(response)
            await message.reply_document(
                types.FSInputFile(f"{username}_results.txt"))
            os.remove(f"{username}_results.txt")
        else:
            await message.reply(response)

    except subprocess.CalledProcessError as e:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=wait_msg.message_id)
        await message.reply(
            f"⚠️ Ошибка: {e.stderr or 'Неизвестная ошибка Sherlock'}")
    except Exception as e:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=wait_msg.message_id)
        await message.reply(f"🚫 Ошибка: {str(e)}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
