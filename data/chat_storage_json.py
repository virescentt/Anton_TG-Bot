import json
from datetime import datetime
from pathlib import Path
import uuid
from aiogram import Bot, types
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext


"""
СТРУКТУРА
{
  "user_id": {
    "first_name": "Вася",
    "username": "vxrescent",
    "status": "active",  // "waiting", "inactive"
    "manager": {
            "id": 12345678,
            "first_name": "Петя",
            "username": "@jacob",
            "status": "active",
    },
    "chat_history": [
      {"role": "user", "text": "Привет!", "timestamp": "2025-10-13T23:00:00"},
      {"role": "manager", "text": "Здравствуйте!", "timestamp": "2025-10-13T23:01:00"}
    ]
  }
}
"""




CHAT_FILE = Path("data/chats.json")
# Проверяем и создаём файл, если его нет или он пустой
if not CHAT_FILE.exists() or CHAT_FILE.stat().st_size == 0:
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)



def load_chats():
    if CHAT_FILE.exists():
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)




def add_to_waiting(user_id: int, first_name: str, username: str = None, message_text: str = None, message_date=None):
    chats = load_chats()
    uid = str(user_id)

    # Если юзера нет — создаём
    if uid not in chats:
        chats[uid] = {
            "first_name": first_name,
            "username": username,
            "status": "waiting",
            "manager": None,
            "chat_history": []
        }
    else:
        # Если уже есть, просто обновляем статус
        chats[uid]["status"] = "waiting"
        # chats[uid]["manager"] = None  - если после очередного запроса хотим удалить менеджера

    # Добавляем сообщение в историю (если оно есть)
    if message_text:
        timestamp = (
            message_date.isoformat() if message_date else datetime.utcnow().isoformat()
        )
        chats[uid].setdefault("chat_history", []).append({
            "role": "user",
            "text": message_text,
            "timestamp": timestamp
        })

    save_chats(chats)
    update_chats_cache()


def set_status(user_id, status):
    chats = load_chats()
    if str(user_id) in chats:
        chats[str(user_id)]["status"] = status
        save_chats(chats)


def assign_manager(user_id, manager, manager_status="inactive"):
    
    chats = load_chats()

    # manager ---> callback.from_user
    if str(user_id) in chats:
        chats[str(user_id)]["manager"] = {  # None пока никто не принял заявку
            "id": manager.id,
            "first_name": manager.first_name,
            "username": manager.username if manager.username else "Не указан",
            "status": f"{manager_status}"  # или "inactive" при завершении чата
        }
        save_chats(chats)
        update_chats_cache()


def add_message(user_id, message: types.Message, role="user"): # МЕССЕДЖ ДОЛЖЕН БЫТЬ ТОЛЬКО ТЕКСТОВЫМ!!! или нет....
    chats = load_chats()
    uid = str(user_id)
    if uid not in chats:
        return

    timestamp = (
        message.date.isoformat() if getattr(message, "date", None) else datetime.utcnow().isoformat()
    )

    entry = {"role": role, "timestamp": timestamp}

    # Текст
    if message.text:
        entry.update({"type": "text", "text": message.text})

    # Фото
    elif message.photo:
        file_id = message.photo[-1].file_id
        key = uuid.uuid4().hex[:8]
        entry.update({"type": "photo", "file_id": file_id, "caption": message.caption, "file_key": key})

    # Документ
    elif message.document:
        file_id = message.document.file_id
        key = uuid.uuid4().hex[:8]
        entry.update({"type": "document", "file_id": file_id, "caption": message.caption, "filename": message.document.file_name, "file_key": key})

    # Видео
    elif message.video:
        file_id = message.video.file_id
        key = uuid.uuid4().hex[:8]
        entry.update({"type": "video", "file_id": file_id, "caption": message.caption, "file_key": key})

    # Голос
    elif message.voice:
        file_id = message.voice.file_id
        key = uuid.uuid4().hex[:8]
        entry.update({"type": "voice", "file_id": file_id, "file_key": key})

    # Стикер
    elif message.sticker:
        file_id = message.sticker.file_id
        key = uuid.uuid4().hex[:8]
        entry.update({"type": "sticker", "file_id": file_id, "file_key": key})

    else:
        return

    chats[uid].setdefault("chat_history", []).append(entry)
    save_chats(chats)

