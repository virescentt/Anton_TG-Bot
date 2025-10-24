import json
from aiogram import Router, types, F
from utils.keyboards import cities_groups_keyboard
from aiogram.fsm.context import FSMContext

group_router = Router()

@group_router.callback_query(F.data.startswith("city_"))
async def group_selection(callback: types.CallbackQuery, state: FSMContext):
    city = callback.data.replace("city_", "")
    
    with open('data/cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
    
    if city not in cities:
        await callback.message.answer("Такого города нет в списке!")
        return
            
    city_data = cities[city]
    
    text = ""
    lines = []

    lines.append(f'🏙️ <i>ГРУППЫ <b>{city_data["name"]}</b></i>:')
    
    for i, group_data in enumerate(city_data["groups"], start=1):
        # https://t.me/
        group_name = group_data.get("name", "Без имени")
        group_url = group_data.get("url", "")
        group_subs = group_data.get("subscribers", "-")
        group_avg_views = group_data.get("avg_views", "-")
        group_description = group_data.get("description", "-")

        group_text = (
            f'{i}. <b><a href="{group_url}">{group_name}</a></b>\n'
            f"👥Подписчики:<b> {group_subs}</b>\n"
            f"👀 Просмотры (за месяц):<b> {group_avg_views}\n</b>"
            f"<i>{group_description}</i>"
        )
        lines.append(group_text)
    
    text = "\n\n".join(lines)
                
    await state.update_data(picked_city=city)
    await state.update_data(picked_group=group_name)

    await callback.message.edit_text(text, reply_markup=cities_groups_keyboard(city_data["groups"], city=city,back_cb="start"), disable_web_page_preview=True)

    await callback.answer()


# Обработчик кнопки "Назад к городам"
# @group_router.callback_query(F.data == "back_to_cities")
# async def back_to_cities(callback: types.CallbackQuery):
#     await callback.message.delete()
#     await callback.message.answer(
#         "🎬 Выберите город для продвижения:",
#         reply_markup=cities_keyboard()
#     )
#     await callback.answer()
