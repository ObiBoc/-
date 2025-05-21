import os
import threading
import logging
from pyrogram import Client, filters, types, enums
from pyrogram.enums import ChatMemberStatus
from pyrogram.handlers import ChatMemberUpdatedHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from background import start_server

TOKEN = os.getenv("BOT_TOKEN", "8153701407:AAFqW7hv-eeF4dgkHb2Usjr3i0atiOhXnIM")
API_ID = int(os.getenv("API_ID", "28833157"))
API_HASH = os.getenv("API_HASH", "36fd7803fd4b53ee2f421f547e010cdb")

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
    return "⁣"

@client.on_message(filters.command(["start"], prefixes=["/", ".", "!"]))
async def start_cmd(_, msg: types.Message):
    try:
        await msg.reply(f"Привет, {full_name(msg)}!\nИспользуй команду /all в группе для созыва всех ее учасников\nИспользуй команду /help для получения полного списка возможностей бота")
    except Exception as e:
        logger.error(e)

@client.on_message(filters.command(["help"], prefixes=["/", ".", "!"]))
async def help_cmd(_, msg: types.Message):
    try:
        text = (
            "<b>Команды:</b>\n\n"
            "/all или @all или /all [сообщение] — упоминает всех участников группы\n"
            "Можно добавить сообщение, оно будет отображено после упоминаний\n\n"
            "/help - выводит это сообщение"
        )
        await msg.reply(text)
    except Exception as e:
        logger.error(e)

@client.on_message(filters.command(["all", "@all"], prefixes=["/", "@"]))
async def tag_cmd(_, msg: types.Message):
    try:
        if msg.chat.type == enums.ChatType.PRIVATE:
            bot_username = (await client.get_me()).username
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Добавить в группу", url=f"https://t.me/{bot_username}?startgroup=true")]]
            )
            await msg.reply("Эту команду можно использовать только в группах", reply_markup=keyboard)
            return

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

async def welcome_bot(client, update: types.ChatMemberUpdated):
    try:
        old = update.old_chat_member
        new = update.new_chat_member
        if not old or not new or not new.user:
            return
        if new.user.is_self and new.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
            await client.send_message(
                chat_id=update.chat.id,
                text="Всем привет!\nИспользуйте /all для упоминания всех участников чата"
            )
    except Exception as e:
        logger.error(e)

client.add_handler(ChatMemberUpdatedHandler(welcome_bot))

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    logger.info("START BOT")
    app.run()
