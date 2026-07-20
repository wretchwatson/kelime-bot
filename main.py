import discord
from discord.ext import commands
from aiohttp import web
import config
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Health check sunucusu {port} portunda başladı")

@bot.event
async def on_ready():
    print(f"Bot giriş yaptı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} komut senkronize edildi")
    except Exception as e:
        print(f"Komut senkronizasyon hatası: {e}")

async def setup_hook():
    await bot.load_extension("cogs.general")
    await bot.load_extension("cogs.word_game")

bot.setup_hook = setup_hook

async def main():
    await start_webserver()
    await bot.start(config.TOKEN)

asyncio.run(main())
