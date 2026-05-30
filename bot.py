import os
import re
import time
import math
import asyncio
import subprocess

from google import genai
from pyromod import Client
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

# =========================
# JONUKING BRANDING
# =========================
OWNER_NAME = "Jonu👑King"
CHANNEL_ID = -1002160747497  # ⚠️ YAHAN APNI ASLI CHANNEL ID DAALEIN
CHANNEL_USERNAME = "lion 🦁" 
SIGNATURE = f"\n\n⚡ *Powered by | {CHANNEL_USERNAME} x {OWNER_NAME}*"

# =========================
# VARIABLES & API KEYS
# =========================
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

THUMBNAIL = "thumb.jpg"
COOKIES_FILE = "cookies.txt"

UPLOADED_HISTORY = set()
REVERSE_ORDER = False # Sequence control variable

# =========================
# SETUP AI (GEMINI)
# =========================
AI_ENABLED = False
if GEMINI_KEY:
    try:
        ai_client = genai.Client(api_key=GEMINI_KEY)
        AI_ENABLED = True
    except Exception as e:
        print(f"⚠️ AI Setup Failed: {e}")

# =========================
# BOT START & STORAGE
# =========================
bot = Client(
    "JonuKingAIEngineFinal",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

USER_DATA = {}
STOP_DOWNLOAD = {}

# =========================
# PROGRESS BAR
# =========================
async def progress_bar(current, total, reply_msg, start_time, file_type):
    now = time.time()
    diff = now - start_time
    if round(diff % 4.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        eta = round((total - current) / speed) if speed > 0 else 0
        
        progress = "".join(["🔥" if i < round(percentage / 10) else "⚪" for i in range(10)])
        
        tmp = (
            f"👑 **JonuKing AI Processing...**\n\n"
            f"📥 **Uploading:** `{file_type}`\n"
            f"🌀 **Status:** `[{progress}]` {round(percentage, 2)}%\n"
            f"⚡ **Speed:** `{round(speed/1024/1024, 2)} MB/s`\n"
            f"⏱️ **ETA:** `{time.strftime('%M:%S', time.gmtime(eta))}`"
            f"{SIGNATURE}"
        )
        try:
            await reply_msg.edit_text(tmp, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Terminate Batch", callback_data="stop_current_batch")]]))
        except: pass

# =========================
# AI HELPER
# =========================
def extract_info_via_ai(text_content):
    if not AI_ENABLED:
        return "Unknown Batch", "Unknown Topic"
    try:
        prompt = f"Analyze this text and extract Course/Batch Name and Topic. Format: 'Batch: <name> | Topic: <name>'. Text: {text_content[:1000]}"
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        res = response.text
        batch = re.search(r'Batch:\s*(.*?)\s*\|', res).group(1).strip()
        topic = re.search(r'Topic:\s*(.*)', res).group(1).strip()
        return batch, topic
    except:
        return "Auto-Batch", "Auto-Topic"

def generate_caption_via_ai(title, batch, topic, f_type):
    if not AI_ENABLED:
        return f"🎬 **Title:** `{title}`"
    try:
        prompt = f"Write a 2-line attractive Telegram caption with emojis for a {f_type} titled '{title}' from the course '{batch} - {topic}'. No hashtags."
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except:
        return f"🎬 **Title:** `{title}`"

# =========================
# COMMANDS
# =========================
@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):
    seq_state = "Niche se Upar ⬆️" if REVERSE_ORDER else "Upar se Niche ⬇️"
    await message.reply_text(
        f"👑 **Welcome to {OWNER_NAME}'s Master Engine!**\n\n"
        f"🤖 **AI Status:** `Active`\n"
        f"🔄 **Skip System:** `Enabled`\n"
        f"📑 **Current Order:** `{seq_state}`\n\n"
        "**Commands:**\n/txt - Process Batch\n/thumb - Send a Photo to Set Thumbnail\n/reverse - Change Download Order\n/cookies - Sync Cookies\n/reset_history - Clear Memory"
        f"{SIGNATURE}"
    )

@bot.on_message(filters.command("reverse"))
async def reverse_command(client, message: Message):
    global REVERSE_ORDER
    REVERSE_ORDER = not REVERSE_ORDER
    state = "Niche se Upar (Bottom to Top) ⬆️" if REVERSE_ORDER else "Upar se Niche (Top to Bottom) ⬇️"
    await message.reply_text(f"🔄 **Sequence Changed!**\n\nAb bot aapki aane wali TXT file ko **{state}** order mein padhega.")

@bot.on_message(filters.photo & filters.private)
async def save_thumbnail(client, message: Message):
    await message.download(file_name=THUMBNAIL)
    await message.reply_text("✅ **Custom Thumbnail Saved!**\n\nAb aage se har video par yehi cover photo lagegi. 🖼️")

@bot.on_message(filters.command("stop"))
async def stop_command(client, message: Message):
    STOP_DOWNLOAD[message.chat.id] = True
    await message.reply_text("🛑 **Terminating batch!**")

@bot.on_message(filters.command("reset_history"))
async def reset_history_command(client, message: Message):
    UPLOADED_HISTORY.clear()
    await message.reply_text("🔄 **Memory cleared! Sari files shuru se download hongi.**")

@bot.on_message(filters.command("cookies"))
async def cookies_command(client, message: Message):
    ask = await message.reply_text("📂 **Send `cookies.txt`:**")
    msg = await bot.listen(message.chat.id)
    if msg.document: 
        await msg.download(file_name=COOKIES_FILE)
        await ask.edit("✅ **Cookies Synced!**")

# =========================
# TXT COMMAND
# =========================
@bot.on_message(filters.command("txt"))
async def txt_command(client, message: Message):
    chat_id = message.chat.id
    ask = await message.reply_text("📂 **Send TXT/HTML File:**")
    txt_msg = await bot.listen(chat_id)
    
    if not txt_msg.document: return await ask.edit("❌ **Invalid File!**")
    await ask.edit("🤖 **AI is analyzing...**")
    
    txt_path = await txt_msg.download()
    with open(txt_path, "r", encoding="utf-8") as f: content = f.read()

    batch_name, topic_name = extract_info_via_ai(content)
    
    links = []
    html_matches = re.findall(r'href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', content, re.IGNORECASE)
    if html_matches:
        links = [(re.sub(r'<[^>]+>', '', t).strip(), u) for u, t in html_matches]
    else:
        for line in content.splitlines():
            match = re.search(r'(.*?)(https?://\S+)', line.strip())
            if match:
                links.append((match.group(1).strip(' :|-'), match.group(2)))

    # Apply Sequence Reversal if Enabled
    if REVERSE_ORDER:
        links.reverse()

    USER_DATA[chat_id] = {"links": links, "batch_name": batch_name, "topic_name": topic_name}

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 480p", callback_data="480"), InlineKeyboardButton("💎 720p", callback_data="720")],
        [InlineKeyboardButton("🔥 Best Quality", callback_data="best")]
    ])
    
    seq_state = "⬆️ Bottom to Top" if REVERSE_ORDER else "⬇️ Top to Bottom"
    await ask.edit(
        f"✨ **Extraction Complete!**\n\n"
        f"📦 **Batch:** `{batch_name}`\n"
        f"📚 **Topic:** `{topic_name}`\n"
        f"📑 **Order:** `{seq_state}`\n"
        f"🔗 **Total Files Found:** `{len(links)}`\n\n"
        f"📺 **Choose Quality:**", reply_markup=buttons
    )

