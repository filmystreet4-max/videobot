# ================= IMPORTS ================= #

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


# ================= COOKIES ================= #

COOKIES_FILE = "cookies.txt"


# ================= BOT ================= #

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

routes = web.RouteTableDef()


# ================= WEB ================= #

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


# ================= START ================= #

@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, m: Message):

    await m.reply_text(
        Ashu.START_TEXT,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✜ Powerful Leech Bot ✜",
                        url="https://t.me/AshutoshGoswami24"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🦋 Support 🦋",
                        url="https://t.me/AshuSupport"
                    )
                ]
            ]
        )
    )


# ================= STOP ================= #

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):

    await m.reply_text(
        "🛑 Bot Restarting..."
    )

    os.execl(
        sys.executable,
        sys.executable,
        *sys.argv
    )


# ================= COOKIES ================= #

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


# ================= UPLOAD ================= #

@bot.on_message(
    filters.command(["upload"])
)
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

        try:
            os.remove(x)
        except:
            pass

        return

    total_links = len(links)

    await editable.edit(
        f"""
📄 Total Links Found : {total_links}

Send Start Number

Example : 1
"""
    )

    input0: Message = await bot.listen(
        editable.chat.id
    )

    raw_text = input0.text

    await input0.delete(True)

    await editable.edit(
        "📌 Send Batch Name"
    )

    input1: Message = await bot.listen(
        editable.chat.id
    )

    raw_text0 = input1.text

    await input1.delete(True)

    await editable.edit(
        Ashu.Q1_TEXT
    )

    input2: Message = await bot.listen(
        editable.chat.id
    )

    raw_text2 = input2.text

    await input2.delete(True)

    await editable.edit(
        Ashu.C1_TEXT
    )

    input3: Message = await bot.listen(
        editable.chat.id
    )

    raw_text3 = input3.text

    await input3.delete(True)

    MR = raw_text3

    await editable.edit(
        Ashu.T1_TEXT
    )

    input6: Message = await bot.listen(
        editable.chat.id
    )

    thumb = input6.text

    await input6.delete(True)

    await editable.delete()

    # ================= THUMB ================= #

    if (
        thumb.startswith("http://")
        or
        thumb.startswith("https://")
    ):

        subprocess.getstatusoutput(
            f"wget '{thumb}' -O 'thumb.jpg'"
        )

        thumb = "thumb.jpg"

    else:

        thumb = "no"

    # ================= START NUMBER ================= #

    count = 1

    if len(links) > 1:

        try:

            count = int(raw_text)

            if count < 1:

                count = 1

        except:

            count = 1

    # ================= MAIN LOOP ================= #

    try:

        for i in range(
            count - 1,
            len(links)
        ):

            try:

                # ================= URL ================= #

                V = links[i][1].replace(
                    "file/d/",
                    "uc?export=download&id="
                ).replace(
                    "www.youtube-nocookie.com/embed",
                    "youtu.be"
                ).replace(
                    "?modestbranding=1",
                    ""
                ).replace(
                    "/view?usp=sharing",
                    ""
                )

                url = "https://" + V

                # ================= VISIONIAS ================= #

                if "visionias" in url:

                    async with ClientSession() as session:

                        async with session.get(
                            url,
                            headers={
                                "User-Agent": "Mozilla/5.0"
                            }
                        ) as resp:

                            text = await resp.text()

                            match = re.search(
                                r"(https://.*?playlist.m3u8.*?)\"",
                                text
                            )

                            if match:

                                url = match.group(1)

                # ================= CLASSPLUS ================= #

                elif "videos.classplusapp" in url:

                    try:

                        response = requests.get(
                            f"https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}",
                            headers={
                                "x-access-token": "YOUR_TOKEN"
                            },
                            timeout=30
                        )

                        data = response.json()

                        if "url" in data:

                            url = data["url"]

                    except:
                        pass

                elif "utkarsh" in url:

                    url = get_utkarsh_cdn(url)

                # ================= MPD ================= #

                elif "/master.mpd" in url:

                    id = url.split("/")[-2]

                    url = (
                        "https://d26g5bnklkwsh4.cloudfront.net/"
                        + id +
                        "/master.m3u8"
                    )

                # ================= TITLE FIX ================= #

                raw_title = links[i][0]

                raw_title = raw_title.replace(
                    "https",
                    ""
                )

                raw_title = raw_title.replace(
                    "http",
                    ""
                )

                raw_title = raw_title.replace(
                    ".html",
                    ""
                )

                raw_title = raw_title.replace(
                    "html",
                    ""
                )

                name1 = re.sub(
                    r'[^a-zA-Z0-9 _.-]',
                    '',
                    raw_title
                ).strip()

                safe_name = re.sub(
                    r'[^a-zA-Z0-9]',
                    '_',
                    name1[:80]
                )

                current_number = str(
                    count
                ).zfill(3)

                name = (
                    f"{current_number}_{safe_name}"
                )

                # ================= CAPTION ================= #

                cc = f"""
🎥 Vid_ID : {current_number}

📌 Title : {name1}

📚 Batch : {raw_text0}

📝 Caption : {MR}
"""

                cc1 = f"""
📁 Pdf_ID : {current_number}

📌 Title : {name1}

📚 Batch : {raw_text0}
"""

                # ================= STATUS ================= #

                progress_msg = await m.reply_text(
                    f"""
⬇️ Downloading

📌 {name1}

🎬 Quality : {raw_text2}
"""
                )

                # ================= GOOGLE DRIVE ================= #

                if "drive" in url:

                    ka = await helper.download(
                        url,
                        name
                    )

                    await bot.send_document(
                        chat_id=m.chat.id,
                        document=ka,
                        caption=cc1
                    )

                    if os.path.exists(ka):

                        os.remove(ka)

                # ================= PDF ================= #

                elif ".pdf" in url.lower():

                    pdf_name = f"{name}.pdf"

                    pdf_cmd = f'''yt-dlp \
                    --cookies cookies.txt \
                    --no-check-certificate \
                    --extractor-retries 25 \
                    --file-access-retries 25 \
                    --retries 25 \
                    --fragment-retries 25 \
                    --socket-timeout 30 \
                    -o "{pdf_name}" \
                    "{url}" '''

                    subprocess.run(
                        pdf_cmd,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    # ================= FALLBACK ================= #

                    if (
                        not os.path.exists(pdf_name)
                        or
                        os.path.getsize(pdf_name) < 5000
                    ):

                        r = requests.get(
                            url,
                            headers={
                                "User-Agent": "Mozilla/5.0"
                            },
                            stream=True,
                            verify=False,
                            timeout=60
                        )

                        with open(
                            pdf_name,
                            "wb"
                        ) as f:

                            for chunk in r.iter_content(
                                1024 * 100
                            ):

                                if chunk:

                                    f.write(chunk)

                    if (
                        not os.path.exists(pdf_name)
                        or
                        os.path.getsize(pdf_name) < 5000
                    ):

                        raise Exception(
                            "PDF Download Failed"
                        )

                    await bot.send_document(
                        chat_id=m.chat.id,
                        document=pdf_name,
                        caption=cc1
                    )

                    if os.path.exists(pdf_name):

                        os.remove(pdf_name)

                # ================= VIDEO ================= #

                else:

                    # ================= M3U8 ================= #

                    if ".m3u8" in url:

                        cmd = f'''yt-dlp \
                        --cookies cookies.txt \
                        --no-check-certificate \
                        --hls-prefer-ffmpeg \
                        --extractor-retries 25 \
                        --file-access-retries 25 \
                        --retries 25 \
                        --fragment-retries 25 \
                        --concurrent-fragments 10 \
                        --socket-timeout 30 \
                        -o "{name}.mp4" \
                        "{url}" '''

                    else:

                        cmd = f'''yt-dlp \
                        --cookies cookies.txt \
                        --no-check-certificate \
                        --external-downloader aria2c \
                        --downloader-args "aria2c:-x 16 -j 16 -s 16 -k 1M" \
                        --extractor-retries 25 \
                        --file-access-retries 25 \
                        --retries 25 \
                        --fragment-retries 25 \
                        --socket-timeout 30 \
                        -o "{name}.mp4" \
                        "{url}" '''

                    res_file = await helper.download_video(
                        url,
                        cmd,
                        name
                    )

                    # ================= FALLBACK ================= #

                    if not res_file:

                        fallback_cmd = f'''yt-dlp \
                        --cookies cookies.txt \
                        --no-check-certificate \
                        --socket-timeout 30 \
                        -o "{name}.mp4" \
                        "{url}" '''

                        subprocess.run(
                            fallback_cmd,
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )

                        if os.path.exists(
                            f"{name}.mp4"
                        ):

                            res_file = (
                                f"{name}.mp4"
                            )

                    filename = res_file

                    if (
                        not filename
                        or
                        not os.path.exists(filename)
                    ):

                        raise Exception(
                            "Video Download Failed"
                        )

                    try:
                        await progress_msg.delete()
                    except:
                        pass

                    await helper.send_vid(
                        bot,
                        m,
                        cc,
                        filename,
                        thumb,
                        name,
                        progress_msg
                    )

                count += 1

                await asyncio.sleep(2)

            except Exception as e:

                await m.reply_text(
                    f"""
❌ Download Failed

📌 Name :
{name1}

🔗 URL :
`{url}`

⚠️ Error :
`{str(e)}`
"""
                )

                continue

    except Exception as e:

        await m.reply_text(
            str(e)
        )

    await m.reply_text(
        "✅ Successfully Done"
    )


# ================= MAIN ================= #

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

        print(
            f"Web server started on port {PORT}"
        )


if __name__ == "__main__":

    print(
        "🚀 Bot Started"
    )

    async def start_bot():

        await bot.start()

    async def start_web():

        await main()

    loop = asyncio.get_event_loop()

    try:

        loop.create_task(
            start_bot()
        )

        loop.create_task(
            start_web()
        )

        loop.run_forever()

    except KeyboardInterrupt:

        pass

    finally:

        loop.stop()
