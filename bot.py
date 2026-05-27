import os
import re
import asyncio
import subprocess
from aiohttp import web

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from pyromod import listen

# =========================
# VARIABLES
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

PORT = int(os.getenv("PORT", 8080))
WEBHOOK = os.getenv("WEBHOOK", "False")

COOKIES_FILE = "cookies.txt"

# =========================
# BOT CLIENT
# =========================

bot = Client(
    "AdvancedLeechBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# WEB SERVER
# =========================

routes = web.RouteTableDef()

@routes.get("/")
async def root(request):

    return web.Response(
        text="🔥 Bot Running Successfully"
    )

async def web_server():

    app = web.Application(
        client_max_size=30000000
    )

    app.add_routes(routes)

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT
    )

    await site.start()

# =========================
# START COMMAND
# =========================

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):

    txt = """
🔥 Advanced Leech Bot Ready

✅ TXT Support
✅ MP4 Support
✅ PDF Support
✅ Cookies Support
✅ Railway Hosting
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⚡ Advanced Bot ⚡",
                    url="https://t.me/example"
                )
            ]
        ]
    )

    await message.reply_text(
        txt,
        reply_markup=buttons
    )

# =========================
# COOKIES COMMAND
# =========================

@bot.on_message(filters.command("cookies"))
async def cookies_handler(client, message: Message):

    ask = await message.reply_text(
        "📂 Send Cookies TXT File"
    )

    cookie_msg: Message = await bot.listen(
        message.chat.id
    )

    if not cookie_msg.document:

        return await ask.edit(
            "❌ Invalid File"
        )

    if not cookie_msg.document.file_name.endswith(".txt"):

        return await ask.edit(
            "❌ Send TXT File Only"
        )

    await cookie_msg.download(
        file_name=COOKIES_FILE
    )

    await ask.edit(
        "✅ Cookies Saved Successfully"
    )

# =========================
# UPLOAD COMMAND
# =========================

@bot.on_message(filters.command("upload"))
async def upload_handler(client, message: Message):

    editable = await message.reply_text(
        "📂 Send TXT File"
    )

    input_msg: Message = await bot.listen(
        message.chat.id
    )

    if not input_msg.document:

        return await editable.edit(
            "❌ TXT File Required"
        )

    if not input_msg.document.file_name.endswith(".txt"):

        return await editable.edit(
            "❌ Send TXT File Only"
        )

    txt_path = await input_msg.download()

    # =========================
    # READ LINKS
    # =========================

    try:

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

        os.remove(txt_path)

    except Exception as e:

        return await editable.edit(
            f"❌ TXT Read Error\n{str(e)}"
        )

    if not urls:

        return await editable.edit(
            "❌ No Links Found"
        )

    total = len(urls)

    await editable.edit(
        f"✅ {total} Links Found"
    )

    # =========================
    # LOOP LINKS
    # =========================

    for index, url in enumerate(urls, start=1):

        try:

            await message.reply_text(
                f"⬇️ Downloading {index}/{total}"
            )

            # =========================
            # PDF DOWNLOAD
            # =========================

            if ".pdf" in url.lower():

                pdf_name = f"PDF_{index}.pdf"

                pdf_cmd = (
                    f'curl -L "{url}" '
                    f'-o "{pdf_name}"'
                )

                process = await asyncio.create_subprocess_shell(
                    pdf_cmd
                )

                await process.communicate()

                if os.path.exists(pdf_name):

                    await message.reply_document(
                        document=pdf_name,
                        caption=f"📄 PDF {index}"
                    )

                    os.remove(pdf_name)

                else:

                    await message.reply_text(
                        f"❌ PDF Failed {index}"
                    )

            # =========================
            # VIDEO DOWNLOAD
            # =========================

            else:

                video_name = f"Video_{index}.mp4"

                cmd = (
                    f'yt-dlp '
                    f'--cookies cookies.txt '
                    f'--retries 20 '
                    f'-f mp4 '
                    f'-o "{video_name}" '
                    f'"{url}"'
                )

                process = await asyncio.create_subprocess_shell(
                    cmd
                )

                await process.communicate()

                if os.path.exists(video_name):

                    size = os.path.getsize(video_name)

                    # 49MB Limit
                    if size > 49 * 1024 * 1024:

                        await message.reply_text(
                            f"⚠️ File Too Large\n{video_name}"
                        )

                        os.remove(video_name)

                    else:

                        await message.reply_video(
                            video=video_name,
                            caption=f"🎬 Video {index}"
                        )

                        os.remove(video_name)

                else:

                    await message.reply_text(
                        f"❌ Video Failed {index}"
                    )

        except Exception as e:

            await message.reply_text(
                f"❌ Error On Link {index}\n\n{str(e)}"
            )

    await message.reply_text(
        "✅ All Downloads Completed"
    )

# =========================
# MAIN FUNCTION
# =========================

async def main():

    print("🚀 Bot Started")

    await web_server()

    await bot.start()

    print("✅ Bot Running")

    await asyncio.Event().wait()

# =========================
# RUN
# =========================

if __name__ == "__main__":

    asyncio.run(main())
