# cogs/emoji_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import re
import emoji  # pip install emoji


class EmojiCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="emo", description="그곳 이 커진다")
    @app_commands.describe(이모지_입력="이모지 이름 입력")
    async def emoji(self, interaction: discord.Interaction, 이모지_입력: str):
        target = 이모지_입력.strip()
        url = None
        size = 128

        # 1) 커스텀 이모지 (<:name:id> 또는 <a:name:id>)
        m1 = re.fullmatch(r'<a?:([\w~]+):(\d+)>', target)
        if m1:
            eid = m1.group(2)
            ext = 'gif' if target.startswith('<a:') else 'png'
            url = f"https://cdn.discordapp.com/emojis/{eid}.{ext}?size={size}"

        # 2) :shortcode: (예: :smile:)
        elif re.fullmatch(r':([\w+-]+):', target):
            em = discord.utils.get(self.bot.emojis, name=target.strip(":"))
            if em:
                url = f"{em.url}?size={size}"
            else:
                uni = emoji.emojize(target, language="alias")
                if uni != target:
                    await interaction.response.send_message(uni)
                    return

        # 3) 유니코드 이모지 직접 입력
        else:
            if emoji.is_emoji(target):
                await interaction.response.send_message(target)
                return

        # 최종 응답
        if url:
            await interaction.response.send_message(url)
        else:
            await interaction.response.send_message(
                "올바른 이모지 형식으로 입력해주세요! :\n`<:이름:ID>`, `:이름:`, 또는 유니코드 문자.",
                ephemeral=True
            )

    @app_commands.command(name="emoji_list", description="서버 이모지 목록을 보여줍니다")
    async def emoji_list(self, interaction: discord.Interaction):
        emojis = interaction.guild.emojis if interaction.guild else []
        embed = discord.Embed(
            title="이모지 목록",
            color=discord.Color(0xFEB7D5)
        )

        if emojis:
            lines = [f"{e} `:{e.name}:`" for e in emojis]
            desc = ""
            for line in lines:
                if len(desc) + len(line) + 1 > 4096:
                    break
                desc += line + "\n"
            embed.description = desc
        else:
            embed.description = "그딴거 없어"

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiCog(bot))
