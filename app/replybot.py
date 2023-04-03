# -*- coding: utf-8 -*-
import json
import requests
from typing import Dict

# from src.mocks.bots import mockBot
from conf.config import get_config
from logs.logger import Logger

# 设置日志
logger = Logger(__name__)
# mockbots = mockBot()

class replyBot:
    def __init__(self, data: Dict, key):
        self.chat_id = data.get("chatid")
        self.user_id = data.get("creator")
        self.content = data.get("content")
        self.robot_key = data.get("robot_key")
        self.url = data.get("url")
        self.ctime = data.get("ctime")
        self.hook_url = get_config().WOA_URL + key
    
    # 建立索引操作
    def __getitem__(self, key):
        return getattr(self, key, None)
    
    # 答复方法，需要针对不同的状态进行答复
    def reply(self, message): 
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Host":"xz.wps.cn",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }
        requests.post(self.hook_url, data=json.dumps(message), headers=header)
