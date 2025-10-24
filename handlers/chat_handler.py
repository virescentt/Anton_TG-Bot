from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import MANAGER_IDS

from data.chat_storage_json import format_chat_history, get_active_chats_count, get_active_users_data, get_inactive_chats_count, get_inactive_users_data, get_receiver_id_status, get_waiting_count, get_waiting_users_data, load_chats, active_chats, save_chats
  

from utils.keyboards import InActive_chat_control_keyboard, InActive_chats_list_keyboard, active_chat_control_keyboard, admin_panel_keyboard, back_keyboard, back_to_admin_keyboard, confirm_keyboard, waiting_request_keyboard
from utils.states import ManagerState

chat_router = Router()



# Команда /admin для менеджеров
@chat_router.message(Command("admin"))
@chat_router.callback_query(F.data == "admin")
async def admin_panel(event: object):
    message = event.message if isinstance(event, types.CallbackQuery) else event
    
    if event.from_user.id not in MANAGER_IDS:
        return
    
    admin_text = (
        f"<b>АДМИНКА</b>\n\n"
        f"<i>Выберите категорию чатов/запросы, чтобы получить ее список пользователей и действий над ними.</i>\n\n"
        # f"==============================\n"
        f"🟢 Активных чатов: {get_active_chats_count()}\n"
        # f"------------------------------\n"
        f"🔴 Неактивных чатов: {get_inactive_chats_count()}\n"
        # f"------------------------------\n"
        f"⏳ Ожидающих запросов: {get_waiting_count()}\n"
        # f"==============================\n"
        f"\n <b>Всего чатов:</b> {get_inactive_chats_count() + get_waiting_count() + get_active_chats_count()}"
    )
    
    await message.answer(admin_text, reply_markup=admin_panel_keyboard())
    if isinstance(event, types.CallbackQuery):
        await event.answer()





