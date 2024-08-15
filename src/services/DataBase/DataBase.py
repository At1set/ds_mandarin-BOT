import json
import mysql.connector

class DataBase():
  def __init__(self, bd_user, bd_password, bd_host, bd_database) -> None:
    self.bd_user = bd_user
    self.bd_password = bd_password
    self.bd_host = bd_host
    self.bd_database = bd_database
    self.guilds = Guilds(self)
    self.optionsStore = OptionsStore(self)
  
  async def execute_query(self, query, params=None, isNeedFetch=False):
    result = {
      "error": None,
      "data": None
    }
    try:
      connect = mysql.connector.connect(user=self.bd_user, password=self.bd_password, host=self.bd_host, database=self.bd_database, charset="utf8mb4")
      cursor = connect.cursor()
      cursor.execute(query, params)
      if isNeedFetch:
        result["data"] = cursor.fetchall()
      connect.commit()
    except mysql.connector.Error as error:
      print(f"Error: {error}")
      if connect.is_connected():
        connect.rollback()
      result["error"] = error
    finally:
      cursor.close()
      connect.close()
      return result


class Guilds():
  def __init__(self, __dataBase__) -> None:
    self.__dataBase__ = __dataBase__
  
  async def addGuild(self, guild_id, isBot=False):
    query = """INSERT IGNORE INTO guilds (id) VALUES (%s)"""
    if (isBot): query = """INSERT IGNORE INTO guilds (id, is_bot) VALUES (%s, 1)"""
    result = await self.__dataBase__.execute_query(query, params=[guild_id])
    if (result["error"]): return result
    return await self.getGuild(guild_id)

  async def getGuild(self, guild_id):
    query = """SELECT * FROM guilds WHERE id = %s;"""
    result = await self.__dataBase__.execute_query(query, params=[guild_id], isNeedFetch=True)
    if (len(result["data"])):
      id, isBot, auto_moderation = list(result["data"][0])
      result["data"] = {
        "id": id,
        "isBot": isBot,
        "auto_moderation": auto_moderation
      }
    return result

  async def getGuilds(self):
    query = """SELECT * FROM guilds;"""
    return await self.__dataBase__.execute_query(query, isNeedFetch=True)
  
  async def isBotGuild(self, guild_id):
    query = """SELECT COUNT(1) FROM guilds WHERE id = (%s);"""
    result = await self.__dataBase__.execute_query(query, params=[guild_id], isNeedFetch=True)
    if (result["data"]): result["data"] = result["data"][0][0] > 0
    return result

  async def removeBot(self, guild_id):
    query = """UPDATE guilds SET is_bot = 0 WHERE id = (%s);"""
    return await self.__dataBase__.execute_query(query, params=[guild_id])
  
  async def changeGuild(self, guild_id, module_name, value):
    query = f"""UPDATE guilds SET {module_name} = {value} WHERE id = (%s);"""
    return await self.__dataBase__.execute_query(query, params=[guild_id])
  
  async def isModule(self, guild_id, module_name):
    query = f"""SELECT {module_name} FROM guilds WHERE id = %s;"""
    result = await self.__dataBase__.execute_query(query, params=[guild_id], isNeedFetch=True)
    if (result["data"]): result["data"] = bool(result["data"][0][0])
    print(result)
    return result


class OptionsStore():
  def __init__(self, __dataBase__) -> None:
    self.__dataBase__ = __dataBase__
    self._defaultOptions = {
      "auto_moderation": {"testFunc": False, "secondSwitch": False, "Menu_select": 1}
    }
  
  async def initOptions(self, guild_id, module_name):
    json_options = json.dumps(self._defaultOptions[module_name])
    query = f"""INSERT INTO guild_options (id, {module_name}) VALUES ({guild_id}, '{json_options}');"""
    print(query)
    result = await self.__dataBase__.execute_query(query)
    if (not result["error"]): result["data"] = self._defaultOptions[module_name]
    return result

  async def getOptions(self, guild_id, module_name):
    query = """SELECT * FROM guild_options WHERE id = %s;"""
    result = await self.__dataBase__.execute_query(query, params=[guild_id], isNeedFetch=True)
    if (result["error"]): return result

    if (result["data"]):
      result["data"] = json.loads(result["data"][0][1])
    else: # Инициализация настроек если их не существует
      result = await self.initOptions(guild_id, module_name)
    
    return result
  
  async def updateOptions(self, guild_id, module_name, options: object):
    json_options = json.dumps(options)
    query = f"""UPDATE guild_options SET {module_name} = '{json_options}' WHERE id = {guild_id};"""
    result = await self.__dataBase__.execute_query(query)
    if (not result["error"]): result["data"] = options
    return result


async def test():
  dataBase = DataBase(
    bd_user="root",
    bd_password="",
    bd_host="localhost",
    bd_database="ds_mandarin_bot"
  )

  guild = await dataBase.guilds.getGuild(761604207680946176)
  print(guild)
  if guild["data"]: print(await dataBase.guilds.changeGuild(guild.id, "is_Bot", 1))
  else: print(await dataBase.guilds.addGuild(guild.id, True))


if __name__ == "__main__":
  import asyncio
  asyncio.run(test())