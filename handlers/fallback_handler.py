from aiogram import types, Router

fallback_router = Router()

@fallback_router.callback_query()
async def test(callback: types.CallbackQuery):
    print(f"Сработал fallback:", callback.data)
    await callback.answer()