import discord
from discord.ext import commands
from discord.ext.commands import Context
import json

from services.DataBase import DataBase

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)
dataBase = DataBase(
  bd_user="root",
  bd_password="",
  bd_host="localhost",
  bd_database="ds_mandarin_bot"
)


def is_allowed_chatId():
  def predicate(ctx : Context):
    return ctx.channel.id == 764437873658953739
  return commands.check(predicate)


async def printRoleMessage():
  channel = bot.get_channel(1251883923190059130)
  message = await channel.send("При добавлении предустановленных реакций на это сообщение, я выдам вам соответствующие роли!")
  reactions = "0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟".split()
  for reaction in reactions:
    await message.add_reaction(reaction)

  roles_message = "============ Получение ролей игр ============\n"
  for i, role in enumerate(getRoles()):
    roles_message += f"{i}) {role}\n"
  await channel.send(roles_message)


async def sendAllReactionRoles():
  print("Начинаю выдавать роли по сообщению.")
  channel = bot.get_channel(1251883923190059130)
  message = await channel.fetch_message(1272518907319549962)
  for reaction in message.reactions:
    async for user in reaction.users():
      if user.id == bot.user.id: continue
      role = getRoleFromEmoji(reaction.emoji)
      if role:
        print(f"Выдана {role}, для {user.name}")
        await user.add_roles(role)
  print("Я закончил выдачу ролей!")


@bot.event
async def on_ready():
  print("Bot is started!")
  # await sendAllReactionRoles()

  # channel = bot.get_channel(1251883923190059130)
  # message = await channel.fetch_message(1272518933555183656)
  # await message.edit(content=message.content + "\n7) Minecraft")
  
  

import sys

@bot.event
async def on_error(event, *args, **kwargs):
  print(event)
  print(sys.exc_info())

def getRoles():
  roles_id = [1251864962356215849, 1260145881705877536, 1197120086419447878, 1251864196237230090, 1251864798174646303, 1251878642879823984, 1251875809548046409, 1275573808018751629]
  roles = []
  guild = bot.get_guild(761604207680946176)
  for role_id in roles_id:
    roles.append(guild.get_role(role_id))
  return roles


def getRoleFromEmoji(emoji):
  reactions = "0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟".split()
  index = None
  try:
    index = reactions.index(str(emoji))
    return getRoles()[index]
  except:
    return


@bot.event
async def on_raw_reaction_add(payload : discord.RawReactionActionEvent):
  if bot.user.id == payload.user_id: return print("Бот реагирует")
  if payload.message_id == 1272518907319549962:
    role = getRoleFromEmoji(emoji=payload.emoji)
    if not role: return print("Не удалось получить роль :(")
    print(f"Пользователь {payload.member.global_name} {payload.member.name} получил роль {role}!")
    await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload : discord.RawReactionActionEvent):
  if bot.user.id == payload.user_id: return print("Бот реагирует")
  if payload.message_id == 1272518907319549962:
    member = bot.get_guild(payload.guild_id).get_member(payload.user_id)
    role = getRoleFromEmoji(emoji=payload.emoji)
    if not role: return print("Не удалось получить роль :(")
    print(f"Пользователь {member.global_name} {member.name} убрал роль {role}!")
    await member.remove_roles(role)


@bot.event
async def on_guild_join(guild):
  print(f'Bot has joined the guild: {guild.name} (id: {guild.id})')
  guildObject = await dataBase.guilds.getGuild(guild.id)
  if guildObject["data"]: print(await dataBase.guilds.changeGuild(guild.id, "is_Bot", 1))
  else: print(await dataBase.guilds.addGuild(guild.id, True))


@bot.event
async def on_guild_remove(guild):
  print(f'Bot has been removed from the guild: {guild.name} (id: {guild.id})')
  await dataBase.guilds.removeBot(guild.id)


def is_module_active(module_name):
  async def predicate(ctx : Context):
    result = await dataBase.guilds.isModule(ctx.guild.id, module_name)
    return bool(result["data"])
  return commands.check(predicate)


@bot.command()
@is_module_active("auto_moderation")
async def ping(ctx : Context):
  await ctx.send("Pong!")


@ping.error  # Обработчик ошибок для команды ping
async def ping_error(ctx, error):
  if isinstance(error, commands.CheckFailure):
    # await ctx.send('This command can be used only in the allowed channel.')
    await ctx.send('auto_moderation module is not active')
  else:
    raise error  # Передаем обработку других ошибок вышестоящим обработчикам


async def get_config(data, websocket):
  print("get_config, data: ", data)
  id = data["id"]
  status = "ok"
  message = None
  try:
    await dataBase.guilds.addGuild(id)
    response = await dataBase.optionsStore.getOptions(id, "auto_moderation")
    if (response["error"]): raise response["error"]
    message = response["data"]
  except Exception as err:
    print(err)
    status = "error"
  finally:
    print(1)
    await websocket.send(json.dumps({
      "id": id,
      "data": {
        "status": status,
        "message": message if status == "ok" else "Бот не смог прочитать настройки!",
      }
    }))


async def update_config(data, websocket):
  print("Bot is updating config's, data: ", data)
  id, data = data["id"], data["data"]
  status = "ok"
  message = None
  try:
    response = await dataBase.optionsStore.updateOptions(id, "auto_moderation", data)
    print(response)
    if (response["error"]): raise response["error"]
    message = response["data"]
  except Exception as err:
    print(err)
    status = "error"
  finally:
    await websocket.send(json.dumps({
      "id": id,
      "data": {
        "status": status,
        "message": message if status != "error" else "Бот не смог применить текущие настройки!",
      }
    }))


async def getUserGuilds(data, websocket):
  print("getUserGuilds, data: ", data)
  id, guilds = data["id"], data["data"]
  status = "ok"
  message = None
  try:
    userResultGuilds = []
    for guild_id in guilds:
      response = await dataBase.guilds.getGuild(guild_id)
      if (response["error"]): raise response["error"]
      guild = response["data"]

      if (not guild): guild = {"isBot": 0}
      userResultGuilds.append(guild)
    
    userResultGuilds = list(map(lambda guild: bool(guild["isBot"]), userResultGuilds))
    message = userResultGuilds
  except Exception as err:
    print(err)
    status = "error"
  finally:
    await websocket.send(json.dumps({
      "id": id,
      "data": {
        "status": status,
        "message": message if status != "error" else "Боту не удалось прочитать/инициализировать гильдии пользователя!",
      }
    }))

import asyncio

@bot.event
async def on_message(message : discord.Message):
  if message.author == bot.user:
    return
  options = await dataBase.optionsStore.getOptions(761604207680946176, "auto_moderation")
  banwords = options["data"]["banwords"]
  for banword in banwords:
    if banword in message.content:
      await message.delete()
      message = await message.channel.send("Ваше сообщение я удалил НАХУЙ, т.к. в нем присуствует БАНворд!")
      await asyncio.sleep(3)
      await message.delete()