import os
import discord
from discord.ext import commands
import asyncio
from aiohttp import web
from dotenv import load_dotenv

# ─── Keep-Alive 웹서버 정의 ───────────────────────────────────────
async def handle(request):
    return web.Response(text="OK")

async def start_keep_alive():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 3000)
    await site.start()

# ────────────────────────────────────────────────────────────────

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # ① 봇 루프가 돌아가고 나서 Keep-Alive 서버 시작
        self.loop.create_task(start_keep_alive())
        print("▶ Keep-alive server task scheduled")

        # ② Cog 확장 로드
        for ext in [
                "cogs.emoji_cog",
                "cogs.sm_cog",
                "cogs.dday_cog",
        ]:
            await self.load_extension(ext)
            print(f"Loaded extension: {ext}")

        # ③ 글로벌 슬래시 명령어 동기화
        await self.tree.sync()
        print("▶ Commands synced globally")

if __name__ == "__main__":
    # ⬇️ 여기에 dotenv 불러오는 코드 정확히 위치
    load_dotenv(dotenv_path=".env")
    token = os.getenv("DISCORD_TOKEN")

    print("토큰 확인:", token)  # 이 줄 추가!

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN이 설정되지 않았습니다.")
    
    bot = MyBot()
    bot.run(token)
