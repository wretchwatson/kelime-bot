import discord
from discord.ext import commands
from discord import app_commands
from utils.game_logic import GameManager

game = GameManager()

class WordGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kanal-ayarla", description="Oyun kanalını belirler (yönetici)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, kanal: discord.TextChannel):
        game.scores[str(interaction.guild_id)] = game.scores.get(str(interaction.guild_id), {})
        game.scores[str(interaction.guild_id)]["channel_id"] = kanal.id
        game._save_scores()
        embed = discord.Embed(
            title="Kanal Ayarlandı",
            description=f"Oyun kanalı {kanal.mention} olarak belirlendi.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="basla", description="Yeni bir kelime zinciri oyunu başlatır")
    async def start_game(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        channel_id = interaction.channel_id

        existing = game.get_game(guild_id)
        if existing:
            await interaction.response.send_message(
                "Zaten aktif bir oyun var. Önce `/bitir` ile bitir.",
                ephemeral=True,
            )
            return

        word = game.start_game(guild_id, channel_id)
        last = game.get_last_letter(word)

        embed = discord.Embed(
            title="Oyun Başladı!",
            description=f"İlk kelime: **{word}**\nSon harf: **{last.upper()}**\n\nBu harfle başlayan bir kelime yaz!",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bitir", description="Aktif oyunu bitirir")
    async def end_game(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if game.end_game(guild_id):
            await interaction.response.send_message("Oyun sonlandırıldı. Tebrikler!")
        else:
            await interaction.response.send_message("Aktif oyun bulunamadı.", ephemeral=True)

    @app_commands.command(name="skor", description="Puanını gösterir")
    async def score(self, interaction: discord.Interaction, kullanici: discord.User = None):
        user = kullanici or interaction.user
        score = game.get_score(interaction.guild_id, user.id)
        await interaction.response.send_message(f"{user.mention} puanı: **{score}**")

    @app_commands.command(name="siralama", description="Liderlik tablosunu gösterir")
    async def leaderboard(self, interaction: discord.Interaction):
        leaderboard = game.get_leaderboard(interaction.guild_id)
        if not leaderboard:
            await interaction.response.send_message("Henüz puan kaydı yok.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Liderlik Tablosu",
            color=discord.Color.gold(),
        )
        for i, (user_id, score) in enumerate(leaderboard, 1):
            user = self.bot.get_user(user_id)
            if user is None:
                try:
                    user = await self.bot.fetch_user(user_id)
                except:
                    pass
            name = user.display_name if user else f"Kullanıcı {user_id}"
            embed.add_field(
                name=f"{i}. {name}",
                value=f"**{score}** puan",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return

        guild_id = message.guild.id
        game_state = game.get_game(guild_id)

        if not game_state or not game_state["active"]:
            return

        channel_id = game_state["channel_id"]
        guild_scores = game.scores.get(str(guild_id), {})
        saved_channel = guild_scores.get("channel_id")
        target_channel = saved_channel or channel_id

        if message.channel.id != target_channel:
            return

        word = message.content.strip()
        if not word:
            return

        result, error = game.submit_word(guild_id, message.author.id, word)

        if result is None:
            await message.add_reaction("❌")
            await message.channel.send(f"{message.author.mention} ❌ **{error}**")
            return

        await message.add_reaction("✅")
        if result == "ğ":
            next_msg = f"{message.author.mention} **{word.upper()}** ✅ (+{len(word)} puan)\n📌 Son harf ğ — bir sonraki kelime **G** veya **K** ile başlamalı!"
        else:
            next_msg = f"{message.author.mention} **{word.upper()}** ✅ (+{len(word)} puan)\n📌 Sıradaki harf: **{result.upper()}**"
        await message.channel.send(next_msg)

async def setup(bot):
    await bot.add_cog(WordGame(bot))
