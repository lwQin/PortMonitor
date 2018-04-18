# _*_ coding:utf-8 _*_
import os
import logging
from logging.handlers import TimedRotatingFileHandler

run_path = os.path.dirname(os.path.realpath(__file__)) + "\\"
log_path = run_path + "logs\\"
if os.path.isdir(log_path) == 0:
	os.mkdir(run_path + "logs")

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d - %(levelname)s - %(message)s')

file_handler = TimedRotatingFileHandler(filename=log_path + "log", when="midnight", interval=1, backupCount=7, encoding="UTF-8")
file_handler.suffix = "%Y-%m-%d.txt"
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)
