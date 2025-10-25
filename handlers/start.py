from aiogram import F, Router, types
from aiogram.filters import Command
from common.utils_funcs import render_cities_start_pick
from config import VIDEO_FILE_ID

start_router = Router()

@start_router.callback_query(F.data == "start")
@start_router.message(F.text == "старт" )
@start_router.message(Command("start"))
async def start_command(event: object):
    message = event.message if isinstance(event, types.CallbackQuery) else event

    if VIDEO_FILE_ID:
        await message.answer_video(video=VIDEO_FILE_ID)

    await render_cities_start_pick(
        event,
        # Начальный текст хранится в файле config.py переменной START_TEXT. Поменяйте его если хотите изменить начальный текст.   
        # text=START_TEXT
        )



#  Вставьте этот файл айди в файле config для переменной VIDEO_FILE_ID, чтобы поменять вступительное видео

# @start_router.message(F.video)
# async def handle_video(message: types.Message):
    # await message.answer("Получил видео!")
    # await message.answer_video(message.video.file_id)
    # await message.answer(f"file_id: {message.video.file_id}")