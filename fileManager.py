from threading import Thread
from copy import deepcopy
from uuid import uuid4
from time import sleep
import json
import time
import re
import os


def syncmethod(func):
  def function(*args, **kwargs):
    th = Thread(target=func, args=args, kwargs=kwargs)
    th.start()
  return function


@syncmethod
def interval(fc, time):
  while True:
    sleep(time)
    fc()




class FileManager:
	def __init__(self):
		super(FileManager, self).__init__()
		self.data_file = "collector_data.json"
		# self.base_url = "http://localhost:7860"
		self.base_url = "https://astraos-nx-storage.hf.space"
		if not os.path.exists(self.data_file): self.writeJson()
		else: self.checkFiles()


	def formatPath(self, path):
	  new_path = re.sub(r'\s+|\s', '-', path)
	  new_path = re.sub(r'\!|\?|\#|\*|Ç|ç|ê|Ê|ã|Ã', '', new_path)
	  return new_path


	def rename(self, path, new_path):
		os.rename(path, new_path)


	def readJson(self, path):
		with open(path, 'r') as json_data:
			return json.load(json_data)


	def writeJson(self, data={}):
		data_file = open(self.data_file, "w")
		json.dump(data, data_file, indent=2)
		data_file.close()


	def start(self, gap=5):
		interval(self.checkFiles, gap * 60)


	def checkFiles(self):
		data_file = self.readJson(self.data_file)
		for idx, file_infor in enumerate(deepcopy(data_file)):
			if file_infor["expiresAt"] < time.time():
				try:
					os.remove(file_infor["path"])
				except Exception as e:
					print(e)
				del data_file[idx]
		self.writeJson(data=data_file)


	def reValidate(self, path, expiresAt=60):
		data_file = self.readJson(self.data_file)
		for file_infor in data_file:
			if file_infor["path"] == path:
				file_infor["expiresAt"] = time.time() + (expiresAt * 60)
		self.writeJson(data=data_file)


	def addPath(self, path, expiresAt=60):
		new_path = self.formatPath(path)
		self.rename(path, new_path)
		data_file = self.readJson(self.data_file)
		fc = lambda file_infor: file_infor["path"] != new_path
		data_file = list(filter(fc, data_file))
		new_file_infor = {
			"path": new_path,
			"filename": new_path.split("/")[-1],
			"id": str(uuid4()),
			"expiresAt": time.time() + (expiresAt * 60) # + 30 minutes
		}
		data_file.append(new_file_infor)
		self.writeJson(data=data_file)
		return new_file_infor


	def hasFile(self, path):
		path = self.formatPath(path)
		data_file = self.readJson(self.data_file)
		for file_infor in data_file:
			if file_infor["path"] == path:
				self.reValidate(path)
				return True


	def saveFile(self, data, filename):
		filename = self.formatPath(filename)
		file_path = f"fl/{str(uuid4())}_{filename}"
		with open(file_path, "wb") as file:
			file.write(data)
		return self.addPath(file_path)


	def getFileObjByPath(self, path):
		path = self.formatPath(path)
		data_file = self.readJson(self.data_file)
		for file_infor in data_file:
			if file_infor["path"] == path:
				self.reValidate(path)
				return file_infor


	def getFileObjById(self, uid):
		data_file = self.readJson(self.data_file)
		for file_infor in data_file:
			if file_infor["id"] == uid:
				self.reValidate(file_infor["path"])
				return file_infor


	def getFileById(self, uid):
		file_path = self.getFilePathById(uid)
		if not file_path: return
		with open(file_path, "rb") as file:
			file_data = file.read()
		return file_data


	def getFileUrlById(self, uid):
		file_path = self.getFilePathById(uid)
		if not file_path: return
		return self.getFileUrlByPath(file_path)


	def getFileUrlByPath(self, path):
		return f"{self.base_url}/file=./{path}"
