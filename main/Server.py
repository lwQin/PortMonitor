# _*_ coding:utf-8 _*_
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.websocket import WebSocketHandler
import os
import json

from Logger import logger
from Scanner import Scanner
from Token import Token
from RestartServer import RestartServer


class Server(WebSocketHandler):

    users = set()  # 用来存放在线用户的容器
    scanner = Scanner()
    token_cls = Token()
    RestartServer = RestartServer()

    def open(self):
        logger.info("client " + self.request.remote_ip + " connected")
        self.users.add(self)  # 建立连接后添加用户到容器中

    def on_message(self, message):
        logger.info("Recive message: " + message)
        message = message.split('?s=')
        msg_type = message[0]
        if len(message) > 1:
            msg_info = message[1]

        if msg_type == "GET_DATA":
            data = self.scanner.run()

        if msg_type == "GET_TOKEN":
            data = self.token_cls.get_token(msg_info)

        if msg_type == "RESTART":
            data = self.RestartServer.run(msg_info, self)

        self.write_message(data)

    def on_close(self):
        logger.info("client " + self.request.remote_ip + " cloed")
        self.users.remove(self)  # 用户关闭连接后从容器中移除用户

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求


if __name__ == '__main__':
    run_path = os.path.dirname(os.path.realpath(__file__)) + "\\"
    config_json = open(run_path + "web\\config.json", "r", encoding="UTF-8")
    config = json.loads(config_json.read())

    app = tornado.web.Application([
        (r"/", Server)
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(config['server']['port'])
    tornado.ioloop.IOLoop.current().start()
