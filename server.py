# -*- coding: utf-8 -*-
from flask import Flask, request, session
from flask_restful import Api
from routes.chat import Chat
from flask_session import Session

from datetime import timedelta
from uuid import uuid4
import redis

from logs.logger import Logger
from conf.config import  get_config


# 设置日志
logger = Logger(__name__)

# 初始化 Flask 和 Flask-RESTful
app = Flask(__name__)
app.secret_key = "chat_key_B4sG7hD6K8"

api = Api(app)
# 创建一个 Memcached 实例
redis_store = redis.Redis(host="127.0.0.1", port=6379)

# 设置 Flask-Session 的配置
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis_store

app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)

# 初始化 Flask-Session
Session(app)

# 添加 Chat 资源到 Flask-RESTful
api.add_resource(Chat, '/chat', '/chat/<string:key>')

# 运行 Flask 应用
if __name__ == "__main__":

    app.run(debug=True)

