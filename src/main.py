from Bot import bot, update_config
from services.Observer import Observer, ConfigHandler
import asyncio


# import services.Logger


import os
from dotenv import load_dotenv


import json


# читаем данные из файла config.json
with open('./src/config.json', 'r') as f:
  config_data = json.load(f)


load_dotenv()
TOKEN = os.getenv("TOKEN")


def registerObserver():
  current_directory = config_data['Observer']['current_directory']
  wathing_file = config_data['Observer']['wathingFile']

  loop = asyncio.get_event_loop()
  event_handler = ConfigHandler(fr"{wathing_file}", loop)
  def update_config(Url):
    global update_config
    return lambda: update_config(Url)
  port, updateConfigEndpoint  = config_data["BackendApi"]["port"], config_data["BackendApi"]["updateConfigEndpoint"]
  event_handler.Subscribe(update_config(f"http://localhost:{port}{updateConfigEndpoint}"))
  observer = Observer()
  observer.schedule(event_handler, path=fr'{current_directory}', recursive=False)
  observer.start()
  return observer


import websockets
import logging


async def startWsConnection(limit=3):
  if (limit <= 0): raise Exception("Превышено максимальное колличество переподключений к серверу!")

  global update_config
  try:
    async with websockets.connect('ws://localhost:8000') as websocket:
      limit = 3
      print(await websocket.recv()) # Приветственное сообщение

      while True: # Получение новых настроек для серверов
        response = await websocket.recv()
        response = json.loads(response)
        await update_config(response, websocket)
  except Exception as err:
    print(err)
    print("Bot lost connection with server! Restarting the connection...")
    await asyncio.sleep(1)
    await startWsConnection(limit-1)


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


if __name__ == "__main__":
  asyncio.run(main())