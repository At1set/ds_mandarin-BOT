from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio


class ConfigHandler(FileSystemEventHandler):
  def __init__(self, observerFilePath, loop):
    self.observerFilePath = observerFilePath
    self.pool = []
    self.curent_loop = loop
    self.lastFileContent = ""
    with open(observerFilePath, "r") as file:
      self.lastFileContent = file.read()
  

  def fileContentModified(self):
    with open(self.observerFilePath, "r") as file:
      fileContent = file.read()
    result = self.lastFileContent != fileContent
    self.lastFileContent = fileContent
    return result


  def on_modified(self, event):
    if event.is_directory or event.src_path != f'{self.observerFilePath}'\
    or not self.fileContentModified():
      return
    
    print(f'{self.observerFilePath.split("/")[-1]} file modified')
    for function in self.pool:
      asyncio.run_coroutine_threadsafe(function(), loop=self.curent_loop)
  

  def Subscribe(self, function):
    return self.pool.append(function)
  

  def Unsubscribe(self, function):
    if (not function in self.pool): return
    try:
      self.pool.remove(function)
    except:
      pass