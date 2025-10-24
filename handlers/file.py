from aiogram import Router, types, F

from data.chat_storage_json import load_chats

file_router = Router()

@file_router.message(F.text.startswith("/getfile_"))
async def getfile_handler(message: types.Message):
    text = message.text.strip()
    if "_" not in text:
        await message.answer("Неверная команда.")
        return
    key = text.split("_", 1)[1].strip()
    if not key:
        await message.answer("Неверный ключ.")
        return

    chats = load_chats()
    found = None
    found_uid = None
    for uid, data in chats.items():
        for entry in data.get("chat_history", []):
            if entry.get("file_key") == key:
                found = entry
                found_uid = uid
                break
        if found:
            break

    if not found:
        await message.answer("Файл не найден или ключ устарел.")
        return

    mtype = found.get("type")
    file_id = found.get("file_id")
    caption = found.get("caption", "")

    try:
        if mtype == "photo":
            await message.answer_photo(file_id, caption=f"{caption}\n(<i>из истории с {data.get('first_name','?')})</i>")
        elif mtype == "document":
            await message.answer_document(file_id, caption=f"{caption}\n(<i>из истории с {data.get('first_name','?')})</i>")
        elif mtype == "video":
            await message.answer_video(file_id, caption=f"{caption}\n(<i>из истории с {data.get('first_name','?')}</i>)")
        elif mtype == "voice":
            await message.answer_voice(file_id)
        elif mtype == "sticker":
            await message.answer_sticker(file_id)
        else:
            await message.answer("Тип файла не поддерживается для прямой отправки.")
    except Exception as e:
        await message.answer("Ошибка при отправке файла.")
        print("getfile error:", e)