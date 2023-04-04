import socks
import socket
import os
from itertools import chain
import pandas as pd

from .executor import CommandStrategy
from logs.logger import Logger
from conf.config import  get_config

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
# logger.info(os.getcwd())
df = pd.read_csv('./acts.csv', encoding='gb2312', header=0)

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
class ArtsCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        # 当前bot的当前用户对话, 判断是否是以 act-> 开头
        user_id = robot["user_id"]
        message = {
            "msgtype": "text",
            "text": {
                "content": f"<at user_id=\"{user_id}\"></at>https://kdocs.cn/l/cgPpL1tqMyUe"
            }
        }
        return (message , None)
    


class ArtsSetCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        # 当前bot的当前用户对话, 判断是否是以 act-> 开头
        user_id = robot["user_id"]
        
        row = df.loc[df['num'] == int(command_arg), ['role', 'prompt']].squeeze()
        role, prompt = row['role'], row['prompt']
        
        template="以下是一份扮演者的prompt,请理解并从扮演者的角度，给出对此prompt的简要解释。\
            考虑用户如何与此扮演者进行交互，并给出一个示例\
            返回格式为：\
            ---\
            简要解释:\
            ---\
            使用示例:"
        
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template="prompt:{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        reply = chat(chat_prompt.format_prompt(text=prompt).to_messages())
        answer = reply.content
        
        
        message = {
            "msgtype": "text",
            "text": {
                "content": f"<at user_id=\"{user_id}\"></at>当前需要设置的角色为{role}:\n\n{answer}"
            }
        }
        return (message , None)
