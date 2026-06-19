import asyncio
import os
from aiogram import Bot, Dispatcher, F 
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token = API_TOKEN)
dp = Dispatcher()

# ☁️ ОБЛАЧНОЕ ХРАНИЛИЩЕ
archives = {}


# СОСТОЯНИЯ
class UploadState(StatesGroup):
    archive_name = State()
    waiting_file = State()

class DownloadState(StatesGroup):
    archive_name = State()



# команда /start и остальные
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Облачные архивы:\n"
        "/upload - загрузить файл\n"
        "/get - получить файл\n"
        "/list - список архивов"
    )



# список архивов
@dp.message(Command("list"))
async def list_archives(message: Message):
    if not archives:
        await message.answer("Архивов пока нет.")
        return

    text = "Архивы:\n" + "\n".join(archives.keys())
    await message.answer(text)



# загрузка файла
@dp.message(Command("upload"))
async def upload_start(message: Message, state: FSMContext):
    await state.set_state(UploadState.archive_name)
    await message.answer("В какой архив сохранить файл?")


@dp.message(UploadState.archive_name)
async def get_archive_name(message: Message, state: FSMContext):
    archive = message.text.strip()

    archives.setdefault(archive, [])

    await state.update_data(archive=archive)
    await state.set_state(UploadState.waiting_file)

    await message.answer("Отправь файл 📎")


@dp.message(UploadState.waiting_file, F.document)
async def save_file(message: Message, state: FSMContext):
    data = await state.get_data()
    archive = data["archive"]

    file_id = message.document.file_id

    archives[archive].append(file_id)

    await message.answer(f"Файл сохранён в архив: {archive}")
    await state.clear()



# получение файлов
@dp.message(Command("get"))
async def get_start(message: Message, state: FSMContext):
    await state.set_state(DownloadState.archive_name)
    await message.answer("Из какого архива получить файлы?")


@dp.message(DownloadState.archive_name)
async def send_files(message: Message, state: FSMContext):
    archive = message.text.strip()

    if archive not in archives:
        await message.answer("Такого архива нет.")
        await state.clear()
        return

    files = archives[archive]

    if not files:
        await message.answer("Архив пуст.")
        await state.clear()
        return

    await message.answer(f"📦 Файлы из архива {archive}:")

    for file_id in files:
        await message.answer_document(file_id)

    await state.clear()



# запуск (устойчивый)
async def main():
    while True:
        try:
            print("Бот запущен...")
            await dp.start_polling(bot)
        except Exception as e:
            print("Ошибка, перезапуск:", e)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())