import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Bot gecikmesini gösterir")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! **{latency}ms**")

    @app_commands.command(name="yardim", description="Komut listesini gösterir")
    async def yardim(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Kelime Zinciri Botu - Yardım",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="/kanal-ayarla",
            value="Oyun kanalını belirler (yönetici)",
            inline=False,
        )
        embed.add_field(name="/basla", value="Yeni bir oyun başlatır", inline=False)
        embed.add_field(
            name="/skor",
            value="Kendi puanını gösterir",
            inline=False,
        )
        embed.add_field(name="/siralama", value="Liderlik tablosunu gösterir", inline=False)
        embed.add_field(name="/bitir", value="Oyunu bitirir", inline=False)
        embed.add_field(name="/ping", value="Bot gecikmesini gösterir", inline=False)
        embed.set_footer(text="Oyunda kanala direkt kelime yazman yeterli!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
