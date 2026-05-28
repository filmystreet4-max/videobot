import os
import re
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = Client(
    "VideoBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# START COMMAND
@bot.on_message(filters.command("start"))
async def start(client, message):

    await message.reply_text(
        "✅ Bot Running\n\nUse /txt command and send TXT file"
    )

# TXT COMMAND
@bot.on_message(filters.command("txt"))
async def txt_command(client, message):

    await message.reply_text(
        "📂 Ab TXT file bhejo"
    )

# TXT FILE HANDLER
@bot.on_message(filters.document)
async def txt_handler(client, message: Message):

    document = message.document

    if not document.file_name.endswith(".txt"):

        return await message.reply_text(
            "❌ Sirf TXT file bhejo"
        )

    txt_path = await message.download()

    await message.reply_text(
        "📥 TXT Received\n⏳ Processing..."
    )

    with open(txt_path, "r", encoding="utf-8") as f:

        content = f.read()

    urls = re.findall(r'https?://\S+', content)

    if not urls:

        return await message.reply_text(
            "❌ No links found"
        )

    count = 1

    for url in urls:

        try:

            # PDF DOWNLOAD
            if ".pdf" in url.lower():

                filename = f"PDF_{count}.pdf"

                cmd = f'yt-dlp -o "{filename}" "{url}"'

                process = await asyncio.create_subprocess_shell(cmd)

                await process.communicate()

                if os.path.exists(filename):

                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=filename,
                        caption=f"📄 PDF {count}"
                    )

                    os.remove(filename)

            # VIDEO DOWNLOAD
            else:

                filename = f"Video_{count}.mp4"

                cmd = f'yt-dlp --cookies cookies.txt -o "{filename}" "{url}"'

                process = await asyncio.create_subprocess_shell(cmd)

                await process.communicate()

                if os.path.exists(filename):

                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=filename,
                        caption=f"🎬 Video {count}"
                    )

                    os.remove(filename)

            count += 1

        except Exception as e:

            await message.reply_text(
                f"❌ Error:\n{e}"
            )

    os.remove(txt_path)

    await message.reply_text(
        "✅ All Downloads Completed"
    )

print("🚀 Bot Started")

bot.run()
