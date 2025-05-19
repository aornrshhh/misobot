import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import datetime
import json
import os


# ==== 설정 ====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "misobot_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# ==== 헬퍼 함수 ====
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_data(user_id):
    data = load_data()
    return data.setdefault(str(user_id), {
        "dday": None,
        "todo": [],
        "done": [],
        "timers": {},
        "today": {}
    })

# ==== 슬래시 명령어 ====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} 슬래시 명령어 등록 완료!")

@bot.tree.command(name="dday", description="디데이 설정하기♡")
@app_commands.describe(title="디데이 제목", date="날짜 (YYYY-MM-DD)")
async def dday_command(interaction: discord.Interaction, title: str, date: str):
    try:
        dday_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        await interaction.response.send_message("날짜 형식이 잘못됐어ㅠㅅㅠ YYYY-MM-DD 형식으로 입력해줄래?", ephemeral=True)
        return

    data = load_data()
    user_data = get_user_data(interaction.user.id)
    user_data["dday"] = {"title": title, "date": date}
    data[str(interaction.user.id)] = user_data
    save_data(data)

    delta = (dday_date - datetime.date.today()).days
    await interaction.response.send_message(f" 디데이 '{title}' 설정 완료했어૮꒰⸝⸝> ·̫ <⸝⸝꒱ა⋆⸜ D-{delta}♡")

@bot.tree.command(name="todo", description="투두 관리하기♡")
@app_commands.describe(action="투두 추가는 1, 투두 완료는 2, 투두 보기는 3을 입력해줘♡", content="할 일을 추가하려면 '할일 이름'을 써줘. 완료 체크하려면 할 일의 번호를 알려줘! action에 2를 누르면 몇 번인지 확인할 수 있어o(^o^)o")
async def todo_command(interaction: discord.Interaction, action: str, content: str = None):
    data = load_data()
    user_data = get_user_data(interaction.user.id)

    if action == "1" and content:
        user_data["todo"].append(content)
        response = f"해야 할 일이 생겼어(~ ᵕ   ̫  ᵕ)~: {content}"
    elif action == "3":
        if not user_data["todo"]:
            response = "할 일이 없어!(먹바눕 시킨다)"
        else:
            username = interaction.user.display_name
            response = f"{username}의 투두리스트♡:\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(user_data["todo"])])
    elif action == "2" and content and content.isdigit():
        idx = int(content) - 1
        if 0 <= idx < len(user_data["todo"]):
            done = user_data["todo"].pop(idx)
            user_data["done"].append(done)
            response = f"완료! 수고했어 ('ω')三( ε: )三(.ω.)三( :3 )三('ω'): {done}"
        else:
            response = "헐! 이 번호의 할 일이 없어! 다시 체크하시오ㅡ3ㅡ"
    else:
        response = "“ 놉놉. ”  “ 안됀는것은안돼는것. ” (네 눈앞에 검지손가락을 가져다되고 흔들며) (잘몬된 명령이야!)"

    data[str(interaction.user.id)] = user_data
    save_data(data)
    await interaction.response.send_message(response)

@bot.tree.command(name="timer", description="타이머 시작하기♡")
@app_commands.describe(todo="할일 리스트의 번호를 입력하면 그 일을 얼마나 했는지 잴 수 있어! 아무것도 안 쓰면 그냥 카운트할게>3<")
async def timer_command(interaction: discord.Interaction, todo: str = None):
    data = load_data()
    user_data = get_user_data(interaction.user.id)

    if user_data["timers"].get("running"):
        await interaction.response.send_message("이미 타이머가 작동 중이야! /finish로 종료해줘!", ephemeral=True)
        return

    label = "자유공부"
    if todo and todo.startswith("todo:"):
        idx = int(todo.split(":")[1]) - 1
        if 0 <= idx < len(user_data["todo"]):
            label = user_data["todo"][idx]
    elif todo:
        label = todo

    now = datetime.datetime.now().isoformat()
    user_data["timers"] = {"start": now, "label": label, "total": 0, "running": True}
    data[str(interaction.user.id)] = user_data
    save_data(data)

    message = await interaction.response.send_message("⏱️ 경과 시간: 00:00:00")

    async def update_timer():
        while user_data["timers"].get("running"):
            now = datetime.datetime.now()
            elapsed = now - datetime.datetime.fromisoformat(user_data["timers"]["start"])
            seconds = int(elapsed.total_seconds())
            h, m = divmod(seconds, 3600)
            m, s = divmod(m, 60)
            formatted = f"{h:02}:{m:02}:{s:02}"
            try:
                await message.edit(content=f"⏱️ 경과 시간: {formatted}")
            except Exception as e:
                print("메시지 수정 실패:", e)
            await asyncio.sleep(10)

    bot.loop.create_task(update_timer())

@bot.tree.command(name="stop", description="타이머 정지")
@bot.tree.command(name="smadd", description="스마일 문장 추가하기")
@app_commands.describe(text="추가할 문장")
async def smadd_command(interaction: discord.Interaction, text: str):
    data = load_data()
    user_data = get_user_data(interaction.user.id)
    user_data.setdefault("sm_messages", []).append(text)
    data[str(interaction.user.id)] = user_data
    save_data(data)
    await interaction.response.send_message("문장 추가했어!")

@bot.tree.command(name="smplay", description="미소와의 sm플레이♡")
async def smplay_command(interaction: discord.Interaction):
    username = interaction.user.display_name
    import random
    messages = [
        "아이 ㅅㅂ!!!! 할일해"
        f"{username} 독촉하기 위해서는 sm 입사해야 함."
        "<:sm_s:1373985901931135067>"
        "“ 놉놉. ”  “ 안됀는것은안돼는것. ” (네 눈앞에 검지손가락을 가져다되고 흔들며) “ 놉놉. ”  “ 안됀는것은안돼는것. ” (네 눈앞에 검지손가락을 가져다되고 흔들며) “ 놉놉. ”  “ 안됀는것은안돼는것“ 놉놉. ”  “ 안됀는것은안돼는것. ” (네 눈앞에 검지손가락을 가져다되고 흔들며) “ 놉놉. ”"
    ]
    data = load_data()
    user_data = get_user_data(interaction.user.id)
    custom = user_data.get("sm_messages", [])
    all_msgs = messages + custom
    await interaction.response.send_message(random.choice(all_msgs))
async def finish_command(interaction: discord.Interaction):
    data = load_data()
    user_data = get_user_data(interaction.user.id)
    timer = user_data["timers"]

    if not timer.get("running"):
        await interaction.response.send_message("진행 중인 타이머가 없어요.")
        return

    start_time = datetime.datetime.fromisoformat(timer["start"])
    end_time = datetime.datetime.now()
    duration = end_time - start_time
    seconds = int(duration.total_seconds())

    label = timer["label"]
    user_data["today"].setdefault(label, 0)
    user_data["today"][label] += seconds
    user_data["timers"] = {}

    data[str(interaction.user.id)] = user_data
    save_data(data)

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    await interaction.response.send_message("타이머 정지했어!")

bot.run(os.getenv("BOT_TOKEN"))
