import os
import re
import time
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

# Storage Dictionaries
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

    # 1. Ask for TXT
    ask = await message.reply_text("📂 **TXT file bhejo:**")
    txt_msg: Message = await bot.listen(chat_id)
    if not txt_msg.document:
        return await ask.edit("❌ TXT file required!")
    txt_path = await txt_msg.download()

    # 2. Ask Batch Name
    await ask.edit("🏷 **Batch Name enter karo:**")
    batch_msg: Message = await bot.listen(chat_id)
    batch_name = batch_msg.text

    # 3. Ask Topic Name
    await ask.edit("📝 **Topic Name enter karo:**")
    topic_msg: Message = await bot.listen(chat_id)
    topic_name = topic_msg.text

    # 4. Ask Extract By
    await ask.edit("👤 **Extract By (Your Name/Channel) enter karo:**")
    extract_msg: Message = await bot.listen(chat_id)
    extract_by = extract_msg.text

    # Store all data securely for this user
    USER_DATA[chat_id] = {
        "txt_path": txt_path,
        "batch_name": batch_name,
        "topic_name": topic_name,
        "extract_by": extract_by
    }

    # Quality Selection
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
            ]
        ]
    )

    await ask.edit(
        f"""
📊 **Details Saved!**

**Batch:** {batch_name}
**Topic:** {topic_name}
**By:** {extract_by}

📺 **Video Quality Select Karo:**
""", 
        reply_markup=buttons
    )

# =========================
# DOWNLOAD CORE
# =========================

@bot.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    await callback_query.answer("Processing Batch...", show_alert=False)
    
    quality = callback_query.data
    chat_id = callback_query.message.chat.id
    data = USER_DATA.get(chat_id)

    if not data:
        return await callback_query.message.edit_text("❌ **Session expired. Please send /txt again.**")

    STOP_DOWNLOAD[chat_id] = False
    await callback_query.message.edit_text(f"✅ **Started Processing in {quality}p...**")

    # Read and Parse TXT (Supports "Video Name: https://link")
    with open(data["txt_path"], "r", encoding="utf-8") as f:
        lines = f.readlines()

    videos = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Smart Regex to split Title and Link
        match = re.search(r'(.*?)(https?://\S+)', line)
        if match:
            v_title = match.group(1).strip(' :|-') # Removes extra colons/spaces
            v_url = match.group(2)
            if not v_title:
                v_title = "No Title Found"
            videos.append((v_title, v_url))

    if not videos:
        return await bot.send_message(chat_id, "❌ **No valid links found in the TXT file.**")

    total = len(videos)
    success, failed = 0, 0

    for count, (vid_title, url) in enumerate(videos, start=1):
        if STOP_DOWNLOAD.get(chat_id):
            await bot.send_message(chat_id, "🛑 **Batch stopped by user.**")
            break

        # Fallback Title if missing
        if vid_title == "No Title Found":
            vid_title = f"Video {count}"

        filename = f"Video_{count}.mp4"
        status_msg = await bot.send_message(
            chat_id,
            f"⬇️ **Downloading Video {count} / {total}**\n\n📌 **Title:** `{vid_title}`\n📺 **Quality:** {quality}p"
        )

        try:
            cookies_cmd = f'--cookies {COOKIES_FILE} ' if os.path.exists(COOKIES_FILE) else ''
            
            cmd = (
                f'yt-dlp '
                f'-f "bestvideo[height<={quality}]+bestaudio/best[height<={quality}]" '
                f'--merge-output-format mp4 '
                f'{cookies_cmd}'
                f'--retries 10 '
                f'-o "{filename}" '
                f'"{url}"'
            )

            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()

            if os.path.exists(filename):
                await status_msg.edit("⬆️ **Uploading to Telegram...**")
                
                # Custom Caption Configuration
                final_caption = (
                    f"📁 **Batch Name :** {data['batch_name']}\n\n"
                    f"📝 **Topic Name :** {data['topic_name']}\n"
                    f"🎬 **Video Title :** {vid_title}\n"
                    f"**[{{🎥}}] Video ID :** {count:02d}\n\n"
                    f"👤 **Extract By :** {data['extract_by']}"
                )

                video_kwargs = {
                    "chat_id": chat_id,
                    "video": filename,
                    "caption": final_caption,
                    "supports_streaming": True
                }
                
                if os.path.exists(THUMBNAIL):
                    video_kwargs["thumb"] = THUMBNAIL

                await bot.send_video(**video_kwargs)
                os.remove(filename)
                success += 1
                await status_msg.delete()

            else:
                failed += 1
                await status_msg.edit(f"❌ **Failed to download Video {count}**")

        except Exception as e:
            failed += 1
            await bot.send_message(chat_id, f"❌ **Error On Video {count}**\n\n`{str(e)}`")

    # Final Summary
    await bot.send_message(
        chat_id,
        f"✅ **Batch Completed!**\n\n"
        f"📦 **Total :** {total}\n"
        f"✅ **Success :** {success}\n"
        f"❌ **Failed :** {failed}"
    )

# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
    print("🚀 Ultra-Advanced Bot Started!")
    bot.run()
    
