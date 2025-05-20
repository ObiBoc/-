import os
import threading
from pyrogram import Client, filters, types, enums
import logging, random, asyncio

from background import start_server  # Импорт Flask-сервера

# Получаем переменные окружения
TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")

class Logger:
    def __init__(self, filename=None, logging_format="[%(asctime)s] [%(levelname)s]: %(message)s") -> None:
        self.filename = filename
        self.level = logging.INFO
        self.format = logging_format

        if filename:
            logging.basicConfig(level=self.level, format=self.format, filename=filename, filemode="a+")
        else:
            logging.basicConfig(level=self.level, format=self.format)

        self.logger = logging.getLogger(__name__)

    def error(self, message): self.logger.error(message)
    def warning(self, message): self.logger.warning(message)
    def info(self, message): self.logger.info(message)
    def critical(self, message): self.logger.critical(message)

class App:
    def __init__(self, api_id, api_hash, token):
        self.client = Client(
            "zazyvala",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=token,
            parse_mode=enums.ParseMode.HTML
        )

    def run(self):
        self.client.run()

logger = Logger()
app = App(API_ID, API_HASH, TOKEN)
client = app.client

def full_name(msg: types.Message) -> str:
    return f"{msg.from_user.first_name}{' ' + msg.from_user.last_name if msg.from_user.last_name else ''}"

async def empty_char() -> str:
    return "⁠"

@client.on_message(filters.command(["start"], prefixes=["/", ".", "!"]))
async def start_cmd(_, msg: types.Message):
    try:
        await msg.reply(f"<b>Привет, {full_name(msg)}!</b> Используй команду /all или @all в чате.")
    except Exception as e:
        logger.error(e)

@client.on_message(filters.command(["all", "@all", ".все", ".всем", ".призыв", "калл", ".all"], prefixes=[".", "/", "!", "@", ""]) & filters.group)
async def tag_cmd(_, msg: types.Message):
    try:
        members = [member async for member in client.get_chat_members(msg.chat.id)]
        users = [m for m in members if m.user and not m.user.is_bot and not m.user.is_deleted]

        command_parts = msg.text.split(maxsplit=1)
        args = command_parts[1] if len(command_parts) > 1 else ""

        mentioned_users = "Внимание!"
        for user in users:
            mentioned_users += f"<a href='tg://user?id={user.user.id}'>{await empty_char()}</a>"
        if args:
            mentioned_users += f"\n{args}"
        mentioned_users += "\nСпасибо за внимание."

        await client.send_message(chat_id=msg.chat.id, text=mentioned_users)
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    # Запускаем Flask-сервер в фоне
    threading.Thread(target=start_server, daemon=True).start()

    logger.info("START BOT")
    app.run()
