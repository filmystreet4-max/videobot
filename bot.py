import os
import re
import asyncio
import subprocess

from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start"))
async def start_handler(client, message):

    await message.reply_text(
        "Bot Working ✅\n\nUse /upload"
    )

@bot.on_message(filters.command("upload"))
async def upload_handler(client, message):

    ask = await message.reply_text(
        "📂 TXT file bhejo"
    )

    txt: Message = await bot.listen(message.chat.id)

    if not txt.document:
        return await message.reply_text("❌ TXT file nahi bheji")

    file_path = await txt.download()

    await message.reply_text("📥 TXT received")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    links = []

    for line in lines:
        line = line.strip()

        if line.startswith("http"):
            links.append(line)

    if not links:
        return await message.reply_text("❌ No links found")

    count = 1

    for url in links:

        try:

            if ".pdf" in url.lower():

                filename = f"file_{count}.pdf"

                cmd = f'yt-dlp -o "{filename}" "{url}"'

                subprocess.run(cmd, shell=True)

                if os.path.exists(filename):

                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=filename,
                        caption=f"PDF {count}"
                    )

                    os.remove(filename)

            else:

                filename = f"video_{count}.mp4"

                cmd = f'yt-dlp -o "{filename}" "{url}"'

                subprocess.run(cmd, shell=True)

                if os.path.exists(filename):

                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=filename,
                        caption=f"Video {count}"
                    )

                    os.remove(filename)

            count += 1

        except Exception as e:

            await message.reply_text(
                f"❌ Error:\n{e}"
            )

    await message.reply_text("✅ Done")

print("🚀 Bot Started")

bot.run()
