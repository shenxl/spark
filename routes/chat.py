# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from logs.logger import Logger


logger = Logger(__name__)

class Chat(Resource):
    def get(self, key):
        return {"result": "ok"}

    
    def post(self, key):
        # 获取请求数据
        data = request.json
        logger.info("commit push for hook!")
        logger.info(data)
