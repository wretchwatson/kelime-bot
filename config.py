import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
guild_env = os.getenv("GUILD_ID", "")
GUILD_ID = int(guild_env) if guild_env.isdigit() else None
