import os
import re
import time
import math
import shutil
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
OWNER_NAME = "GURUJI"
CHANNEL_ID = -1002160747497  # ⚠️ Aapki genuine channel id
CHANNEL_USERNAME = "LION 🦁" 
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
REVERSE_ORDER = False 
ENGINE_BUSY = False  # Anti-Overload Queue System

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
    "JonuKingAIEngineV3",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

USER_DATA = {}
STOP_DOWNLOAD = {}

# =========================
# PREMIUM ADVANCED TOOLS
# =========================
def clean_workspace():
    """🧹 Auto-Cleanup System: Clears all junk/leftover files"""
    try:
        cleaned = 0
        for file in os.listdir("."):
            if file.startswith("JonuKing_") or file.endswith(".part") or file.endswith(".ytdl"):
                os.remove(file)
                cleaned += 1
        if cleaned > 0:
            print(f"🧹 Auto-Cleanup: Removed {cleaned} junk files safely.")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def check_cookies_health():
    """🍪 Auto-Detect Cookies Expiry System"""
    if not os.path.exists(COOKIES_FILE):
        return "❌ Not Found (Upload using /cookies)"
    try:
        now = time.time()
        expired_count = 0
        total_count = 0
        with open(COOKIES_FILE, "r", errors="ignore") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split("\t")
                if len(parts) >= 5:
                    total_count += 1
                    expiry = int(parts[4])
                    if expiry < now:
                        expired_count += 1
        if total_count == 0:
            return "⚠️ Invalid Format (Re-download file)"
        if expired_count == total_count:
            return "❌ Expired! (Need Fresh Cookies)"
        if expired_count > 0:
            return f"⚠️ Warning! ({total_count - expired_count} active sessions left)"
        return "✅ 100% Fresh & Active"
    except:
        return "⚠️ Unreadable Format"

def get_free_disk_space():
    """📊 Real-time Storage Monitor"""
    try:
        total, used, free = shutil.disk_usage(".")
        return f"{free / (1024**3):.2f} GB Khaali"
    except:
        return "Unknown"

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
    cookie_status = check_cookies_health()
    disk_space = get_free_disk_space()
    
    await message.reply_text(
        f"👑 **JonuKing Ultimate AI Engine v3**\n\n"
        f"🤖 **AI Status:** `Active (Gemini 2.5)`\n"
        f"🍪 **Cookies Health:** `{cookie_status}`\n"
        f"📊 **Server Disk:** `{disk_space}`\n"
        f"📑 **Sequence Order:** `{seq_state}`\n\n"
        "**Master Commands:**\n"
        "/txt - Process Batch (Video/PDF)\n"
        "/thumb - Send any photo to set Video Cover\n"
        "/reverse - Reverse link processing order\n"
        "/cookies - Sync cookies.txt\n"
        "/reset_history - Wipe out skip memory\n"
        "/stop - Emergency Kill"
        f"{SIGNATURE}"
    )

@bot.on_message(filters.command("reverse"))
async def reverse_command(client, message: Message):
    global REVERSE_ORDER
    REVERSE_ORDER = not REVERSE_ORDER
    state = "Niche se Upar ⬆️" if REVERSE_ORDER else "Upar se Niche ⬇️"
    await message.reply_text(f"🔄 **Order Changed!**\nAb batch `{state}` padha jayega.")

@bot.on_message(filters.photo & filters.private)
async def save_thumbnail(client, message: Message):
    await message.download(file_name=THUMBNAIL)
    await message.reply_text("✅ **Custom Thumbnail Saved!** 🖼️")

@bot.on_message(filters.command("stop"))
async def stop_command(client, message: Message):
    STOP_DOWNLOAD[message.chat.id] = True
    await message.reply_text("🛑 **Emergency stop initiated by Master!**")

@bot.on_message(filters.command("reset_history"))
async def reset_history_command(client, message: Message):
    UPLOADED_HISTORY.clear()
    await message.reply_text("🔄 **Upload memory wiped out successfully!**")

@bot.on_message(filters.command("cookies"))
async def cookies_command(client, message: Message):
    ask = await message.reply_text("📂 **Send fresh `cookies.txt` file:**")
    msg = await bot.listen(message.chat.id)
    if msg.document: 
        await msg.download(file_name=COOKIES_FILE)
        health = check_cookies_health()
        await ask.edit(f"✅ **Cookies Synced!**\n📊 **Status:** `{health}`")

# =========================
# TXT COMMAND (WITH QUEUE LOCK)
# =========================
@bot.on_message(filters.command("txt"))
async def txt_command(client, message: Message):
    global ENGINE_BUSY
    chat_id = message.chat.id
    
    # Smart Queue Check
    if ENGINE_BUSY:
        return await message.reply_text("⚠️ **Engine Busy!**\nPehle se ek batch chal raha hai, kripya uske khatam hone ka intezar karein.")

    clean_workspace() # Auto-clean junk before starting
    
    ask = await message.reply_text("📂 **Send TXT/HTML Batch File:**")
    txt_msg = await bot.listen(chat_id)
    
    if not txt_msg.document: return await ask.edit("❌ **Invalid File Format!**")
    await ask.edit("🤖 **AI is parsing your batch file...**")
    
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

    if REVERSE_ORDER:
        links.reverse()

    USER_DATA[chat_id] = {"links": links, "batch_name": batch_name, "topic_name": topic_name}

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 480p", callback_data="480"), InlineKeyboardButton("💎 720p", callback_data="720")],
        [InlineKeyboardButton("🔥 Best Quality", callback_data="best")]
    ])
    
    seq_state = "⬆️ Bottom to Top" if REVERSE_ORDER else "⬇️ Top to Bottom"
    await ask.edit(
        f"✨ **AI Extraction Complete!**\n\n"
        f"📦 **Batch Name:** `{batch_name}`\n"
        f"📚 **Topic Name:** `{topic_name}`\n"
        f"📑 **Sequence:** `{seq_state}`\n"
        f"🔗 **Total Links:** `{len(links)}`\n\n"
        f"📺 **Select Video Quality:**", reply_markup=buttons
    )

# =========================
# CORE PROCESSING ENGINE
# =========================
@bot.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    global ENGINE_BUSY
    chat_id = callback_query.message.chat.id
    
    if callback_query.data == "stop_current_batch":
        STOP_DOWNLOAD[chat_id] = True
        ENGINE_BUSY = False
        clean_workspace()
        return await callback_query.answer("🛑 Processing Stopped!", show_alert=True)

    quality = callback_query.data
    data = USER_DATA.get(chat_id)
    STOP_DOWNLOAD[chat_id] = False
    ENGINE_BUSY = True # Lock Engine
    
    await callback_query.message.edit_text(f"🚀 **{OWNER_NAME} Engine Active. Spawning workers...**")
    
    links = data["links"]
    total = len(links)
    success, skipped = 0, 0

    for count, (vid_title, url) in enumerate(links, start=1):
        if STOP_DOWNLOAD.get(chat_id): break
        
        # 🧹 JUNK CLEANER: URL ke aage-peeche se extra quotes, brackets aur spaces saaf karega
        url = url.strip(' "\'<>():')
        vid_title = vid_title.strip() if vid_title else f"File {count}"
        
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
            clean_workspace() # Auto-clean on single item crash

    ENGINE_BUSY = False # Unlock Engine
    clean_workspace() # Final batch cleanup
    await bot.send_message(chat_id, f"✅ **Batch Processing Finished!**\n📊 Success: `{success}` | Skipped: `{skipped}`\n{SIGNATURE}")

if __name__ == "__main__":
    clean_workspace() # Core startup cleanup
    bot.run()
