import os
import re
import asyncio
from pyromod import Client
from pyrogram import filters (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

# =========================
# VARIABLES
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

THUMBNAIL = "thumb.jpg"
COOKIES_FILE = "cookies.txt"

# =========================
# BOT START
# =========================

bot = Client(
    "VideoBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# STORAGE
# =========================

TXT_FILES = {}
STOP_DOWNLOAD = {}
USER_QUALITY = {}

# =========================
# START COMMAND
# =========================

@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):

    await message.reply_text(
        """
🔥 Advanced TXT Leech Bot

Commands:

/txt = Upload TXT
/cookies = Upload Cookies
/stop = Stop Batch
"""
    )

# =========================
# STOP COMMAND
# =========================

@bot.on_message(filters.command("stop"))
async def stop_command(client, message: Message):

    STOP_DOWNLOAD[message.chat.id] = True

    await message.reply_text(
        "🛑 Download Stopped"
    )

# =========================
# COOKIES COMMAND
# =========================

@bot.on_message(filters.command("cookies"))
async def cookies_command(client, message: Message):

    ask = await message.reply_text(
        "📂 Cookies TXT bhejo"
    )

    cookie_msg: Message = await bot.listen(
        message.chat.id
    )

    if not cookie_msg.document:

        return await ask.edit(
            "❌ TXT file bhejo"
        )

    await cookie_msg.download(
        file_name=COOKIES_FILE
    )

    await ask.edit(
        "✅ Cookies Saved"
    )

# =========================
# TXT COMMAND
# =========================

@bot.on_message(filters.command("txt"))
async def txt_command(client, message: Message):

    ask = await message.reply_text(
        "📂 TXT file bhejo"
    )

    txt_msg: Message = await bot.listen(
        message.chat.id
    )

    if not txt_msg.document:

        return await ask.edit(
            "❌ TXT file bhejo"
        )

    txt_path = await txt_msg.download()

    TXT_FILES[message.chat.id] = txt_path

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "144p",
                    callback_data="144"
                ),
                InlineKeyboardButton(
                    "240p",
                    callback_data="240"
                )
            ],
            [
                InlineKeyboardButton(
                    "360p",
                    callback_data="360"
                ),
                InlineKeyboardButton(
                    "480p",
                    callback_data="480"
                )
            ],
            [
                InlineKeyboardButton(
                    "720p",
                    callback_data="720"
                ),
                InlineKeyboardButton(
                    "1080p",
                    callback_data="1080"
                )
            ]
        ]
    )

    await ask.edit(
        "📺 Quality Select Karo",
        reply_markup=buttons
    )

# =========================
# QUALITY CALLBACK
# =========================

@bot.on_callback_query()
async def callback_handler(
    client,
    callback_query: CallbackQuery
):

    quality = callback_query.data

    chat_id = callback_query.message.chat.id

    USER_QUALITY[chat_id] = quality

    STOP_DOWNLOAD[chat_id] = False

    await callback_query.message.edit_text(
        f"✅ Selected Quality : {quality}p"
    )

    txt_path = TXT_FILES.get(chat_id)

    if not txt_path:

        return await bot.send_message(
            chat_id,
            "❌ TXT not found"
        )

    with open(
        txt_path,
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()

    urls = re.findall(
        r'https?://\S+',
        content
    )

    if not urls:

        return await bot.send_message(
            chat_id,
            "❌ No links found"
        )

    total = len(urls)

    success = 0
    failed = 0
    count = 1

    for url in urls:

        if STOP_DOWNLOAD.get(chat_id):

            await bot.send_message(
                chat_id,
                "🛑 Batch Stopped"
            )

            break

        try:

            filename = f"Video_{count}.mp4"

            status = await bot.send_message(
                chat_id,
                f"""
⬇️ Downloading Video {count}

📺 Quality : {quality}p
"""
            )

            cmd = (
                f'yt-dlp '
                f'-f "bestvideo[height<={quality}]+bestaudio/best[height<={quality}]" '
                f'--merge-output-format mp4 '
                f'--cookies {COOKIES_FILE} '
                f'--retries 10 '
                f'-o "{filename}" '
                f'"{url}"'
            )

            process = await asyncio.create_subprocess_shell(
                cmd
            )

            await process.communicate()

            if os.path.exists(filename):

                await bot.send_video(
                    chat_id=chat_id,
                    video=filename,
                    caption=f"""
🎬 Video {count}

📺 Quality : {quality}p
""",
                    thumb=THUMBNAIL,
                    supports_streaming=True
                )

                os.remove(filename)

                success += 1

                await status.delete()

            else:

                failed += 1

                await status.edit(
                    f"❌ Failed Video {count}"
                )

        except Exception as e:

            failed += 1

            await bot.send_message(
                chat_id,
                f"""
❌ Error On Video {count}

{str(e)}
"""
            )

        count += 1

    await bot.send_message(
        chat_id,
        f"""
✅ Batch Completed

📦 Total : {total}

✅ Success : {success}

❌ Failed : {failed}
"""
    )

# =========================
# RUN BOT
# =========================

print("🚀 Bot Started")

bot.run()
