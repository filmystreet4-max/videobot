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
    
    quality_text = "Best" if quality == "best" else f"{quality}p"
    await callback_query.message.edit_text(f"✅ **Started Processing in {quality_text} Quality...**")

    with open(data["txt_path"], "r", encoding="utf-8") as f:
        lines = f.readlines()

    videos = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.search(r'(.*?)(https?://\S+)', line)
        if match:
            v_title = match.group(1).strip(' :|-')
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

        is_pdf = url.lower().endswith('.pdf') or ".pdf?" in url.lower()
        
        if vid_title == "No Title Found":
            vid_title = f"File {count}"

        ext = "pdf" if is_pdf else "mp4"
        file_type = "Document" if is_pdf else "Video"
        filename = f"File_{count}.{ext}"
        
        status_msg = await bot.send_message(
            chat_id,
            f"⬇️ **Downloading {file_type} {count} / {total}**\n\n📌 **Title:** `{vid_title}`\n📺 **Quality:** {quality_text} (if video)"
        )

        try:
            cookies_cmd = f'--cookies {COOKIES_FILE} ' if os.path.exists(COOKIES_FILE) else ''
            
            if quality == "best":
                format_str = '-f "bestvideo+bestaudio/best" '
            else:
                format_str = f'-f "bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best" '
                
            merge_cmd = "" if is_pdf else "--merge-output-format mp4 "

            cmd = (
                f'yt-dlp '
                f'{format_str}'
                f'{merge_cmd}'
                f'{cookies_cmd}'
                f'--retries 10 '
                f'-o "{filename}" '
                f'"{url}"'
            )

            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()

            if os.path.exists(filename):
                await status_msg.edit("⬆️ **Uploading to Telegram...**")
                
                final_caption = (
                    f"📁 **Batch Name :** {data['batch_name']}\n\n"
                    f"📝 **Topic Name :** {data['topic_name']}\n"
                    f"🎬 **File Title :** {vid_title}\n"
                    f"**[{{🎥}}] File ID :** {count:02d}\n\n"
                    f"👤 **Extract By :** {data['extract_by']}"
                )

                if is_pdf:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=filename,
                        caption=final_caption,
                        thumb=THUMBNAIL if os.path.exists(THUMBNAIL) else None
                    )
                else:
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
                await status_msg.edit(f"❌ **Failed to download {file_type} {count}**")

        except Exception as e:
            failed += 1
            await bot.send_message(chat_id, f"❌ **Error On {file_type} {count}**\n\n`{str(e)}`")

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

