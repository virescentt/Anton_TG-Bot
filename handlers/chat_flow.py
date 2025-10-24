from aiogram import Bot, types, F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from common.utils_funcs import msg_is_sent
from config import MANAGER_IDS
from data.chat_storage_json import add_message, assign_manager, end_chat, load_chats, save_chats,  update_chats_cache, active_chats, get_receiver_id_status


from utils.keyboards import manager_online_keyboard, new_message_keyboard
from utils.states import ManagerState, UserState

flow_router = Router()


# --- Начало чата с пользователем ---
@flow_router.callback_query(F.data.startswith("start_chat_"))
async def start_chat(callback: types.CallbackQuery):
    manager_id = callback.from_user.id

    if manager_id not in MANAGER_IDS:
        await callback.answer("❌ Нет доступа")
        return

     # Безопасное извлечение user_id
    try:
        user_id = callback.data.split("_")[2]
    except IndexError:
        await callback.answer("❌ Ошибка в данных кнопки")
        return
    
    chats = load_chats()
    if user_id not in chats:
        await callback.answer("<i>❌ Пользователь не найден</i>")
        return
    
    key = f"{manager_id}_active" 
    if key in active_chats:
        current_user_id, _ = get_receiver_id_status(key)

        end_chat(str(current_user_id))

        await callback.message.answer(
            f"<i>🔴 Чат с пользователем {chats[str(current_user_id)]['first_name']} завершён.</i>\n"
            f"<i>Пользователь добавлен в Неактивные чаты.</i>"
            )
        try:
            await callback.bot.send_message(int(current_user_id), "<i>🔴 <b>Чат был завершён менеджером.</b>\n\nСнова связаться с менеджером - /contact_manager.</i>")
        except:
            pass


    # Обновляем статус и добавляем менеджера
    assign_manager(user_id, callback.from_user, "active")
    
    
    chats = load_chats()
    
    chats[user_id]["status"] = "active"
    # chats[user_id]["manager"]["status"] = "active"

    
    save_chats(chats)
    update_chats_cache()

    await callback.message.answer(
        f"<i>✅ Вы начали чат с пользователем <b>{chats[user_id]['first_name']}</b>.</i>\n\n"
        f"<i>Теперь его и ваши сообщения будут копироваться друг другу в бота.</i>\n"
        f"<i>Чтобы отключиться самому и обрабатывать другие заявки, нажмите <u>Выйти из онлайн</u>, отключить обоих - <u>Завершить чат</u></i>",
        reply_markup=manager_online_keyboard(user_id)
    )

    # Уведомляем пользователя
    try:
        await callback.bot.send_message(
            int(user_id),
            "<i>🟢 Менеджер установил онлайн связь. Можете писать свои сообщения.</i>"
        )
    except:
        pass

    await callback.answer("Чат активирован.")

# --- Написать пользователю, т.е. статус = active для менеджера с этим юзером ---
@flow_router.callback_query(F.data.startswith("manager_activate_chat_"))
async def manager_activate_chat(callback: types.CallbackQuery):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Нет доступа")
        return

    user_id = callback.data.split("_")[3]
    chats = load_chats()
    if user_id not in chats:
        await callback.answer("<i>❌ Пользователь не найден</i>")
        return
    key = f"{callback.from_user.id}_active"
    if key in active_chats:
        curr_active_user, _ = get_receiver_id_status(key)
        await callback.message.answer(f'<i>🟢 Вы уже на связи с {chats[str(curr_active_user)]["first_name"]}.</i>')
        await callback.answer()
        return
    
    # Обновляем статус и добавляем менеджера
    chats[user_id]["manager"]["status"] = "active"


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ПОКА ЧТО ТАК, МОЖЕТ И ВСЕГДА ТАК
    chats[user_id]["status"] = "active"

    
    save_chats(chats)
    update_chats_cache()


    await callback.message.answer(
        f"<i>🟢<b> Вы снова в онлайн для пользователя {chats[user_id]['first_name']}</b>.</i>\n\n"
        f"<i>Чтобы отключиться самому и обрабатывать другие заявки, нажмите <u>Выйти из онлайн</u>.\nОтключить обоих - <u>Завершить чат</u></i>",
        reply_markup=manager_online_keyboard(user_id)
    )

    # Уведомляем пользователя
    try:
        await callback.bot.send_message(
            int(user_id),
            "<i>🟢 Менеджер в чате.</i>"
        )
    except:
        pass
    
    # Состояние для менеджера

    await callback.answer("Чат активирован.")


