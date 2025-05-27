import discord
from discord.ui import View, Select # Button, Modal, TextInput 등 사용하지 않는 요소는 제거해도 됩니다.
from discord import SelectOption # app_commands는 여기서 직접 사용하지 않으므로 제거 가능

# utils에서 필요한 함수만 가져옵니다. 현재 DDay 관련 View에서는 load_data, save_data, get_user_data가 필요합니다.
from utils import load_data, save_data, get_user_data


# DDayDeleteSelect와 DDayDeleteView는 dday_cog.py에서 사용하므로 유지합니다.
class DDayDeleteSelect(Select):
    def __init__(self, options, user_id: int):
        super().__init__(placeholder="삭제할 디데이를 선택하시오 ㄟ( ▔ω▔ )ㄏ",
                         min_values=1, max_values=1, options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("너가 설정한 디데이가 아니야!", ephemeral=True)
            return

        idx = int(self.values[0])
        user_id_str = str(self.user_id)

        data_to_modify = load_data()
        # get_user_data를 호출하여 사용자 데이터가 없거나 dday 리스트가 없을 경우를 대비할 수 있으나,
        # dday_delete_command에서 이미 get_user_data를 호출하여 dday_list를 가져오므로, 여기서는 바로 접근합니다.
        user_data_node = data_to_modify.get(user_id_str)

        if user_data_node is None or not isinstance(user_data_node.get("dday"), list):
            await interaction.response.edit_message(
                content="오류: 디데이 데이터를 찾을 수 없습니다. 다시 시도해주세요.",
                view=None) # 오류 시 View 제거
            return

        dday_list = user_data_node["dday"]

        if 0 <= idx < len(dday_list):
            removed = dday_list.pop(idx) # 여기서 dday_list (즉, data_to_modify 내부) 직접 수정
            save_data(data_to_modify) # 수정된 data_to_modify 전체를 저장
            await interaction.response.edit_message(
                content=f"삭제 완료! ⁽⁽ଘ( ˙꒳˙ )ଓ⁾⁾`{removed['title']}` 사라졌어⋆｡°✩",
                view=None) # 성공 시 View 제거
        else:
            await interaction.response.edit_message(
                content="“ 놉놉. ”  “ 안됀는것은안돼는것. ” (오류: 삭제할 항목을 찾을 수 없음)",
                view=None) # 오류 시 View 제거

class DDayDeleteView(View):
    def __init__(self, options, user_id: int):
        super().__init__(timeout=60) # 60초 후 타임아웃
        self.user_id = user_id
        self.add_item(DDayDeleteSelect(options, self.user_id))
        self.message: discord.Message | None = None # View가 첨부된 메시지를 저장하기 위함

    async def on_timeout(self):
        # ephemeral 메시지는 timeout 시 수정이 어려울 수 있습니다.
        # 만약 non-ephemeral 메시지이고 self.message가 설정되었다면, 메시지 내용을 변경하고 View를 제거합니다.
        if self.message:
            try:
                await self.message.edit(content="선택 시간이 초과되었어! 명령어를 다시 입력해줘.", view=None)
            except (discord.NotFound, discord.HTTPException) as e:
                print(f"DDayDeleteView on_timeout에서 메시지 수정 실패: {e}")
                pass # 오류 발생 시 조용히 실패
        # ephemeral 메시지의 경우, 사용자가 직접 다시 명령어를 실행하도록 유도하는 것이 좋습니다.
        # 현재 dday_delete_command에서 ephemeral=True로 보내고 있으므로, on_timeout 시 메시지 수정이 안 될 수 있습니다.
        # 이 경우, on_timeout에서 특별한 동작을 하지 않거나, 로깅만 남길 수 있습니다.

# Todo 및 Timer 관련 UI 클래스들은 모두 삭제되었습니다.