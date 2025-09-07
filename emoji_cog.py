import discord
from discord.ext import commands
from discord import app_commands
import re
import emoji


class EmojiCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="emo", description="그곳 이 커진다")
    @app_commands.describe(이모지_입력="이모지 이름 입력")
    async def emoji(self, interaction: discord.Interaction, 이모지_입력: str):
        target = 이모지_입력.strip()
        url = None
        size = 128

        # 먼저 명령어 입력 흔적 없애기
        await interaction.response.defer(ephemeral=True)  # 원래 메시지는 숨김

        # 1) 커스텀 이모지
        m1 = re.fullmatch(r'<a?:([\w~]+):(\d+)>', target)
        if m1:
            eid = m1.group(2)
            ext = 'gif' if target.startswith('<a:') else 'png'
            url = f"https://cdn.discordapp.com/emojis/{eid}.{ext}?size={size}"

        # 2) :shortcode:
        elif re.fullmatch(r':([\w+-]+):', target):
            em = discord.utils.get(self.bot.emojis, name=target.strip(":"))
            if em:
                url = f"{em.url}?size={size}"
            else:
                uni = emoji.emojize(target, language="alias")
                if uni != target:
                    await interaction.followup.send(uni)
                    return

        # 3) 유니코드 이모지
        else:
            if emoji.is_emoji(target):
                await interaction.followup.send(target)
                return

        # 최종 응답
        if url:
            await interaction.followup.send(url)
        else:
            await interaction.followup.send(
                "올바른 이모지 형식으로 입력해주세요! :\n`<:이름:ID>`, `:이름:`, 또는 유니코드 문자."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiCog(bot))