# --- Завершение чата менеджером---
@flow_router.callback_query(F.data.startswith("end_chat_"))
async def manager_end_chat(callback: types.CallbackQuery):

    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Нет доступа")
        return

    user_id = callback.data.split("_")[2]
    chats = load_chats()
    if user_id not in chats:
        await callback.answer("❌ Пользователь не найден")
        return

    end_chat(user_id)

    await callback.message.answer(
        f"<i>🔴 Чат с пользователем {chats[user_id]['first_name']} завершён.</i>\n"
        f"<i>Пользователь добавлен в Неактивные чаты.</i>"
        )
    try:
        await callback.bot.send_message(int(user_id), "<i>🔴 <b>Чат был завершён менеджером.</b>\n\nСнова связаться с менеджером - /contact_manager.</i>")
    except:
        pass
    

    await callback.answer()
    


# --- Завершение чата пользователем ---
@flow_router.message(Command("end_chat"))
async def user_end_chat(message: types.Message):
    user_id = str(message.from_user.id)
    chats = load_chats()
    if user_id not in chats or chats[user_id].get("status", "inactive") == "inactive":
        await message.answer("<i>❌ Вы не в онлайн связи с менеджером.</i>")
        return
    manager_id = chats[user_id]["manager"]["id"]

    end_chat(user_id)

    await message.answer(
        "<i>🔴 <b>Чат был завершён Вами.</b>\n\nЕсли у Вас остались вопросы, можете связаться с менеджером снова командой /contact_manager</i>"
        )
    try:
        await message.bot.send_message(int(manager_id),
        f"<i>🔴 Чат с {chats[user_id]['first_name']} был завершён пользователем для обоих.</i>\n"
        f"<i><b>{chats[user_id]['first_name']}</b> добавлен в Неактивные чаты.</i>")
    except:
        pass



