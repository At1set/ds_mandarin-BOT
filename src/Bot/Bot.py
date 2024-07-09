import discord
from discord.ext import commands
from discord.ext.commands import Context
import json

intents = discord.Intents.all()


bot = commands.Bot(command_prefix='!', intents=intents)


def is_allowed_chatId():
  def predicate(ctx : Context):
    return ctx.channel.id == 764437873658953739
  return commands.check(predicate)


@bot.event
async def on_ready():
  print("Bot is started!")


@bot.command()
@is_allowed_chatId()
async def ping(ctx : Context):
  await ctx.send("Pong!")


@ping.error  # Обработчик ошибок для команды ping
async def ping_error(ctx, error):
  if isinstance(error, commands.CheckFailure):
    await ctx.send('This command can be used only in the allowed channel.')
  else:
    raise error  # Передаем обработку других ошибок вышестоящим обработчикам


async def update_config(data, websocket):
  id, data = data["id"], data["data"]
  print("Bot is updating config's data")
  status = "ok"
  newOptions = None
  try:
    with open("./src/options.json", "r") as file:
      options = json.load(file)
      with open("./src/options.json", "w") as file:
        options[f"{id}"] = data
        newOptions = options
        json.dump(options, file, indent=2, ensure_ascii=False)
  except Exception as err:
    print(err)
    status = "error"
  finally:
    await websocket.send(json.dumps({
      "id": id,
      "data": {
        "status": status,
        "message": newOptions[f"{id}"] if status != "error" else "Бот не смог применить текущие настройки!",
      }
    }))
