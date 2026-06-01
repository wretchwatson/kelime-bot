import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
bot.run(config.TOKEN)