# --- Выход менеджера из онлайн режима ---
@flow_router.callback_query(F.data.startswith("leave_chat_"))
async def leave_chat(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in MANAGER_IDS:
        await callback.answer("❌ Нет доступа")
        return

    user_id = callback.data.split("_")[2]
    chats = load_chats()
    if user_id not in chats:
        await callback.message.answer("❌ Пользователь не найден")
        await callback.answer()
        return
    
    if chats[user_id]["manager"]["status"] == "inactive":
        await callback.answer("❌ Вы не онлайн")
        return
    
    
    # Не завершаем чат — просто "отключаем" менеджера
    chats[user_id]["manager"]["status"] = "inactive"

    save_chats(chats)
    update_chats_cache()

    await callback.message.answer(f'<i>🚪 Вы вышли из онлайн-режима с { chats[user_id]["first_name"]} для себя.</i>')
    await callback.answer()

    try:
        await callback.bot.send_message(
            int(user_id),
            "<i>🕓 Менеджер отошел..</i>\n\n" \
            "<i>Прервать связь с менеджером - /end_chat</i>"
        )
    except:
        pass


@flow_router.message(UserState.in_chat_with_manager)
async def handle_user_message(message: types.Message):
    user_id = str(message.from_user.id)
    chats = load_chats()
    if user_id not in chats:
        return  # пользователь не зарегистрирован в JSON

    data = chats[user_id]
    add_message(user_id, message, role="user")  # добавляем в историю

    manager = data.get("manager")
    if not manager:
        await message.answer("<i>❌ Менеджер не назначен. Попробуйте связаться снова - /contact_manager</i>")
        return

    manager_id = manager["id"]
    manager_status = manager.get("status", "inactive")

    # Если менеджер активен с этим пользователем — отправляем сообщение сразу
    # Менеджер не активен — уведомляем его

    await message.bot.send_message(
        manager_id,
        # (@{data.get('username','не указан')})
        f"<i>📩 Новое сообщение от <b>{data['first_name']}</b>:<i>\n"
        f"{message.text or '<i>[медиа]</i>'}",
        reply_markup=new_message_keyboard(user_id)
    )

    add_message(user_id, message, role="user")
    save_chats(chats)
    update_chats_cache()


@flow_router.message(ManagerState.in_chat_with_user)
async def handle_manager_message(message: types.Message):


    # Ищем, с кем у этого менеджера активный чат
    managers_active_uid = ManagerState.manager_active_with
    
    if not managers_active_uid:
        await message.answer("<i>⚠ Вы не находитесь в активном чате. Выберите пользователя, чтобы ответить.</i>")
        return

    # Добавляем в историю
    add_message(managers_active_uid, message, role="manager")

    prefix = f"👨‍💼 Менеджер {message.from_user.first_name}:"

    try:
        # Универсальный вариант для любых типов сообщений

        await message.bot.copy_message(
            chat_id=int(managers_active_uid),
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        await message.answer("<i>Отправлено 🛫</i>")


    except Exception as e:
        print("Ошибка при отправке пользователю:", e)




@flow_router.message()
async def handle_all_messages(message: types.Message):
    # Игнорируем команды
    if message.text and message.text.startswith("/"):
        return

    sender_id = str(message.from_user.id)
    chats = load_chats()
    
    # Определяем тип отправителя
    is_manager = False
    if message.from_user.id in MANAGER_IDS:
        is_manager = True
    elif sender_id not in chats:
        raise KeyError(f"Пользователь {sender_id} не найден в chats.json")
    
    # Ищем получателя и его статус
    receiver_id = None
    receiver_status = None
    

    # если отправляющий в активном статусе
    key = f"{sender_id}_active" 
    if key in active_chats:
        
        # данные получателя
        receiver_id, receiver_status = get_receiver_id_status(key)

        # Получатель есть, отправка от менеджера
        if is_manager and receiver_id:

            try:
                print(active_chats)

                await message.bot.copy_message(
                    chat_id=receiver_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                await msg_is_sent(message, receiver_id)
                add_message(receiver_id, message, role="manager")


            except Exception as e:
                print(f"Ошибка при отправке пользователю: ", e)

        # Получатель есть, отправка от юзера
        elif receiver_id:
            if receiver_status == "active":
                # менеджер активен, перешлем ему сообщение
                try:
                    # print(active_chats)

                    await message.bot.forward_message(
                        chat_id=receiver_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    # await message.bot.send_message(
                    #     receiver_id,
                    #     f"👤 <b>{chats[sender_id]['first_name']}</b>:\n{message.text or '[📃 не текствое сообщение]'}"
                    # )
                    await msg_is_sent(message, receiver_id)

                    # при желании можно пересылать реальные медиа, используя file_id
                    add_message(receiver_id, message, role="user")

                except Exception as e:
                    print("Ошибка при пересылке менеджеру: ", e)


            elif receiver_status == "inactive":
                # Менеджер не активен — уведомляем его
                try:
                    await message.bot.send_message(
                        receiver_id,
                        # (@{data.get('username','не указан')})
                        f"📩 Новое сообщение от <b>{chats[sender_id]['first_name']}</b> :\n"
                        f"{message.text or '<i>[медиа]</i>'}",
                        reply_markup=new_message_keyboard(sender_id)
                    )
                    await msg_is_sent(message, receiver_id)
                    add_message(receiver_id, message, role="user")
                except Exception as e:
                    print("Ошибка при пересылке менеджеру:", e)
            else:
                raise ValueError(receiver_status, "Такой статус (менеджера) не обрабатывается.")
        else:
            if is_manager:
                await message.answer("<i>❌ Такой связки менеджер --> пользователь <b>нет</b>. Выберите другого пользователя.</i>")
            else:
                await message.answer("<i>❌ Менеджер не назначен. Попробуйте связаться снова - /contact_manager</i>")
    # если отправляющий в неактивном статусе
    else:
        if is_manager:
            await message.answer("<i>⚠ Вы не находитесь в активном чате с пользователем.</i>")
        else:
            await message.answer("<i>⚠ Вы не находитесь в активном чате с менеджером.\n\n/contact_manager для связи 📞</i>")