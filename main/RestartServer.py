# _*_ coding:utf-8 _*_
import os
import json
import paramiko
import threading

from Token import Token
from Logger import logger


class RestartServer:
	token_cls = Token()

	def __init__(self):
		run_path = os.path.dirname(os.path.realpath(__file__)) + "\\"
		data_conf = open(run_path + "web\\data.json", "r", encoding="UTF-8")
		self.data = json.loads(data_conf.read())
		self.data['type'] = "RESTART"

		server_info_conf = open(run_path + "ServerInfo.json", "r", encoding="UTF-8")
		self.server_info = json.loads(server_info_conf.read())

	def restart(self, flag, token, websocket_server):
		hostname = self.server_info[flag]['host']
		port = self.server_info[flag]['port']
		username = self.server_info[flag]['username']
		password = self.server_info[flag]['password']
		cmd_path = self.server_info[flag]['cmd_path']
		log_path = self.server_info[flag]['log_path']

		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			restart_cmd = cmd_path + " > /dev/null"
			client.connect(hostname, port, username, password)
			client.exec_command(restart_cmd)

			log_cmd = "cat " + log_path
			stdin, stdout, stderr = client.exec_command(log_cmd)
			msg = ''
			for line in stdout:
				msg = line.strip("\n")
			self.data['code'] = 0
			self.data['msg'] = "success"
			self.data['data'] = "脚本执行成功 -- " + msg
		except Exception as e:
			logger.error(str(e))
			self.data['code'] = -1
			self.data['msg'] = "error"
			self.data['data'] = "脚本执行失败 -- " + str(e)
		client.close()

		logger.info(self.data['data'])
		websocket_server.write_message(json.dumps(self.data))

	def run(self, message, websocket_server):

		message = message.split('&t=')
		if len(message) == 1:
			self.data['code'] = -1
			self.data['message'] = 'error'
			self.data['data'] = '参数错误'
		else:
			flag, token = message[0], message[1]
			if token == '':
				self.data['code'] = -1
				self.data['message'] = 'error'
				self.data['data'] = '脚本执行失败 -- 缺少token'
			else:
				result = self.token_cls.token_certify(flag, token)
				if result != True:
					self.data['code'] = -1
					self.data['msg'] = "error"
					self.data['data'] = "脚本执行失败 -- " + result[1]
				else:
					t = threading.Thread(target=self.restart, args=(flag, token, websocket_server))
					t.start()
					self.data['msg'] = "run"
					self.data['data'] = "脚本执行中"

		logger.info(self.data['data'])
		return json.dumps(self.data)
