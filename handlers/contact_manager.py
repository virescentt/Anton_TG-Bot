from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from common.utils_funcs import new_request
from utils.states import UserState
from utils.keyboards import cancel_contact_manager_keyboard, cities_keyboard
from data.chat_storage_json import active_chats

contact_router = Router()


@contact_router.message(Command("contact_manager"))
@contact_router.callback_query(F.data == "contact_manager")
async def contact_manager_command_message(event: object, state: FSMContext):
    message = event.message if isinstance(event, types.CallbackQuery) else event
    if (f"{event.from_user.id}_active") in active_chats:
        await message.answer("<i>🟢 Вы уже на связи с Менеджером. Можете писать сообщения.</i>")
        if isinstance(event, types.CallbackQuery):
            event.answer()
        return
    
    if isinstance(event, types.CallbackQuery):
        await state.update_data(prev_msg_id=message.message_id)
        await message.answer(
        "Напишите краткое сообщение для менеджера. Свободный менеджер ответит Вам в ближайшее время.",
        reply_markup=cancel_contact_manager_keyboard()
    )    
        await event.answer()
    
    else:    
        await message.answer(
            "Напишите краткое сообщение для менеджера. Свободный менеджер ответит Вам в ближайшее время.",
            reply_markup=cancel_contact_manager_keyboard()
        )

    await state.set_state(UserState.waiting_for_initial_text)




@contact_router.message(UserState.waiting_for_initial_text)
async def user_initial_message(message: types.Message, state: FSMContext):
    # если сообщение не текстовое (например, фото, видео, документ)
    if not message.text:
        await message.answer("Отправьте текстовое сообщение.")
        return
    
    await state.update_data(init_message=message.text)
    
    data = await state.get_data()
    city = data.get("picked_city", "Не выбран")
    group = data.get("picked_group", "Не выбран")
    msg = data.get("init_message", "Нет")
    
    await new_request(message, state, message.from_user, city=city, group=group, init_message=msg)




@contact_router.callback_query(F.data == "cancel_contact_manager")
async def cancel_contact_manager(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    city = data.get("picked_city")
    prev_msg_id = data.get("prev_msg_id")

    await state.clear()

    # Если prev_msg_id есть (значит был callback)
    try:
        # 2nd parametr: prev_msg_id if prev_msg_id else callback.message.message_id
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
        
        await callback.answer("Отменено.")
    except Exception:
        pass    

    # # Показываем карточку города или список
    # if city:
    #     await render_cities_groups_card(callback.message, city, state)