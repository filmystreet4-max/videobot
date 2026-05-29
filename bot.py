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
CHANNEL_ID = -1002160747497  # ⚠️ Aapki asli channel id set kar di hai!
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

# History to prevent re-downloading (Resume Feature)
UPLOADED_HISTORY = set()

# =========================
# SETUP AI (GEMINI)
# =========================
AI_ENABLED = False
if GEMINI_KEY:
    try:
        ai_client = genai.Client(api_key=GEMINI_KEY)
        AI_ENABLED = True
        print("🤖 AI Module Successfully Activated!")
    except Exception as e:
        print(f"⚠️ AI Setup Failed: {e}")

# =========================
# BOT START & STORAGE
# =========================
bot = Client(
    "JonuKingAIEngineV2",
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
# AI HELPER FUNCTIONS
# =========================
def extract_info_via_ai(text_content):
    if not AI_ENABLED:
        return "Unknown Batch", "Unknown Topic"
    try:
        prompt = f"Analyze this text and extract the Course/Batch Name and the Main Topic. Reply exactly in this format: 'Batch: <name> | Topic: <name>'. Keep it short. Text snippet: {text_content[:1000]}"
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        result = response.text
        
        batch = re.search(r'Batch:\s*(.*?)\s*\|', result).group(1).strip()
        topic = re.search(r'Topic:\s*(.*)', result).group(1).strip()
        return batch, topic
    except:
        return "Auto-Batch", "Auto-Topic"

def generate_caption_via_ai(title, batch, topic, f_type):
    if not AI_ENABLED:
        return f"🎬 **Title:** `{title}`"
    try:
        prompt = f"Write a 2-line attractive Telegram caption with emojis for a {f_type} titled '{title}' from the course '{batch} - {topic}'. Do not use hashtags."
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except:
        return f"🎬 **Title:** `{title}`"

# =========================
# COMMANDS
# =========================
@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):
    ai_status = "✅ Active" if AI_ENABLED else "❌ Offline"
    await message.reply_text(
        f"👑 **Welcome to {OWNER_NAME}'s AI Engine V2!**\n\n"
        f"🤖 **AI Status:** `{ai_status}`\n"
        f"🔄 **Resume Engine:** `Enabled` (Auto-skips uploaded files)\n"
        f"📦 **Grouping System:** `Video + PDF Paired`\n\n"
        "**Commands:**\n/txt - Process Batch\n/cookies - Sync Cookies\n/stop - Kill Process\n/reset_history - Clear Skip Memory"
        f"{SIGNATURE}"
    )

@bot.on_message(filters.command("stop"))
async def stop_command(client, message: Message):
    STOP_DOWNLOAD[message.chat.id] = True
    await message.reply_text("🛑 **Terminating batch as per Master's order!**")

@bot.on_message(filters.command("reset_history"))
async def reset_history_command(client, message: Message):
    UPLOADED_HISTORY.clear()
    await message.reply_text("🔄 **Upload memory cleared! Next batch will download everything from scratch.**")

@bot.on_message(filters.command("cookies"))
async def cookies_command(client, message: Message):
    ask = await message.reply_text("📂 **JonuKing Needs `cookies.txt`:**")
    cookie_msg = await bot.listen(message.chat.id)
    if not cookie_msg.document: return await ask.edit("❌ **Invalid Source!**")
    await cookie_msg.download(file_name=COOKIES_FILE)
    await ask.edit("✅ **Cookies Synced Successfully!**")

# =========================
# AI TXT COMMAND
# =========================
@bot.on_message(filters.command("txt"))
async def txt_command(client, message: Message):
    chat_id = message.chat.id
    ask = await message.reply_text("📂 **Send TXT/HTML File (AI will auto-analyze & pair Video+PDF):**")
    txt_msg = await bot.listen(chat_id)
    
    if not txt_msg.document: 
        return await ask.edit("❌ **Invalid File!**")
    
    await ask.edit("🤖 **AI is analyzing your file and pairing content...**")
    txt_path = await txt_msg.download()
    
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    batch_name, topic_name = extract_info_via_ai(content)
    
    # Advanced Parsing for Pairing Video & PDFs
    links = []
    html_matches = re.findall(r'href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', content, re.IGNORECASE)
    if html_matches:
        links = [(re.sub(r'<[^>]+>', '', t).strip(), u) for u, t in html_matches]
    else:
        for line in content.splitlines():
            match = re.search(r'(.*?)(https?://\S+)', line.strip())
            if match:
                links.append((match.group(1).strip(' :|-'), match.group(2)))

    # Smart Grouping (Videos and PDFs mapping)
    paired_batch = []
    temp_video = None
    
    for title, url in links:
        is_pdf = url.lower().endswith('.pdf') or ".pdf?" in url.lower()
        if not is_pdf:
            if temp_video:
                paired_batch.append((temp_video, None)) # Video without PDF
            temp_video = (title, url)
        else:
            if temp_video:
                paired_batch.append((temp_video, (title, url))) # Paired Video + PDF
                temp_video = None
            else:
                paired_batch.append((None, (title, url))) # Isolated PDF
    if temp_video:
        paired_batch.append((temp_video, None))

    USER_DATA[chat_id] = {
        "paired_batch": paired_batch, 
        "batch_name": batch_name, 
        "topic_name": topic_name
    }

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 480p", callback_data="480"), InlineKeyboardButton("💎 720p", callback_data="720")],
        [InlineKeyboardButton("🔥 Best Quality", callback_data="best")]
    ])
    
    await ask.edit(
        f"✨ **AI Parsing & Grouping Complete!**\n\n"
        f"📦 **Detected Batch:** `{batch_name}`\n"
        f"📚 **Detected Topic:** `{topic_name}`\n"
        f"🔗 **Total Paired Items:** `{len(paired_batch)}`\n\n"
        f"📺 **Choose Output Quality:**", 
        reply_markup=buttons
    )

