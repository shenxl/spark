# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from logs.logger import Logger

from app.replybot import replyBot

from commands.executor import CommandExecutor
from commands.parse import CommandType
from commands.executor import HelpCommandStrategy

logger = Logger(__name__)
executor = CommandExecutor()
executor.add_strategy(CommandType.HELP, HelpCommandStrategy(executor))

executor.set_instruction_desc(CommandType.HELP,"输入%help%, 显示所有指令列表。")
class Chat(Resource):
    def get(self, key):
        return {"result": "ok"}

    
    def post(self, key):
        # 获取请求数据
        data = request.json
        replybot = replyBot(data, key)
        content = replybot.content
        # # 执行策略
        (message, paylopad), status = executor.execute(replybot, content)
        replybot.reply(message)