def get_waiting_count() -> int:
    """Количество ожидающих пользователей"""
    chats = load_chats()
    return sum(1 for data in chats.values() if data.get("status") == "waiting")


def get_active_chats_count() -> int:
    """Количество активных чатов"""
    chats = load_chats()
    return sum(1 for data in chats.values() if data.get("status") == "active")


def get_inactive_chats_count() -> int:
    """Количество неактивных чатов"""
    chats = load_chats()
    return sum(1 for data in chats.values() if data.get("status") == "inactive")






def get_users_by_status(status: str) -> list[tuple[int, dict]]:
    """Возвращает список (user_id, data) по заданному статусу"""
    chats = load_chats()
    return [(uid, data) for uid, data in chats.items() if data.get("status") == status]

def get_waiting_users_data() -> list[tuple[int, dict]]:
    return get_users_by_status("waiting")

def get_active_users_data() -> list[tuple[int, dict]]:
    return get_users_by_status("active")

def get_inactive_users_data() -> list[tuple[int, dict]]:
    return get_users_by_status("inactive")

    
def end_chat(uid):
    chats = load_chats()

    chats[uid]["status"] = "inactive"
    chats[uid]["manager"]["status"] = "inactive"
    save_chats(chats)
    update_chats_cache()


def format_chat_history(user_id: int, limit: int = 70) -> str:
    chats = load_chats()
    uid = str(user_id)
    if uid not in chats or not chats[uid].get("chat_history"):
        return "<I>🕸 История сообщений пуста.</i>"

    data = chats[uid]
    history = data["chat_history"][-limit:]
    user_name = data.get("first_name", "Пользователь")
    manager = data.get("manager")
    manager_name = manager.get("first_name") if isinstance(manager, dict) else "Менеджер"

    lines = []
    for msg in history:
        role_label = ("👤 " + user_name) if msg["role"] == "user" else ("👨‍💼 " + manager_name)
        ts = msg.get("timestamp", "Неизвестно")
        try:
            ts = datetime.fromisoformat(ts).strftime("%d.%m.%Y %H:%M")
        except Exception:
            pass

        mtype = msg.get("type", "text")

        if mtype == "text":
            content = msg.get("text", "")
            lines.append(f"{role_label} ({ts}):\n{content}")
        else:
            # пометка + псевдоссылка
            label = {
                "photo": "📷 Фото",
                "document": "📄 Документ",
                "video": "🎞 Видео",
                "voice": "🎤 Голос",
                "sticker": "💠 Стикер"
            }.get(mtype, mtype.upper())

            caption = msg.get("caption") or msg.get("filename") or ""
            key = msg.get("file_key")
            if key:
                lines.append(f"{role_label} ({ts}):\n{label}{(': ' + caption) if caption else ''}\nНажмите /getfile_{key} чтобы получить файл")
            else:
                lines.append(f"{role_label} ({ts}):\n{label}{(': ' + caption) if caption else ''}\n(файл недоступен)")
    return "\n\n".join(lines)




active_chats = {}

"""
active_chats = {
    # Формат: "user_id_status" -> "manager_id_status"
    "123_active": "789_active",           # оба активны
    "789_active": "123_active",           # обратная связь
    
    "456_active": "789_inactive",         # юзер активен, менеджер нет
    "789_inactive": "456_active",         # обратная связь
    
    "123_inactive": "999_active",         # юзер неактивен, менеджер активен  
    "999_active": "123_inactive"          # обратная связь
}
"""
# online_utils_funcs


def update_chats_cache():
    """Обновляем кеш из JSON с учетом всех статусов"""
    chats = load_chats()
    active_chats.clear()
    
    for user_id, data in chats.items():
        manager = data.get('manager')
        if manager:
            manager_id = str(manager['id'])
            user_status = data.get('status', 'inactive')  # active/inactive
            manager_status = manager.get('status', 'inactive')
            
            # Создаем пары в обе стороны
            active_chats[f"{user_id}_{user_status}"] = f"{manager_id}_{manager_status}"
            active_chats[f"{manager_id}_{manager_status}"] = f"{user_id}_{user_status}"


def get_receiver_id_status(key):
    # Получаем данные о получателе "receiver_id_status"
    receiver_data = active_chats[key]
    receiver_id, receiver_status = receiver_data.split("_")
    return int(receiver_id), receiver_status 