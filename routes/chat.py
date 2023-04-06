# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource
from logs.logger import Logger

from app.replybot import replyBot

from commands.executor import CommandExecutor
from commands.parse import CommandType
from commands.executor import HelpCommandStrategy, UnknownCommandStrategy
from commands.message import MessageCommandStrategy
from commands.arts import ArtsCommandStrategy,ArtsSetCommandStrategy
from commands.files import FilesInitCommandStrategy,FilesCommandStrategy

logger = Logger(__name__)

# 策略模式，根据不同的指令，执行不同的策略
executor = CommandExecutor()
executor.add_strategy(CommandType.HELP, HelpCommandStrategy(executor))
executor.add_strategy(CommandType.MSG, MessageCommandStrategy())
executor.add_strategy(CommandType.UNKNOWN, UnknownCommandStrategy())
executor.add_strategy(CommandType.ARTS, ArtsCommandStrategy())
executor.add_strategy(CommandType.ARTS_SET, ArtsSetCommandStrategy())
executor.add_strategy(CommandType.FILES, FilesCommandStrategy())
executor.add_strategy(CommandType.FILES_INIT, FilesInitCommandStrategy())

# 策略描述，用于帮助信息
executor.set_instruction_desc(CommandType.HELP,"输入%help%, 显示所有指令列表。")
executor.set_instruction_desc(CommandType.ARTS,"输入%arts%, 显示「角色」卡片。")
executor.set_instruction_desc(CommandType.ARTS_SET,"输入%arts set xx%, 设置指定的角色。")
executor.set_instruction_desc(CommandType.FILES,"输入%files%, 显示「文档」卡片。")
executor.set_instruction_desc(CommandType.FILES_INIT,"输入%files init xx%, 传递相应文档ID,进行初始化。")
executor.set_instruction_desc(CommandType.FILES_ASK,"输入%files ask xx%, 基于文档上下文进行问答，xx为文档ID，可选。")
class Chat(Resource):
    def get(self, key):
        return {"result": "ok"}

    
    def post(self, key):
        # 获取请求数据
        data = request.json
        replybot = replyBot(data, key)
        content = replybot.content
        # # 执行策略
        (message, paylopad) = executor.execute(replybot, content)
        if message is not None:
            return replybot.reply(message)
        