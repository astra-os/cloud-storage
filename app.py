import gradio as gr
from uuid import uuid4
from fileManager import FileManager
import re

fileManager = FileManager()
fileManager.start()


def saveFile(file):
  with open(file.name, "rb") as rfile:
    file_infor = fileManager.saveFile(rfile.read(), file.orig_name)
  return f"https://astraos-nx-storage.hf.space/file=./{file_infor['path']}"


nxapp = gr.Interface(fn=saveFile, inputs="file", outputs="text")
nxapp.launch()