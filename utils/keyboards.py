import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from data.chat_storage_json import load_chats

def cities_keyboard():
    cities_kb = InlineKeyboardBuilder()
        
    with open('data/cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
    
    for city, city_data in cities.items():
        cities_kb.button(
            text=city_data["name"],
            callback_data=f"city_{city}")
    
    cities_kb.adjust(1,1) # одна кнопка на ряд. И так по дефолту
    return cities_kb.as_markup()


def cities_groups_keyboard(groups_data, city, back_cb="start"):
    group_kb = InlineKeyboardBuilder()

    for i, group_data in enumerate(groups_data, start=1):
        group_name = group_data.get("name", "Без имени")
        group_kb.button(
            text=f"{i}. {group_name}",
            callback_data=f"prices_{city}")
   
    # group_kb.button(
    #     text="💰 Узнать цены",
    #     callback_data=f"prices_{city}")
    
    # group_kb.button(
    #     text="👨‍💼 Связаться с менеджером",
    #     callback_data=f"contact_manager")

    group_kb.button(
        text="⬅ Назад",
        callback_data=back_cb)
    
    group_kb.adjust(1)
    return group_kb.as_markup()
    

# def pricing_keyboard(city, back_cb="start"):
#     pricing_kb = InlineKeyboardBuilder()
#     pricing_kb.button(
#         text="💰 Узнать цены",
#         callback_data=f"prices_{city}")
#     pricing_kb.button(
#         text="👨‍💼 Связаться с менеджером",
#         callback_data=f"contact_manager")
#     pricing_kb.button(
#         text="🔙",
#         callback_data=back_cb)
#     pricing_kb.adjust(2)
#     return pricing_kb.as_markup()
    


def contact_manager_keyboard(city="tri_city"):
    contact_manager_kb = InlineKeyboardBuilder()
    
    contact_manager_kb.button(
        text="👨‍💼 Связаться с менеджером",
        callback_data="contact_manager")
    contact_manager_kb.button(
        text="⬅ Назад",
        callback_data=f"city_{city}")
    contact_manager_kb.adjust(1)
    return contact_manager_kb.as_markup()
    

def cancel_contact_manager_keyboard():
    ccm_kb = InlineKeyboardBuilder()
    ccm_kb.button(
        text="❌ Отменить",
        callback_data="cancel_contact_manager")
    return ccm_kb.as_markup()
    





# --- Админка ---
# Активные чаты
# Неактивные чаты
# Ожидающие запросы
def admin_panel_keyboard():
    kb = InlineKeyboardBuilder()

    kb = InlineKeyboardBuilder()
    kb.button(text="🟢 Активные", callback_data="admin_active_chats")
    kb.button(text="🔴 Неактивные", callback_data="admin_inactive_chats")
    kb.button(text="⏳ Ожидающие запросы", callback_data="admin_waiting_requests")
    kb.button(text="👀 Мой статус", callback_data="admin_my_status")
    kb.adjust(2)
    return kb.as_markup()


# --- Список активных/неактивных чатов ---
# Кнопка на конкретного активного пользователя
# ...
# Админка
def InActive_chats_list_keyboard(users_list):
    kb = InlineKeyboardBuilder()
    for i, (uid, data) in enumerate(users_list, start=1):
        kb.button(text=f"{i}. {data['first_name']}", callback_data=f"view_chat_{uid}")
    kb.button(text="⬅ Назад", callback_data="admin")
    kb.adjust(3, 1)
    return kb.as_markup()



def back_to_admin_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Админка", callback_data="admin")
    return kb.as_markup()



def InActive_chat_control_keyboard(is_active, uid, confirm_cb_name="confirm_delete_user"):
    if is_active:
        return active_chat_control_keyboard(uid)
    else:
        return inactive_chat_control_keyboard(uid, confirm_cb_name)

# --- Управления активным чатом ---
# Завершить чат если он еще не завершен пользователем
# Удалить историю чата
# Написать
# Назад (к списку активных чатов)
def active_chat_control_keyboard(uid):
    kb = InlineKeyboardBuilder()

    chats = load_chats()
    manager_status = chats[uid]["manager"]["status"]
    if manager_status == "active":
        kb.button(text="🔴🔴 Завершить чат", callback_data=f"end_chat_{uid}")
        kb.button(text="🚪 Выйти из онлайн", callback_data=f"leave_chat_{uid}")
        kb.button(text="🧹 Очистить историю", callback_data=f"confirm_clear_chat_history_{uid}")
        kb.button(text="⬅ Назад", callback_data="admin_active_chats")
        kb.adjust(2, 1)
        return kb.as_markup()
    
    else:
        kb.button(text="🔴 Завершить чат", callback_data=f"end_chat_{uid}")
        kb.button(text="📤 Написать", callback_data=f"manager_activate_chat_{uid}")
        kb.button(text="🧹 Очистить историю", callback_data=f"confirm_clear_chat_history_{uid}")
        kb.button(text="⬅ Назад", callback_data="admin_active_chats")
        kb.adjust(2, 1)
        return kb.as_markup()




# --- Управления неактивным чатом ---
# Начать чат (для обоих)
# Удалить историю чата
# Удалить из базы полностью
# Назад (к списку неактивных чатов)
def inactive_chat_control_keyboard(uid, confirm_cb_name="confirm_delete_user"):
    kb = InlineKeyboardBuilder()
    kb.button(text="🟢🟢 Начать чат", callback_data=f"start_chat_{uid}")
    kb.button(text="🧹 Очистить историю", callback_data=f"confirm_clear_chat_history_{uid}")
    kb.button(text="🚯 Удалить из базы", callback_data=f"{confirm_cb_name}_{uid}")
    kb.button(text="⬅ Назад", callback_data=f"admin_inactive_chats")
    kb.adjust(2, 1)
    return kb.as_markup()


# --- Начатый чат/написать для менеджера ---
def manager_online_keyboard(uid):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔴🔴 Завершить чат", callback_data=f"end_chat_{uid}")
    kb.button(text="🚪 Выйти из онлайн", callback_data=f"leave_chat_{uid}")
    kb.adjust(2)
    return kb.as_markup()


def manager_request_keyboard(uid):
    kb = InlineKeyboardBuilder()

    btn1 = InlineKeyboardButton(
        text="🟢🟢 Начать чат",
        callback_data=f"start_chat_{uid}"
        )
    btn2 = InlineKeyboardButton(
        text="Админка",
        callback_data="admin"
        )
  
    kb.add(
        btn1,
        btn2
    )

    return kb.as_markup()


# --- Ожидающий запрос ---
def waiting_request_keyboard(uid):
    kb = InlineKeyboardBuilder()
    kb.button(text="🟢🟢 Начать чат", callback_data=f"start_chat_{uid}")
    kb.button(text="🗑 Удалить запрос", callback_data=f"confirm_delete_request_{uid}")
    kb.button(text="История чата", callback_data=f"history_request_{uid}")
    kb.adjust(2)
    return kb.as_markup()


def back_keyboard(text: str, cb_data: str):
    kb = InlineKeyboardBuilder()

    btn1 = InlineKeyboardButton(
        text=text,
        callback_data=cb_data
        )
    kb.add(
        btn1
    )

    return kb.as_markup()


# --- Начатый чат/написать для менеджера ---
def new_message_keyboard(uid):
    kb = InlineKeyboardBuilder()
    kb.button(text="Написать", callback_data=f"manager_activate_chat_{uid}")
    kb.button(text="Инфа о чате", callback_data=f"view_chat_{uid}")
    kb.adjust(2)
    return kb.as_markup()

# --- Подтвердить удаление запроса ---
def confirm_keyboard(confirm_cb_name, uid):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data=f"{confirm_cb_name}_{uid}")
    kb.button(text="❌ Отмена", callback_data=f"cancel_confirm")
    kb.adjust(2)
    return kb.as_markup()




