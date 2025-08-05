from main import LOGGER as LOGS, prefixes, Config, Msg
from pyrogram import Client as AFK
from pyrogram.types import Message
from handlers.html import parse_html
import os


class TgHandler:
    def __init__(self, bot: AFK, m: Message, path: str) -> None:
        self.bot = bot
        self.m = m
        self.path = path

    @staticmethod
    async def error_message(bot: AFK, m: Message, error: str):
        LOGS.error(error)
        await bot.send_message(
            chat_id=Config.LOG_CH,
            text=f"<b>Error:</b> `{error}`"
        )

    async def linkMsg2(self, List):
        a = ""
        try:
            for data in List:
                if len(f"{a}{data}") > 3500:
                    await self.bot.send_message(
                        chat_id=self.m.chat.id,
                        text=f'**Failed files are ({len(List)}) :-\n\n{a}',
                        disable_web_page_preview=True,
                    )
                    a = ""
                a += data
            await self.bot.send_message(
                chat_id=self.m.chat.id,
                text=f'**Failed files are ({len(List)}) :-\n\n{a}',
                disable_web_page_preview=True,
            )
            List.clear()
        except:
            await self.m.reply_text("Done")
            List.clear()

    async def downloadMedia(self, msg):
        sPath = f"{Config.DOWNLOAD_LOCATION}/FILE/{self.m.chat.id}"
        os.makedirs(sPath, exist_ok=True)
        file = await self.bot.download_media(
            message=msg,
            file_name=f"{sPath}/{msg.id}"
        )
        return file

async def readTxt(self, x):
        try:
            with open(x, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content:
                await self.m.reply_text("**The file is empty.**")
                os.remove(x)
                return []

            content = content.split("\n")
            name_links = []
            for i in content:
                if i.strip() != "":
                    parts = i.split(":", 1)
                    if len(parts) == 2:
                        name_links.append((parts[0].strip(), parts[1].strip()))  # ✅ Return tuple

            if not name_links:
                await self.m.reply_text("**No valid links found in the file.**")
                os.remove(x)
                return []

            os.remove(x)
            print(len(name_links))
            return name_links

        except Exception as e:
            LOGS.error(e)
            await self.m.reply_text("**Invalid file input.**")
            os.remove(x)
            return []
        name = (
            rawName.replace("/", "_")
            .replace("|", "_")
            .replace(":", "-")
            .replace("*", "")
            .replace("#", "")
            .replace("\t", "")
            .replace(";", "")
            .replace("'", "")
            .replace('"', '')
            .replace("{", "(")
            .replace("}", ")")
            .replace("`", "")
            .replace("__", "_")
            .strip()
        )
        return str(name)

    @staticmethod
    def short_name(name: str):
        return name[:70] if len(name) > 100 else name

    def user_(self):
        try:
            if self.m.from_user is None:
                return self.m.chat.title
            return self.m.from_user.first_name
        except Exception as e:
            print(e)
            return "Group Admin"

    @staticmethod
    def index_(index: int):
        return max(0, int(index) - 1)

    @staticmethod
    def resolution_(resolution: str):
        if resolution not in ['144', '180', '240', '360', '480', '720', '1080']:
            return '360'
        return resolution


class TgClient(TgHandler):
    async def Ask_user(self):
        userr = TgClient.user_(self)
        msg1 = await self.bot.send_message(
            self.m.chat.id,
            text=Msg.TXT_MSG.format(user=userr)
        )
        inputFile = await self.bot.listen(self.m.chat.id)

        if inputFile.document:
            if inputFile.document.mime_type not in ["text/plain", "text/html"]:
                return

            txt_name = inputFile.document.file_name.replace("_", " ")
            x = await TgClient.downloadMedia(self, inputFile)
            await inputFile.delete(True)

            if inputFile.document.mime_type == "text/plain":
                nameLinks = await TgClient.readTxt(self, x)
                Token = inputFile.caption if inputFile.caption else None

            elif inputFile.document.mime_type == "text/html":
                nameLinks = parse_html(x)
                Token = None
                os.remove(x)

            msg2 = await self.bot.send_message(
                self.m.chat.id,
                text=Msg.CMD_MSG_1.format(txt=txt_name, no_of_links=len(nameLinks))
            )
            user_index = await self.bot.listen(self.m.chat.id)
            index = int(user_index.text)
            num = TgClient.index_(index=index)

            msg3 = await self.bot.send_message(
                self.m.chat.id,
                text="**Send Caption :-**"
            )
            user_caption = await self.bot.listen(self.m.chat.id)
            caption = user_caption.text

            msg4 = await self.bot.send_message(
                self.m.chat.id,
                text="**Send Quality (Default is 360) :-**"
            )
            user_quality = await self.bot.listen(self.m.chat.id)
            resolution = user_quality.text
            quality = TgClient.resolution_(resolution=resolution)

            return nameLinks, num, caption, quality, Token, txt_name, userr
        else:
            return

    async def thumb(self):
        t = await self.bot.ask(
            self.m.chat.id,
            "**Send Thumb JPEG/PNG or Telegraph Link or No :-**"
        )
        if t.text:
            return t.text
        elif t.photo:
            return await TgClient.downloadMedia(self, t)
        else:
            return "no"