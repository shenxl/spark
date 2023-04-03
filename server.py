# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api
from routes.chat import Chat

import socks
import socket
import os

from logs.logger import Logger
from conf.config import  get_config


# 设置日志
logger = Logger(__name__)

# 初始化 Flask 和 Flask-RESTful
app = Flask(__name__)
api = Api(app)

# 添加 Chat 资源到 Flask-RESTful
api.add_resource(Chat, '/chat', '/chat/<string:key>')

# 运行 Flask 应用
if __name__ == "__main__":

    app.run(debug=True)