# =========================
# CORE ENGINE
# =========================
@bot.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    if callback_query.data == "stop_current_batch":
        STOP_DOWNLOAD[chat_id] = True
        return await callback_query.answer("🛑 Stopped!", show_alert=True)

    quality = callback_query.data
    data = USER_DATA.get(chat_id)
    STOP_DOWNLOAD[chat_id] = False
    
    await callback_query.message.edit_text(f"🚀 **{OWNER_NAME} Engine Initiated...**")
    
    links = data["links"]
    total = len(links)
    success = 0
    skipped = 0

    for count, (vid_title, url) in enumerate(links, start=1):
        if STOP_DOWNLOAD.get(chat_id): break
        
        vid_title = vid_title if vid_title else f"File {count}"
        
        if url in UPLOADED_HISTORY:
            skipped += 1
            continue

        is_pdf = url.lower().endswith('.pdf') or ".pdf?" in url.lower()
        ext = "pdf" if is_pdf else "mp4"
        filename = f"JonuKing_{count}.{ext}"
        f_type = "Document" if is_pdf else "Video"
        
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Stop", callback_data="stop_current_batch")]])
        status_msg = await bot.send_message(chat_id, f"📥 **Downloading [{count}/{total}]**\n📌 `{vid_title}`\n{SIGNATURE}", reply_markup=btn)
        
        try:
            cookies_cmd = f'--cookies {COOKIES_FILE} ' if os.path.exists(COOKIES_FILE) else ''
            res_cmd = "" if quality == "best" else f'-S "res:{quality}" '
            merge_cmd = "" if is_pdf else "--merge-output-format mp4 "

            cmd = f'yt-dlp {res_cmd}{merge_cmd}{cookies_cmd}--retries 10 -o "{filename}" "{url}"'
            
            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()

            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / (1024 * 1024)
                ai_caption = generate_caption_via_ai(vid_title, data['batch_name'], data['topic_name'], f_type)

                caption = (
                    f"{ai_caption}\n\n"
                    f"📦 **Batch:** `{data['batch_name']}`\n"
                    f"💾 **Size:** `{file_size:.2f} MB`\n"
                    f"{SIGNATURE}"
                )

                # Thumbnail logic added here
                thumb_path = THUMBNAIL if os.path.exists(THUMBNAIL) else None

                upload_start = time.time()
                if is_pdf:
                    await bot.send_document(CHANNEL_ID, document=filename, caption=caption, progress=progress_bar, progress_args=(status_msg, upload_start, "Document"))
                else:
                    await bot.send_video(CHANNEL_ID, video=filename, caption=caption, thumb=thumb_path, supports_streaming=True, progress=progress_bar, progress_args=(status_msg, upload_start, "Video"))
                
                os.remove(filename)
                UPLOADED_HISTORY.add(url)
                success += 1
                await status_msg.delete()
            else:
                await status_msg.edit_text(f"❌ **Failed:** `{vid_title}`")
        except Exception as e:
            await bot.send_message(chat_id, f"❌ **Error:**\n`{str(e)}`")

    await bot.send_message(chat_id, f"✅ **Batch Completed!**\n📊 Success: `{success}` | Skipped: `{skipped}`\n{SIGNATURE}")

if __name__ == "__main__":
    bot.run()
        