# --- Просмотр активных чатов ---
@chat_router.callback_query(F.data == "admin_active_chats")
async def show_active_chats(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещен")
        return

    chats = load_chats()
    active_users = get_active_users_data()


    if not active_users:
        await callback.message.edit_text("📭 Активных чатов нет.", reply_markup=back_to_admin_keyboard())
        await callback.answer()
        return

    text = "<b>💬 Активные чаты. Выберите пользователя чтобы просмотреть инфу о чате. </b>\n\n"
    for i, (uid, data) in enumerate(active_users, start=1):
        manager = data.get("manager")
        manager_name = manager.get("first_name", "Не назначен")

        username = f"@{data['username']}" if data.get("username") else "—"
        text += f"{i}. 👤 {data['first_name']} ({username}) — 🧑‍💼 {manager_name}\n"

    await callback.message.edit_text(text, reply_markup=InActive_chats_list_keyboard(active_users))
    await callback.answer()



# --- Просмотр неактивных чатов ---
@chat_router.callback_query(F.data == "admin_inactive_chats")
async def show_inactive_chats(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещен")
        return

    chats = load_chats()
    inactive_users = get_inactive_users_data()


    if not inactive_users:
        await callback.message.edit_text("📭 Нективных чатов нет.", reply_markup=back_to_admin_keyboard())
        await callback.answer()
        return

    text = "<b>🔧 Неактивные чаты. Выберите пользователя чтобы просмотреть инфу о чате.</b>\n\n"
    for i, (uid, data) in enumerate(inactive_users, start=1):
        manager = data.get("manager")
        manager_name = manager.get("first_name", "Не назначен")

        username = f"@{data['username']}" if data.get("username") else "—"
        text += f"{i}. 👤 {data['first_name']} ({username}) — 🧑‍💼 {manager_name}\n"

    await callback.message.edit_text(text, reply_markup=InActive_chats_list_keyboard(inactive_users))
    await callback.answer()





# --- Просмотр очереди ожидания ---
@chat_router.callback_query(F.data == "admin_waiting_requests")
async def show_waiting_requests(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    chats = load_chats()
    waiting_users = get_waiting_users_data()

    if not waiting_users:
        await callback.message.edit_text("📭 Нет ожидающих пользователей.", reply_markup=back_to_admin_keyboard())
        await callback.answer()
        return

    for uid, data in waiting_users:
        last_message = (
            data["chat_history"][-1]["text"] if data.get("chat_history") else "Нет сообщений"
        )

        text = (
            f"💤 Ожидающий пользователь:\n"
            f"👤 Имя: {data['first_name']}\n"
            f"🆔 ID: {uid}\n"
            f"📛 Username: @{data['username'] if data['username'] else 'не указан'}\n\n"
            f"<b>Сообщение:</b> <i>{last_message}</i>"
        )

        await callback.message.answer(text, reply_markup=waiting_request_keyboard(uid))

    await callback.answer()



# --- Просмотр конкретного активного чата ---
@chat_router.callback_query(F.data.startswith("view_chat_"))
async def view_chat(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещен")
        return

    user_id = callback.data.split("_")[2]
    chats = load_chats()
    data = chats.get(user_id)
    is_active = False

    if not data:
        await callback.answer("❌ Чат не найден")
        return
    
    manager = data.get("manager", None)

    username = f"@{data['username']}" if data.get("username") else "—"

    if data["status"] == "active":
        mark = '🟢'
        is_active = True
    else:
        mark = '🔴'

    text_lines = [
        f"<b>Чат с пользователем:</b>\n",
        f"👤 {data['first_name']} ({username}) {mark}",
        f"🆔 ID: {user_id}",
        f"🧑‍💼 Менеджер: {manager['first_name'] if manager else '—'}",
        "\n-------------------------------\n"
        "📜 <b>История сообщений:</b>\n\n"
    ]

    history_lines = format_chat_history(user_id)
    text_lines.append(history_lines)
    
    # for msg in messages[-15:]:  # последние 15 сообщений
    # for msg in messages:
    #     role = "🧑 Менеджер" if msg["role"] == "manager" else "👤 "
    #     text_lines.append(f"{role}: {msg['text']}")

    text = "\n".join(text_lines)

    await callback.message.edit_text(text, reply_markup=InActive_chat_control_keyboard(uid=user_id, is_active=is_active))
    await callback.answer()



# --- Просмотр истории чата конкретного ожидающего ---
@chat_router.callback_query(F.data.startswith("history_request_"))
async def show_request_history(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[2]  # получаем ID пользователя из callback_data
    chats = load_chats()
    
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return

    # Форматируем всю историю сообщений
    history_text = format_chat_history(user_id)

    await callback.message.answer(history_text, reply_markup=back_keyboard("⬅️ Назад к запросу", "admin_waiting_requests"))
    await callback.answer()


# --- Удаление истории чата ---
@chat_router.callback_query(F.data.startswith("clear_chat_history_"))
async def clear_chat_history(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Доступ запрещён")
        return

    user_id = callback.data.split("_")[3]  # ID пользователя
    chats = load_chats()
    is_active = False

    
    if user_id not in chats:
        await callback.answer("❌ Чат не найден")
        return

    if chats[user_id]["chat_history"] == []:
        await callback.answer("История пуста")
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





# Команда /admin для менеджеров
@chat_router.message(Command("my_status"))
@chat_router.callback_query(F.data == "admin_my_status")
async def check_my_status(event: object):
    message = event.message if isinstance(event, types.CallbackQuery) else event
    chats = load_chats()

    myid = event.from_user.id
    
    if myid not in MANAGER_IDS:
        return
    
    print("myid:", myid)
    my_status = "Неактивны"

    key = f"{myid}_active"
    if key in active_chats:
        receiver_id, _= get_receiver_id_status(key)
        my_status = "Активны"
        receiver_first_name = chats.get(str(receiver_id), {}).get("first_name", "Без имени")

        text = (
            f"🟢 <b>{my_status}</b> с пользователем <b>{receiver_first_name}</b>."
        )
    else:
        text = (
            f"🔴 <b>{my_status}</b>."
        )

    await message.answer(text, reply_markup=back_keyboard("Админка", "admin"))
    if isinstance(event, types.CallbackQuery):
        await event.answer()

