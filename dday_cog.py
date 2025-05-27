import discord
from discord.ext import commands
from discord import app_commands # SelectOption은 ui.py에서 사용 또는 discord에서 직접 임포트
import datetime
from utils import load_data, save_data, get_user_data
from ui import DDayDeleteView

class DdayCog(commands.Cog):
    # 클래스 변수로 그룹 정의
    dday_group = app_commands.Group(name="dday", description="디데이 관리 명령어")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @dday_group.command(name="add", description="디데이 설정하기♡")
    @app_commands.describe(title="디데이 제목", date="날짜 (YYYY-MM-DD)")
    async def dday_add_command(self, interaction: discord.Interaction,
                               title: str, date: str):
        user_id = interaction.user.id
        user_id_str = str(user_id)
        try:
            dday_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            await interaction.response.send_message(
                "날짜 형식이 잘못됐어ㅠㅅㅠYYYY-MM-DD 형식으로 입력해줄래?", ephemeral=True)
            return

        get_user_data(user_id)
        data_to_modify = load_data()
        user_data_node = data_to_modify.setdefault(user_id_str, {})
        if not isinstance(user_data_node.get("dday"), list):
            user_data_node["dday"] = []
        user_data_node["dday"].append({"title": title, "date": date})
        save_data(data_to_modify)

        today = datetime.date.today()
        delta = (dday_date - today).days
        await interaction.response.send_message(
            f"'{title}' 설정 완료했어૮꒰⸝⸝> ·̫ <⸝⸝꒱ა⋆⸜ D-{delta}♡")

    @dday_group.command(name="check", description="디데이 확인하기♡")
    async def dday_check_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = get_user_data(user_id)
        dday_list = user_data.get("dday", [])

        embed = discord.Embed(title=f"D-Day♡",
                              color=discord.Color.from_rgb(254, 183, 213))

        # 제목 아래 빈 줄 추가 (요청하신 대로)
        # 빈 필드를 추가하여 간격을 만듭니다.
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        if not dday_list:
            # 디데이 목록이 없을 경우, description을 설정합니다.
            # 이 경우, 아래 내용 필드는 추가되지 않으므로, 바로 푸터가 표시됩니다.
            embed.description = "설정한 디데이가 없어 🚰·̫🚰"
        else:
            msg_content_list = [] # 각 디데이 항목을 저장할 리스트
            today = datetime.date.today()
            for d in dday_list:
                try:
                    dday_date = datetime.datetime.strptime(
                        d["date"], "%Y-%m-%d").date()
                    delta = (dday_date - today).days
                    msg_content_list.append(f"**{d['title']}**: D-{delta}♡ ({d['date']})")
                except ValueError:
                    msg_content_list.append(f"**{d['title']}**: 날짜 형식이 잘못되었어!")
                    print(
                        f"Error: Invalid date format in data for user {user_id}: {d['date']}"
                    )
            # 리스트의 모든 항목을 줄바꿈 문자로 연결하여 description에 설정
            # 이렇게 하면 각 디데이가 별도의 줄에 표시됩니다.
            embed.description = "\n".join(msg_content_list)

        # 내용 아래 빈 줄 추가 (요청하신 대로)
        # embed.description (즉, 디데이 목록)이 표시된 후 빈 줄이 오도록 합니다.
        # 디데이 목록이 없는 경우에는 이 필드가 추가되지 않도록 조건을 걸 수 있습니다.
        if dday_list: # 디데이 목록이 있을 때만 내용 아래 빈 줄 추가
            embed.add_field(name="\u200b", value="\u200b", inline=False)


        embed.set_footer(text="ドキドキ !",
                         icon_url="https://i.ibb.co/rqZ0084/misocute.jpg")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @dday_group.command(name="delete", description="디데이 삭제하기♡")
    async def dday_delete_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = get_user_data(user_id)
        dday_list = user_data.get("dday", [])
        if not dday_list:
            await interaction.response.send_message("삭제할 디데이가 없어ㅠㅅㅠ", ephemeral=True)
            return

        options = [
            discord.SelectOption(label=f"{d['title']} ({d['date']})", value=str(i))
            for i, d in enumerate(dday_list)
        ]
        view = DDayDeleteView(options, user_id)
        await interaction.response.send_message("삭제할 디데이를 골라줘!( ⩌⩊⩌)", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DdayCog(bot))