import json
from aiogram import types
from aiogram.fsm.context import FSMContext

from config import MANAGER_IDS, START_TEXT
from data.chat_storage_json import add_to_waiting, get_waiting_count, load_chats
from utils.keyboards import cities_keyboard, manager_request_keyboard
from utils.states import UserState

async def new_request(message: types.Message, state: FSMContext, user: types.User, city, group, init_message=""):
    username = user.username if user.username else "Не указан"
    first_name = user.first_name
    uid = user.id


    add_to_waiting(uid, first_name, username, init_message, message.date)
    
    chats = load_chats()

    user_info = (
        f'i>Запрос от <b>{"🆕 нового " if chats[str(uid)]["manager"] == None else ""}</b>пользователя:\n\n</i>'
        f"👤 Имя: {first_name}\n"
        f"🆔 ID: {uid}\n"
        f"📛 Username: @{username}\n"
        f"🌆 Город/Группа: {city}/{group}\n\n"
        
        f"<b>Сообщение:</b> <i>{init_message}</i>"
    )

    queue_info = f"\n\n📊 В очереди: {get_waiting_count()} пользователей"

    for manager_id in MANAGER_IDS:
        try:
            await message.bot.send_message(
                manager_id,
                user_info + queue_info,
                reply_markup=manager_request_keyboard(str(user.id))
            )
            # уведомляем пользователя
            await message.answer(
                "✅ <b>Отправлено</b>.\n"
                "⏳ <i>Ожидайте менеджера..</i>\n\n"
                "<i>Вы сможете общаться в онлайн режиме прямо здесь.</i>"
            )
        except Exception as e:
            # уведомляем пользователя
            await message.answer(
                "❌ Ваше сообщение не смогло отправиться менеджеру.\n"
                "Попробуйте позже."
            )
            print(f"Ошибка отправки менеджеру {manager_id}: {e}")

    await state.clear()


async def render_cities_start_pick(event: object, text=START_TEXT):
    message = event.message if isinstance(event, types.CallbackQuery) else event

    await message.answer(text=text,
        reply_markup=cities_keyboard()
    )

    if isinstance(event, types.CallbackQuery):  
        await event.answer()


# async def render_cities_groups_card(message: types.Message, city: str, state: FSMContext):
#     """Показ карточки выбранного города."""
#     with open("data/cities.json", "r", encoding="utf-8") as f:
#         cities = json.load(f)

#     city_data = cities.get(city)
#     if not city_data:
#         await message.edit_text("Город не найден.", reply_markup=cities_keyboard())
#         return

#     text = (
#             f"🏙️ <b>{city}</b>\n\n"
#             f"📊 Подписчики: {city_data['subscribers']}\n"
#             f"👀 Просмотры в месяц: {city_data['views']}\n"
#             f"📝 {city_data['description']}"
#         )
#     print("Город: " + city)
#     await state.update_data(picked_city=city)
#     await message.edit_text(text, reply_markup=pricing_keyboard(city))


async def msg_is_sent(msg: types.Message, receiver_id=0):
    chats = load_chats()
    if int(receiver_id) in MANAGER_IDS:
        receiver_first_name = "Менеджеру"
        await msg.answer(f"<i>Отправлено {receiver_first_name} 🛫</i>")
    elif receiver_id:
        receiver_first_name = chats.get(str(receiver_id), {}).get("first_name", "Без имени")
        await msg.answer(f"<i>Отправлено {receiver_first_name} 🛫</i>")
    else:
        await msg.answer(f"<i>Отправлено {receiver_id}, ???? 🛫</i>")
