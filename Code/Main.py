import discord
from pymongo import MongoClient
from discord.ext import commands

token = 'PUT YOUR TOKEN HERE'
PREFIX = '!' # 봇의 접두사, default = !

server = MongoClient("localhost", 27017)
collections = server["MainData"]["Users"]
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("The bot is ready.")

def autoRegister(id):
    try:
        temp = collections.find_one({}, {'_id': 0})[f'{id}']
    except TypeError:
        collections.update_one({}, {"$set": {f'{id}': 0}}, upsert=True)
        return

def userCheck(index):
    if len(index) != 21 and len(index) != 18:
        return "> 유저 태그(멘션)이 잘못되었습니다."
    if len(index) == 21 and "<@" in str(index):
        return index[2:-1]
    else:
        return index

def intCheck(index):
    try:
        index = int(index)
    except TypeError:
        return "> 숫자로 입력해주세요."
    else:
        return True

@bot.command(aliases=['vhdlsxmwlrmq'])
async def 포인트지급(ctx, arg=None, value=None):
    autoRegister(ctx.author.id)
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("> 관리자 명령어입니다.", reference=ctx.message, mention_author=False)
        return
    if arg is None and value is None:
        await ctx.send("> 명령어 형식이 잘못되었습니다. `(명령어 도움말: !포인트지급 <@유저> <수량>)`")
    id = userCheck(arg)
    if len(id) != 18:
        await ctx.send(id, reference=ctx.message, mention_author=False)
        return
    user = await bot.fetch_user(id)
    temp = intCheck(value)
    if type(temp) is bool:
        data = collections.find_one({}, {'_id': 0})[f'{user.id}']
        data += int(value)
        collections.update_one({}, {"$set": {f'{user.id}': data}})
        await ctx.send(f"> 성공적으로 `{user.name}`님께 `{format(value, ',')}`포인트를 지급했습니다.", reference=ctx.message, mention_author=False)
    else:
        await ctx.send(temp, reference=ctx.message, mention_author=False)

@bot.command(aliases=['vhdlsxm', 'point', 'points'])
async def 포인트(ctx, arg=None):
    autoRegister(ctx.author.id)
    if arg is None:
        await ctx.send(f"> 현재 `{ctx.author.name}`님께서 보유중인 포인트는 `{format(collections.find_one({}, {'_id': 0})[f'{ctx.author.id}'], ',')}` 입니다.", reference=ctx.message, mention_author=False)
        return
    else:
        id = userCheck(arg)
        if len(id) != 18:
            await ctx.send(f"> 명령어 도움말 `(!포인트 <@유저>)`", reference=ctx.message, mention_author=False)
            return
        user = await bot.fetch_user(id)
        await ctx.send(f"> 현재 `{user.name}`님께서 보유중인 포인트는 `{format(collections.find_one({}, {'_id': 0})[f'{user.id}'], ',')}` 입니다.", reference=ctx.message, mention_author=False)
        return

@bot.command(aliases=['ranking', 'rank', 'tnsdnl', '포인트순위', 'vhdlsxmtnsdnl'])
async def 순위(ctx):
    autoRegister(ctx.author.id)
    arr = list()
    for i in collections.find({}, {'_id': 0}):
        for i in i.items():
            arr.append([int(i[0]), i[1]])
    if len(arr) >= 2:
        arr.sort(key=lambda x: -x[1])
    embed=discord.Embed(color=0x2f3136, title=f"포인트 순위")
    cnt = 1
    for i in arr:
        temp = await bot.fetch_user(i[0])
        embed.add_field(name=f"{cnt}등. {temp.name}", value=f"{format(i[1], ',')} Points", inline=False)
        cnt += 1
        if cnt == 10:
            break
    await ctx.send(embed=embed)

bot.run(token)
