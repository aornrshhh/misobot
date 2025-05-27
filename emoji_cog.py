# cogs/emoji_cog.py
import discord
from discord.ext import commands
from discord import app_commands
import re
import urllib.parse
import emoji  # pip install emoji


class EmojiCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="emoji", description="이모지 확대하기♡")
    @app_commands.describe(이모지_입력="이모지 이름 입력")
    async def emoji(self, interaction: discord.Interaction, 이모지_입력: str):
        target = 이모지_입력.strip()
        url = None
        size = 128

        # 1) 커스텀 이모지 처리
        m1 = re.fullmatch(r'<a?:([\w~]+):(\d+)>', target)
        if m1:
            eid = m1.group(2)
            ext = 'gif' if target.startswith('<a:') else 'png'
            url = f"https://cdn.discordapp.com/emojis/{eid}.{ext}?size={size}"
        else:
            # 2) :shortcode: 처리
            m2 = re.fullmatch(r':([\w+-]+):', target)
            if m2:
                name = m2.group(1)
                em = discord.utils.get(self.bot.emojis, name=name)
                if em:
                    url = f"{em.url}?size={size}"
                else:
                    uni = emoji.emojize(target, language='alias')
                    if uni != target:
                        try:
                            p = discord.PartialEmoji.from_str(uni)
                            url = self._get_adjusted_unicode_emoji_url(
                                p.url, size)
                        except ValueError:
                            pass
            else:
                # 3) 유니코드 이모지 처리
                try:
                    p = discord.PartialEmoji.from_str(target)
                    if p.id:
                        url = f"{p.url}?size={size}"
                    else:
                        url = self._get_adjusted_unicode_emoji_url(p.url, size)
                except ValueError:
                    pass

        if url and url.startswith("http"):
            await interaction.response.send_message(url)
        else:
            await interaction.response.send_message(
                "올바른 이모지 형식으로 입력해주세요: `<:이름:ID>`, `:이름:`, 또는 유니코드 문자.",
                ephemeral=True)

    @app_commands.command(name="emoji_list", description="이모지 이름 한눈에 보기♡")
    async def emoji_list(self, interaction: discord.Interaction):
        emojis = interaction.guild.emojis if interaction.guild else []
        # 임베드 생성 (제목 아래 빈 줄 추가, 색상 #feb7d5)
        embed = discord.Embed(title="이모지 목록",
                              description="\n",
                              color=discord.Color(0xFEB7D5))
        if emojis:
            embed.description += "\n".join(f"{e} `:{e.name}:`"
                                           for e in emojis)[:4096]
        else:
            embed.description += "등록된 커스텀 이모지가 없어요."

        await interaction.response.send_message(embed=embed)

    def _get_adjusted_unicode_emoji_url(self, base_url: str | None,
                                        size: int) -> str | None:
        if not base_url:
            return None
        try:
            parsed = urllib.parse.urlparse(base_url)
            params = urllib.parse.parse_qs(parsed.query)
            params['size'] = [str(size)]
            if 'quality' not in params:
                params['quality'] = ['lossless']
            new_query = urllib.parse.urlencode(params, doseq=True)
            return urllib.parse.urlunparse(parsed._replace(query=new_query))
        except Exception as e:
            print(f"URL 조정 오류: {e}")
            return None


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiCog(bot))
