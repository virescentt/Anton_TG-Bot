import os
from aiogram import F, Router, types
from aiogram.filters import Command
from config import MANAGER_IDS
from data.chat_storage_json import load_chats, save_chats, update_chats_cache
from utils.keyboards import InActive_chat_control_keyboard, back_keyboard, cities_keyboard, confirm_keyboard

confirmations_router = Router()


# --- ПОДТВ. УДАЛЕНИЕ ЗАПРОСА ---
@confirmations_router.callback_query(F.data.startswith("confirm_delete_request_"))
async def confirm_delete_request(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # получаем ID пользователя из callback_data
    chats = load_chats()
    
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return
    
    if chats[user_id]["status"] != "waiting":
        await callback.answer(f'Его статус: {chats[user_id]["status"]}\nЗапрос не найден.')
        return

    await callback.message.answer("<i><b>❗❗ Вы точно хотите удалить запрос?</b>\nЕсли пользователь новый, у Вас не сохранятся никакие его данные.</i>", reply_markup=confirm_keyboard(confirm_cb_name="confirmed_delete_request", uid=user_id))

    await callback.answer()


@confirmations_router.callback_query(F.data.startswith("confirmed_delete_request_"))
async def confirmed_delete_request(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # получаем ID пользователя из callback_data
    chats = load_chats()
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return

    chat_data = chats[user_id]
    manager = chat_data.get("manager")
    chat_history = chat_data.get("chat_history", [])
    if chat_history == []:
        callback.answer("История пуста")
        return

    # --- Удаляем сообщение с подтверждением ---
    try:
        await callback.message.delete()
    except Exception:
        pass

    # --- Если у пользователя нет менеджера, удаляем весь чат ---
    if not manager:
        del chats[user_id]
        save_chats(chats)
        await callback.message.answer(
            f"✅ Запрос от пользователя <b>{chat_data.get('first_name', 'Неизвестный')}</b> полностью удалён."
        )

    # --- Если менеджер есть, просто деактивируем чат ---
    else:
        chat_data["status"] = "inactive"
        if chat_history:
            chat_data["chat_history"].pop(-1)  # удаляем последнее сообщение
        chats[user_id] = chat_data
        save_chats(chats)
        update_chats_cache()

        await callback.message.answer(
            f"🕊 Запрос удален."
        )
        # await callback.message.answer

    # --- Возвращаем менеджера к списку ожидающих запросов ---
    await callback.message.answer(
        "⬅️ Возврат к списку ожидающих заявок",
        reply_markup=back_keyboard("📋 К списку запросов", "admin_waiting_requests")
    )

    await callback.answer()

# ----------------------------------------------------------





# --- ПОДТВ. ВЫХОД ИЗ ОНЛАЙН ЧТОБЫ НАЧАТЬ НОВЫЙ ОНЛАЙН ---
@confirmations_router.callback_query(F.data.startswith("confirm_leave_user_"))
async def confirm_leave_user(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # получаем ID пользователя из callback_data
    chats = load_chats()
    
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return

    await callback.message.answer(f'<i><b>Сейчас Вы онлайн с пользователем {chats[user_id]["first_name"]}</b>\n Хотите выйти и войти в этот чат?</i>', reply_markup=confirm_keyboard(confirm_cb_name="confirmed_leave_user", uid=user_id))

    await callback.answer()


@confirmations_router.callback_query(F.data.startswith("confirmed_leave_user_"))
async def confirmed_leave_user(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # получаем ID пользователя из callback_data
    chats = load_chats()
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return


    
    # --- Удаляем сообщение с подтверждением ---
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
            f"🕊 Пользователь удален."
        )
# ------------------------------------------------------




# --- ПОДТВ. УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ИЗ БД ---
@confirmations_router.callback_query(F.data.startswith("confirm_delete_user_"))
async def confirm_delete_user(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # получаем ID пользователя из callback_data
    chats = load_chats()
    
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return

    await callback.message.answer("<i><b>❗❗ Вы точно хотите удалить пользователя из базы?</b>\n Это необратимо.</i>", reply_markup=confirm_keyboard(confirm_cb_name="confirmed_delete_user", uid=user_id))

    await callback.answer()

@confirmations_router.callback_query(F.data.startswith("confirmed_delete_user_"))
async def confirmed_delete_user(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # получаем ID пользователя из callback_data
    chats = load_chats()
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return

    del chats[user_id]
    save_chats(chats)
    
    # --- Удаляем сообщение с подтверждением ---
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
            f"🕊 Пользователь удален."
        )

# ---------------------------------------------------------




# --- ПОДТВ. ОЧИСТКУ ИСТОРИИ ---
@confirmations_router.callback_query(F.data.startswith("confirm_clear_chat_history_"))
async def confirm_delete_user(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[4]  # получаем ID пользователя из callback_data
    chats = load_chats()
    
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return
    if chats[user_id]["chat_history"] == []:
        await callback.answer("История пуста")
        return

    await callback.message.answer(f'<i><b>🧹 Хотите очистить историю чата с {chats[user_id]["first_name"]}?</b>\n</i>', reply_markup=confirm_keyboard(confirm_cb_name="confirmed_clear_chat_history", uid=user_id))

    await callback.answer()

@confirmations_router.callback_query(F.data.startswith("confirmed_clear_chat_history"))
async def confirmed_clear_chat_history(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[4]  # ID пользователя
    chats = load_chats()
    is_active = False

    
    if user_id not in chats:
        await callback.answer("❌ Чат не найден")
        return
    
    # Очищаем историю
    chats[user_id]["chat_history"] = []
    save_chats(chats)

    data = chats.get(user_id)

    if data["status"] == "active":
        mark = '🟢'
        is_active = True
    else:
        mark = '🔴'

    # Формируем обновлённое сообщение без истории
    manager = chats[user_id].get("manager", None)
    username = f"@{chats[user_id]['username']}" if chats[user_id].get("username") else "—"

    text = (
        f"<b>Чат с пользователем:</b>\n"
        f"👤 {data['first_name']} ({username}) {mark}"
        f"🆔 ID: {user_id}"
        f"🧑‍💼 Менеджер: {manager['first_name'] if manager else '—'}"
        "\n-------------------------------\n"
        "📜 <b>История сообщений:</b>\n\n"
        "🗑 История чата удалена."
    )

    # Редактируем сообщение
    await callback.message.edit_text(
        text,
        reply_markup=InActive_chat_control_keyboard(is_active=is_active, uid=user_id)
    )

    await callback.answer("История чата удалена")

# ---------------------------------------------------------






# ОТМЕНА ПОДТВЕРЖДЕНИЯ
@confirmations_router.callback_query(F.data.startswith("cancel_confirm"))
async def cancel_confirm(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return
    try:
        await callback.message.delete()
    except Exception:
        pass
# -----------------------------------------------