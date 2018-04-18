# _*_ coding:utf-8 _*_
import os
import json
import time
import hmac
import base64

from Logger import logger


class Token:
	tokens = {}

	def __init__(self):
		run_path = os.path.dirname(os.path.realpath(__file__)) + "\\"
		server_groups_conf = open(run_path + "web\\servers.json", "r", encoding="UTF-8")
		server_groups = json.loads(server_groups_conf.read())

		for group in server_groups:
			servers = server_groups[group]
			for server in servers:
				self.tokens[server['flag']] = ''

		data_conf = open(run_path + "web\\data.json", "r", encoding="UTF-8")
		self.data = json.loads(data_conf.read())
		self.data['type'] = "TOKEN"

	def get_token(self, message):
		flag = message
		self.data['data'] = {'flag': '', 'token': ''}
		self.data['data']['flag'] = flag

		if self.tokens[flag] == '':
			self.data['data']['token'] = self.tokens[flag] = self.generate(flag)
		elif self.certify(flag, self.tokens[flag]) != True:
			self.data['data']['token'] = self.tokens[flag] = self.generate(flag)
		else:
			self.data['data']['token'] = self.tokens[flag]

		logger.info('token: ' + str(self.tokens))
		data = json.dumps(self.data)
		self.data['data']['token'] = {}
		return data

	def token_certify(self, flag, token):
		return self.certify(flag, token)

	def generate(self, key, expire=120):
		ts_str = str(time.time() + expire)
		ts_byte = ts_str.encode("utf-8")
		sha1_tshexstr = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
		token = ts_str + ':' + sha1_tshexstr
		b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
		return b64_token.decode("utf-8")

	def certify(self, key, token):
		token_str = base64.urlsafe_b64decode(token).decode('utf-8')
		token_list = token_str.split(':')
		if len(token_list) != 2:
			return False
		ts_str = token_list[0]
		if float(ts_str) < time.time():
			logger.warning('token已过期')
			return 1, 'token已过期'
		known_sha1_tsstr = token_list[1]
		sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
		calc_sha1_tsstr = sha1.hexdigest()
		if calc_sha1_tsstr != known_sha1_tsstr:
			logger.warning('token不一致')
			return 2, 'token不一致'

		return True
