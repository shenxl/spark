import socks
import socket
import os
from itertools import chain

from .executor import CommandStrategy
from logs.logger import Logger
from conf.config import  get_config
from app.user import  User,UserMode

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


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
chat = PromptLayerChatOpenAI(temperature=0.9, pl_tags=["woa_chat"])

# 设置日志
logger = Logger(__name__)
class MessageCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        user = User.get_user(robot.user_id)
        logger.info(f"Hello, user {user.id} ({user.status}, {user.mode})")
        if user.mode == UserMode.NORMAL:
            
            template="You are a helpful assistant to me."
            system_message_prompt = SystemMessagePromptTemplate.from_template(template)
            human_template="{text}"
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            reply = chat(chat_prompt.format_prompt(text=command_arg).to_messages())
            answer = reply.content
            
        if user.mode == UserMode.ARTS:
            template = user.arts_template
            ai_answer = user.arts_answer
            
            system_message = SystemMessage(content=template)
            example_ai = SystemMessage(content=ai_answer)
            human_template="{text}"
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
            chat_prompt = ChatPromptTemplate.from_messages([system_message, example_ai,human_message_prompt])
            reply = chat(chat_prompt.format_prompt(text=command_arg).to_messages())
            answer = text = f"""🥷**角色模式**： <font color='#e67700'>**`{user.arts_role}`**</font> \n\n{reply.content}"""
        message = {
            "msgtype": "markdown",
            "content": answer
        }
        return (message , None)
