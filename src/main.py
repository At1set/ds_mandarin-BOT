from Bot import bot
from services.WSServer import startWsConnection

import asyncio
import json


# import services.Logger


import os
from dotenv import load_dotenv


# читаем данные из файла config.json
with open('./src/config.json', 'r') as f:
  config_data = json.load(f)


load_dotenv()
TOKEN = os.getenv("TOKEN")


async def connect_to_server():
  loop = asyncio.get_event_loop()
  await loop.create_task(startWsConnection())


async def main():
  try:
    await asyncio.gather(
      connect_to_server(),
      bot.start(TOKEN)
    )
  except Exception as err:
    print(err)
    await bot.close()
  finally:
    print("Бот остановил свою работу!")


class StartingMode():
  Developing = 1
  Production = 2


start_mode = StartingMode.Developing


if __name__ == "__main__":
  if (start_mode == StartingMode.Production): asyncio.run(main())
  elif (start_mode == StartingMode.Developing) : asyncio.run(bot.start(TOKEN))
  