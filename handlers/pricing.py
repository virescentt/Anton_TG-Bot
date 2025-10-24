import json
from aiogram import Router, types, F
from utils.keyboards import contact_manager_keyboard, cities_keyboard

pricing_router = Router()

@pricing_router.callback_query(F.data.startswith("prices_"))
async def show_prices(callback: types.CallbackQuery):
    city = callback.data.replace("prices_", "")
    
    with open('data/prices.json', 'r', encoding='utf-8') as f:
        prices = json.load(f)
    
    if city in prices:
        city_prices = prices[city]
        text = f"💰 <b>Цены для {city}:</b>\n\n"
        
        for service, price in city_prices.items():
            text += f"• {service}: <b>{price}</b>\n"
        
        text += "\n⬇️ Свяжитесь с менеджером для заказа:"
        
        await callback.message.edit_text(text, reply_markup=contact_manager_keyboard(city=city))
    await callback.answer()

# # Обработчик кнопки "Назад к ценам"
# @pricing_router.callback_query(F.data == "back_to_pricing")
# async def back_to_pricing(callback: types.CallbackQuery):
#     # Здесь нужно получить город из контекста, но для простоты вернем к городам
#     await callback.message.delete()
#     await callback.message.answer(
#         "Выберите город для просмотра цен:",
#         reply_markup=cities_keyboard()
#     )
#     await callback.answer()