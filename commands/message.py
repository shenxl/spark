import socks
import socket
import os
from itertools import chain

from .executor import CommandStrategy
from logs.logger import Logger
from conf.config import get_config
from app.user import  User,UserMode
from .chat_normal import normalChat
from .chat_arts import artsChat
from .chat_files import filesChat

from langchain.chat_models import PromptLayerChatOpenAI
import promptlayer

from logs.logger import Logger


# 设置日志
logger = Logger(__name__)

env = os.environ.get('ENV')
if env != 'prod':
    logger.info("非生产环境，启动代理")
    # 设置代理
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8889'
    # 设置 Socks 代理 访问 firebase (调试中需要)
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", port=1089)
    os.environ["OPENAI_API_KEY"] = get_config().OPENAI_API_KEY
    socket.socket = socks.socksocket

promptlayer.api_key =get_config().PROMPTLAYER_KEY   


# 设置日志
logger = Logger(__name__)

class MessageCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        user = User.get_user(robot.user_id)
        if command_arg == "":
            User.init(robot.user_id)
            User.clear_redis(robot.user_id)
            
            message = {
                "msgtype": "markdown",
                "content": "用户状态初始化完成"
            }
            return (message , None)
        
        if user.mode == UserMode.NORMAL:
            memory_key = f"{robot.user_id}_chat_history"
            # chat = PromptLayerChatOpenAI(model_name="gpt-4-0314",temperature=0.9, pl_tags=[robot.user_id,"woa_gpt4_chat"])
            chat = PromptLayerChatOpenAI(temperature=0.9, pl_tags=[robot.user_id,"woa_chat"])
            answer = normalChat(command_arg,memory_key=memory_key,chat=chat)
            
        if user.mode == UserMode.ARTS:
            memory_key = f"{robot.user_id}_{user.arts_role}_history"
            chat = PromptLayerChatOpenAI(temperature=0.9, pl_tags=[robot.user_id,user.arts_role,"woa_chat"])
            answer = artsChat(command_arg,user=user,memory_key=memory_key,chat=chat)
        
        if user.mode == UserMode.FILE:
            chatllm = PromptLayerChatOpenAI(temperature=0.5, pl_tags=[robot.user_id,user.file_name,"woa_chat"])
            answer = filesChat(command_arg,user=user,chatllm=chatllm)
        
        message = {
            "msgtype": "markdown",
            "content": answer
        }
        return (message , None)
