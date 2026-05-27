import os
import re
import sys
import asyncio
import requests
import subprocess

import core as helper

from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, WEBHOOK, PORT

from aiohttp import ClientSession, web
from pyromod import listen

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from style import Ashu
from utk import get_utkarsh_cdn

COOKIES_FILE = "cookies.txt"

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):

    return web.json_response(
        "Leech Bot Running"
    )

async def web_server():

    web_app = web.Application(
        client_max_size=30000000
    )

    web_app.add_routes(routes)

    return web_app

@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, m: Message):

    await m.reply_text(
        Ashu.START_TEXT,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✜ Powerful Leech Bot ✜",
                        url="https://t.me/example"
                    )
                ]
            ]
        )
    )

@bot.on_message(filters.command("cookies"))
async def cookies_handler(bot: Client, m: Message):

    await m.reply_text(
        "📂 Send Cookies TXT File"
    )

    cookie_msg: Message = await bot.listen(
        m.chat.id
    )

    if not cookie_msg.document:

        return await m.reply_text(
            "❌ Invalid File"
        )

    await cookie_msg.download(
        file_name="cookies.txt"
    )

    await m.reply_text(
        "✅ Cookies Saved Successfully"
    )

@bot.on_message(filters.command(["upload"]))
async def upload_command(bot: Client, m: Message):

    editable = await m.reply_text(
        "📂 Send TXT File"
    )

    input_msg: Message = await bot.listen(
        editable.chat.id
    )

    x = await input_msg.download()

    await input_msg.delete(True)

    try:

        with open(
            x,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().splitlines()

        links = []

        for i in content:

            if "://" in i:

                links.append(
                    i.split("://", 1)
                )

        os.remove(x)

    except Exception:

        await m.reply_text(
            "❌ Invalid TXT File"
        )

        return

    total_links = len(links)

    await editable.edit(
        f"📄 Total Links Found : {total_links}"
    )

    count = 1

    for i in range(len(links)):

        try:

            V = links[i][1]
            url = "https://" + V

            if "utkarsh" in url:
                url = get_utkarsh_cdn(url)

            raw_title = links[i][0]

            name1 = re.sub(
                r'[^a-zA-Z0-9 _.-]',
                '',
                raw_title
            ).strip()

            current_number = str(
                count
            ).zfill(3)

            name = (
                f"{current_number}_{name1}"
            )

            cc = f"🎬 {name1}"

            progress_msg = await m.reply_text(
                f"⬇️ Downloading {name1}"
            )

            if ".pdf" in url.lower():

                pdf_name = f"{name}.pdf"

                pdf_cmd = f'''yt-dlp \
                --cookies cookies.txt \
                --retries 25 \
                -o "{pdf_name}" \
                "{url}" '''

                subprocess.run(
                    pdf_cmd,
                    shell=True
                )

                if os.path.exists(pdf_name):

                    await bot.send_document(
                        chat_id=m.chat.id,
                        document=pdf_name,
                        caption=cc
                    )

                    os.remove(pdf_name)

            else:

                cmd = f'''yt-dlp \
                --cookies cookies.txt \
                --external-downloader aria2c \
                --downloader-args "aria2c:-x 16 -j 16 -s 16 -k 1M" \
                --retries 25 \
                -o "{name}.mp4" \
                "{url}" '''

                process = await asyncio.create_subprocess_shell(cmd)

                await process.communicate()

                filename = f"{name}.mp4"

                if os.path.exists(filename):

                    await bot.send_video(
                        chat_id=m.chat.id,
                        video=filename,
                        caption=cc
                    )

                    os.remove(filename)

            count += 1

            try:
                await progress_msg.delete()
            except:
                pass

        except Exception as e:

            await m.reply_text(
                f"❌ Error : {str(e)}"
            )

    await m.reply_text(
        "✅ Successfully Done"
    )

async def main():

    if WEBHOOK:

        app = await web_server()

        runner = web.AppRunner(app)

        await runner.setup()

        site = web.TCPSite(
            runner,
            "0.0.0.0",
            PORT
        )

        await site.start()

if __name__ == "__main__":

    print("🚀 Bot Started")

    async def start_bot():

        await bot.start()

    async def start_web():

        await main()

    loop = asyncio.get_event_loop()

    try:

        loop.create_task(start_bot())

        loop.create_task(start_web())

        loop.run_forever()

    except KeyboardInterrupt:

        pass

    finally:

        loop.stop()
