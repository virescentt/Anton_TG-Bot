# config.py
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_IDS = [int(x) for x in os.getenv("MANAGER_IDS", "").split(",") if x]
ALLOWED_UPDATES = ["message", "callback_query"]
VIDEO_PATH = "data/welcome.mp4"
VIDEO_FILE_ID = "BAACAgQAAxkBAAILmmj49Glmy9U3yYjAxP8fN5AHjSYJAALWIgAChtDJUw-UPMkZ_wSrNgQ"
START_TEXT = "Добро пожаловать в наш сервис!\n\n🎬 Выберите город для продвижения:"