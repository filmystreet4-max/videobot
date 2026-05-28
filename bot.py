import os
import re
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

# ================= CONFIG =================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

BATCH_NAME = "Kalam Parivar"
CREATOR_NAME = "Shoiab"

THUMBNAIL = "thumb.jpg"
COOKIES_FILE = "cookies.txt"

RETRY_COUNT = 3

STOP_DOWNLOAD = False

# ================= BOT =================

bot = Client(
    "AdvancedLeechBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= START =================

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):

    txt = f"""
🔥 ADVANCED TXT LEECH BOT

📚 Batch : {BATCH_NAME}
👤 Creator : {CREATOR_NAME}

COMMANDS:

/txt → Upload TXT
/cookies → Upload Cookies
/stop → Stop Batch

TXT FORMAT:

720|https://example.com/video
480|https://example.com/video
360|https://example.com/video

PDF links bhi support hain.
"""

    await message.reply_text(txt)

# ================= STOP =================

@bot.on_message(filters.command("stop"))
async def stop_handler(client, message: Message):

    global STOP_DOWNLOAD

    STOP_DOWNLOAD = True

    await message.reply_text(
        "🛑 Batch Stopped"
    )

# ================= COOKIES =================

@bot.on_message(filters.command("cookies"))
async def cookies_handler(client, message: Message):

    await message.reply_text(
        "📂 Cookies TXT bhejo"
    )

    cookie_msg = await bot.listen(
        message.chat.id
    )

    if not cookie_msg.document:

        return await message.reply_text(
            "❌ Invalid File"
        )

    await cookie_msg.download(
        file_name=COOKIES_FILE
    )

    await message.reply_text(
        "✅ Cookies Saved Successfully"
    )

# ================= TXT COMMAND =================

@bot.on_message(filters.command("txt"))
async def txt_command(client, message: Message):

    await message.reply_text(
        "📂 TXT file bhejo"
    )

# ================= TXT HANDLER =================

@bot.on_message(filters.document)
async def txt_handler(client, message: Message):

    global STOP_DOWNLOAD

    document = message.document

    if not document.file_name.endswith(".txt"):

        return await message.reply_text(
            "❌ Sirf TXT file bhejo"
        )

    txt_path = await message.download()

    await message.reply_text(
        "📥 TXT Received\n⚡ Processing..."
    )

    with open(txt_path, "r", encoding="utf-8") as f:

        content = f.read()

    lines = content.splitlines()

    urls = []

    for line in lines:

        line = line.strip()

        if "|" in line:

            quality, url = line.split("|", 1)

            urls.append(
                (
                    quality.strip(),
                    url.strip()
                )
            )

    if not urls:

        return await message.reply_text(
            "❌ No links found"
        )

    total = len(urls)

    success = 0
    failed = 0

    count = 1

    for quality, url in urls:

        try:

            # ================= STOP =================

            if STOP_DOWNLOAD:

                STOP_DOWNLOAD = False

                return await message.reply_text(
                    "🛑 Download Stopped"
                )

            clean_name = f"{count:03d}"

            # ================= PDF =================

            if ".pdf" in url.lower():

                filename = f"PDF_{clean_name}.pdf"

                status = await message.reply_text(
                    f"📄 Downloading PDF {count}/{total}"
                )

                cmd = (
                    f'yt-dlp '
                    f'--cookies {COOKIES_FILE} '
                    f'--retries 20 '
                    f'-o "{filename}" '
                    f'"{url}"'
                )

                process = await asyncio.create_subprocess_shell(
                    cmd
                )

                await process.communicate()

                if os.path.exists(filename):

                    caption = f"""
📚 Batch : {BATCH_NAME}

📄 PDF : {count}

👤 Creator : {CREATOR_NAME}
"""

                    uploaded = False

                    for attempt in range(RETRY_COUNT):

                        try:

                            await bot.send_document(
                                chat_id=message.chat.id,
                                document=filename,
                                caption=caption,
                                thumb=THUMBNAIL
                            )

                            uploaded = True
                            success += 1

                            break

                        except Exception as e:

                            print(
                                f"Retry Failed : {e}"
                            )

                            await asyncio.sleep(5)

                    if not uploaded:

                        failed += 1

                        await message.reply_text(
                            f"❌ PDF Upload Failed : {count}"
                        )

                    os.remove(filename)

                else:

                    failed += 1

                    await message.reply_text(
                        f"❌ PDF Download Failed : {count}"
                    )

                await status.delete()

            # ================= VIDEO =================

            else:

                filename = f"Video_{clean_name}.mp4"

                status = await message.reply_text(
                    f"🎬 Downloading Video {count}/{total}\n📺 Quality : {quality}p"
                )

                cmd = (
                    f'yt-dlp '
                    f'-f "bestvideo[height<={quality}]+bestaudio/best[height<={quality}]" '
                    f'--merge-output-format mp4 '
                    f'--cookies {COOKIES_FILE} '
                    f'--retries 20 '
                    f'-o "{filename}" '
                    f'"{url}"'
                )

                process = await asyncio.create_subprocess_shell(
                    cmd
                )

                await process.communicate()

                if os.path.exists(filename):

                    size = os.path.getsize(filename)

                    # ================= SIZE LIMIT =================

                    if size > 2 * 1024 * 1024 * 1024:

                        failed += 1

                        await message.reply_text(
                            f"❌ File Too Large : {count}"
                        )

                        os.remove(filename)

                    else:

                        caption = f"""
📚 Batch : {BATCH_NAME}

🎬 Video : {count}

📺 Quality : {quality}p

👤 Creator : {CREATOR_NAME}
"""

                        uploaded = False

                        for attempt in range(RETRY_COUNT):

                            try:

                                await bot.send_video(
                                    chat_id=message.chat.id,
                                    video=filename,
                                    caption=caption,
                                    thumb=THUMBNAIL,
                                    supports_streaming=True
                                )

                                uploaded = True
                                success += 1

                                break

                            except Exception as e:

                                print(
                                    f"Retry Failed : {e}"
                                )

                                await asyncio.sleep(5)

                        if not uploaded:

                            failed += 1

                            await message.reply_text(
                                f"❌ Video Upload Failed : {count}"
                            )

                        os.remove(filename)

                else:

                    failed += 1

                    await message.reply_text(
                        f"❌ Video Download Failed : {count}"
                    )

                await status.delete()

            count += 1

        except Exception as e:

            failed += 1

            await message.reply_text(
                f"❌ Error : {str(e)}"
            )

    os.remove(txt_path)

    # ================= FINAL REPORT =================

    await message.reply_text(
        f"""
✅ Batch Completed

📥 Successful : {success}
❌ Failed : {failed}
📦 Total : {total}
"""
    )

# ================= RUN =================

print("🚀 Advanced Bot Started")

bot.run()
