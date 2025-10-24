from aiogram import Router, types, F
from common.utils_funcs import render_cities_start_pick
from aiogram.fsm.context import FSMContext


back_to_router = Router()


@back_to_router.callback_query(F.data.startswith("back_to_"))
async def back_to(callback: types.CallbackQuery, state: FSMContext):
    render_fun_name = callback.data[8:]

    if render_fun_name == "render_cities_start_pick":
        await render_cities_start_pick(callback)
    await callback.answer()