# =========================
# CORE ENGINE
# =========================
@bot.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    if callback_query.data == "stop_current_batch":
        STOP_DOWNLOAD[chat_id] = True
        return await callback_query.answer("🛑 Terminating as per Master's order!", show_alert=True)

    quality = callback_query.data
    data = USER_DATA.get(chat_id)
    if not data: return await callback_query.message.edit_text("❌ **Session Expired.**")

    STOP_DOWNLOAD[chat_id] = False
    await callback_query.message.edit_text(f"🚀 **{OWNER_NAME} V2 Engine Initiated...**")

    paired_batch = data["paired_batch"]
    
    async def process_single_file(title, url, is_pdf, index):
        if url in UPLOADED_HISTORY:
            return "SKIPPED" # Smart Skip Feature
            
        ext = "pdf" if is_pdf else "mp4"
        filename = f"JonuKing_{index}.{ext}"
        
        inline_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Terminate Batch", callback_data="stop_current_batch")]])
        status_msg = await bot.send_message(chat_id, f"📥 **Downloading...**\n📌 `{title}`\n{SIGNATURE}", reply_markup=inline_btn)
        
        try:
            cookies_cmd = f'--cookies {COOKIES_FILE} ' if os.path.exists(COOKIES_FILE) else ''
            format_str = '-f "bestvideo+bestaudio/best" ' if quality == "best" else f'-f "bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best" '
            merge_cmd = "" if is_pdf else "--merge-output-format mp4 "

            cmd = f'yt-dlp {format_str}{merge_cmd}{cookies_cmd}--retries 10 -o "{filename}" "{url}"'
            process = await asyncio.create_subprocess_shell(cmd)
            await process.communicate()

            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / (1024 * 1024)
                f_type = "Document" if is_pdf else "Video"
                ai_generated_text = generate_caption_via_ai(title, data['batch_name'], data['topic_name'], f_type)

                caption = (
                    f"{ai_generated_text}\n\n"
                    f"📦 **Batch:** `{data['batch_name']}`\n"
                    f"💾 **Size:** `{file_size:.2f} MB`\n"
                    f"{SIGNATURE}"
                )

                upload_start = time.time()
                if is_pdf:
                    await bot.send_document(CHANNEL_ID, document=filename, caption=caption, progress=progress_bar, progress_args=(status_msg, upload_start, "Document"))
                else:
                    await bot.send_video(CHANNEL_ID, video=filename, caption=caption, supports_streaming=True, progress=progress_bar, progress_args=(status_msg, upload_start, "Video"))
                
                os.remove(filename)
                UPLOADED_HISTORY.add(url) # Save to memory
                await status_msg.delete()
                return "SUCCESS"
            else:
                await status_msg.edit_text(f"❌ **Failed to download: {title}**")
                return "FAILED"
        except Exception as e:
            await bot.send_message(chat_id, f"❌ **Error on `{title}`:**\n`{str(e)}`")
            return "FAILED"

    # Loop through the paired elements
    for idx, (video_data, pdf_data) in enumerate(paired_batch, start=1):
        if STOP_DOWNLOAD.get(chat_id): break
        
        # 1. Process Video first if available
        if video_data:
            v_title, v_url = video_data
            await process_single_file(v_title, v_url, is_pdf=False, index=idx)
            
        # 2. Process PDF next immediately (mapping it right under the video)
        if pdf_data:
            p_title, p_url = pdf_data
            await process_single_file(p_title, p_url, is_pdf=True, index=idx)

    await bot.send_message(chat_id, f"✅ **JonuKing AI Batch Processing Finished!**\n{SIGNATURE}")

if __name__ == "__main__":
    bot.run()
    
