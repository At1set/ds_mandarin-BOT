import websockets
import asyncio
import json
from Bot import update_config, get_config

async def startWsConnection(limit=3):
  if (limit <= 0): raise Exception("Превышено максимальное колличество переподключений к серверу!")

  try:
    async with websockets.connect('ws://localhost:8000') as websocket:
      limit = 3
      print(await websocket.recv()) # Приветственное сообщение

      while True: # Получение новых настроек для серверов
        response = await websocket.recv()
        response = json.loads(response)
        print(response["action"])
        if response["action"] == "update_config":
          await update_config(response, websocket)
        elif response["action"] == "get_config":
          await get_config(response, websocket)
  except Exception as err:
    print(err)
    print("Bot lost connection with server! Restarting the connection...")
    await asyncio.sleep(1)
    await startWsConnection(limit-1)