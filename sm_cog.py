import discord
from discord.ext import commands
from discord import app_commands
import random
from utils import load_data, save_data, get_user_data

class SmCog(commands.Cog):
    # 클래스 변수로 그룹 정의
    sm_group = app_commands.Group(name="sm", description="미小 bot과 설레는 sm 플레이♡")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.bot.tree.add_command(SmCog.sm_group) # setup에서 add_cog 시 자동 추가 기대

    @sm_group.command(name="add", description="나를 이런 문장으로 조련해주세요♡")
    @app_commands.describe(text="문장 추가하기♡")
    async def sm_add_command(self, interaction: discord.Interaction, text: str):
        user_id = interaction.user.id
        user_id_str = str(user_id)
        get_user_data(user_id)
        data_to_modify = load_data()
        user_data_node = data_to_modify.setdefault(user_id_str, {})
        if "sm_messages" not in user_data_node or not isinstance(user_data_node["sm_messages"], list):
            user_data_node["sm_messages"] = []
        user_data_node["sm_messages"].append(text)
        save_data(data_to_modify)
        await interaction.response.send_message("문장 추가했어^^ 개패주는 미소 bot 출동,", ephemeral=True)

    @sm_group.command(name="play", description="미소와의 sm플레이♡")
    async def sm_play_command(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        username = interaction.user.display_name
        default_messages = [
            "아이 ㅅㅂ!!!! 할일해", f"{username} 독촉하기 위해서는 sm 입사해야 함.",
            "놉놉. 안됀는것은안돼는것. (네 눈앞에 검지손가락을 가져다되고 흔들며)"
        ]
        image_files = ["smmiso.PNG"] # 파일 경로 Replit 환경에 맞게 확인 (예: 'cogs/smmiso.PNG' 또는 절대경로)
        user_data = get_user_data(user_id)
        custom_messages = user_data.get("sm_messages", [])
        all_possible_choices = default_messages + custom_messages
        if image_files:
             all_possible_choices.append("__image__")

        if not all_possible_choices:
            await interaction.response.send_message("놉놉. 안됀는것은안돼는것.(아무것도 없 딘)", ephemeral=True)
            return

        chosen_item = random.choice(all_possible_choices)
        if chosen_item == "__image__":
            try:
                await interaction.response.send_message(file=discord.File(image_files[0]))
            except FileNotFoundError:
                print(f"놉놉. 안됀는것은안돼는것.(파일 경로 오류)")
                await interaction.response.send_message("놉놉. 안됀는것은안돼는것.(파일 찾을 수 없음).", ephemeral=True)
            except Exception as e:
                print(f"이미지 전송 오류 '{image_files[0]}': {e}")
                await interaction.response.send_message("놉놉. 안됀는것은안돼는것.(이미지 전송 오류)", ephemeral=True)
        else:
            await interaction.response.send_message(chosen_item)

async def setup(bot: commands.Bot):
    await bot.add_cog(SmCog(bot))