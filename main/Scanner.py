# _*_ coding:utf-8 _*_
import os
import json
import socket
import threading

from Logger import logger


class Scanner:

	def __init__(self):
		run_path = os.path.dirname(os.path.realpath(__file__)) + "\\"
		server_groups_conf = open(run_path + "web\\servers.json", "r", encoding="UTF-8")
		self.server_groups = json.loads(server_groups_conf.read())

		data_conf = open(run_path + "web\\data.json", "r", encoding="UTF-8")
		self.data = json.loads(data_conf.read())
		self.data['type'] = "DATA"

	def scan(self, host, port, flag):
		try:
			s = socket.socket()
			s.settimeout(1)
			code = s.connect_ex((host, port))
			s.close()
			if code == 0:
				self.data['data'].append({
					'flag': flag,
					'status': 'OPEN'
				})
				logger.info('[+] ' + host + ':' + str(port) + ' is OPEN')
			else:
				self.data['data'].append({
					'flag': flag,
					'status': 'CLOSE'
				})
				logger.warning('[-] ' + host + ':' + str(port) + ' CLOSE')
				logger.error('Connect to ' + host + ':' + str(port) + ' fail. Code: ' + str(code))
		except Exception as e:
			logger.error(str(e))

	def run(self):
		logger.info('The scanner is start')
		threads = []
		for group in self.server_groups:
			servers = self.server_groups[group]
			for server in servers:
				t = threading.Thread(target=self.scan, args=(server['host'], server['port'], server['flag']))
				threads.append(t)
				t.start()

		for t in threads:
			t.join()  # 在子线程完成运行之前，这个子线程的父线程将一直被阻塞。

		data = json.dumps(self.data)
		self.data['data'] = []
		logger.info('The scanner is complete')

		return data
