import os
import re
import asyncio
import subprocess

from pyromod import Client
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

# =========================
# VARIABLES
# =========================

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

THUMBNAIL = "thumb.jpg"
COOKIES_FILE = "cookies.txt"

# =========================
# BOT START & STORAGE
# =========================

bot = Client(
    "UltraVideoBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

USER_DATA = {}
STOP_DOWNLOAD = {}

# =========================
# START & STOP COMMANDS
# =========================

@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        """
🔥 **Ultra-Advanced TXT Leech Bot**

**Commands:**
/txt - Upload TXT & Start Leech
/cookies - Upload Cookies File
/stop - Stop Current Batch
"""
    )

@bot.on_message(filters.command("stop"))
async def stop_command(client, message: Message):
    STOP_DOWNLOAD[message.chat.id] = True
    await message.reply_text("🛑 **Batch Stopped Successfully!**")

# =========================
# COOKIES COMMAND
# =========================

@bot.on_message(filters.command("cookies"))
async def cookies_command(client, message: Message):
    ask = await message.reply_text("📂 **Cookies TXT bhejo:**")
    cookie_msg: Message = await bot.listen(message.chat.id)
    
    if not cookie_msg.document:
        return await ask.edit("❌ **Invalid format! TXT file bhejo.**")
        
    await cookie_msg.download(file_name=COOKIES_FILE)
    await ask.edit("✅ **Cookies Saved Successfully!**")

# =========================
# TXT COMMAND (SEQUENTIAL)
# =========================

@bot.on_message(filters.command("txt"))
async def txt_command(client, message: Message):
    chat_id = message.chat.id

    ask = await message.reply_text("📂 **TXT file bhejo:**")
    txt_msg: Message = await bot.listen(chat_id)
    if not txt_msg.document:
        return await ask.edit("❌ TXT file required! Process cancelled.")
    txt_path = await txt_msg.download()

    await ask.edit("🏷 **Batch Name enter karo:**")
    batch_msg: Message = await bot.listen(chat_id)
    batch_name = batch_msg.text

    await ask.edit("📝 **Topic Name enter karo:**")
    topic_msg: Message = await bot.listen(chat_id)
    topic_name = topic_msg.text

    await ask.edit("👤 **Extract By (Your Name/Channel) enter karo:**")
    extract_msg: Message = await bot.listen(chat_id)
    extract_by = extract_msg.text

    USER_DATA[chat_id] = {
        "txt_path": txt_path,
        "batch_name": batch_name,
        "topic_name": topic_name,
        "extract_by": extract_by
    }

    # Best Quality button added here
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("144p", callback_data="144"),
                InlineKeyboardButton("240p", callback_data="240")
            ],
            [
                InlineKeyboardButton("360p", callback_data="360"),
                InlineKeyboardButton("480p", callback_data="480")
            ],
            [
                InlineKeyboardButton("720p", callback_data="720"),
                InlineKeyboardButton("1080p", callback_data="1080")
            ],
            [
                InlineKeyboardButton("🔥 Best Quality", callback_data="best")
            ]
        ]
    )

    await ask.edit(
        f"""
📊 **Details Saved!**

**Batch:** {batch_name}
**Topic:** {
    
