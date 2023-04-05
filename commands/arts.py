import socks
import socket
import os
from itertools import chain
import pandas as pd

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
        # user_id = robot["user_id"]
        card_text ="""##### 1️⃣ 挑选角色\n\n
  请在下方列表中挑选角色\n\n
##### 2️⃣ 发送指令\n\n
  通过指令 `%arts set <序号>%` 进行角色设定, 例如：`%arts set 5%`\n\n
##### 3️⃣ 对话\n\n
  @BOT 后正常对话，Bot会依据此角色的设定与你进行交流\n\n
### **🎉🎉 玩的开心**"""
        message = {
            "msgtype": "link",
            "link": {
                "title": "🥷 角色卡片",
                "text": card_text,
                "messageUrl": "https://kdocs.cn/l/cgPpL1tqMyUe",
                "btnTitle": "查看列表"
            }
        }
        
        
        return (message , None)
    


class ArtsSetCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        # 当前bot的当前用户对话, 判断是否是以 act-> 开头
        user_id = robot["user_id"]
        user = User.get_user(robot.user_id)
        
        row = df.loc[df['num'] == int(command_arg), ['role', 'prompt']].squeeze()
        role, prompt = row['role'], row['prompt']
        
        template="""以下是一份指导如何扮演{角色}的 prompt,
请理解要扮演的角色:{角色}，并从{角色}的角度，给出此角色的自我介绍。
考虑用户应该如何与{角色}进行交互,给出简短的示例对话
确保返回格式为:
-----------------
#### 💡 自我介绍:
#### 👀 示例对话:
🙎 **用户[User]**:

🥷 **{角色}[bot]**:
"""
        
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template="prompt:{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        reply = chat(chat_prompt.format_prompt(text=prompt,角色=role).to_messages())
        answer = reply.content
        text = f"""🥷**角色模式**： <font color='#e67700'>**`{role}`**</font> \n\n{answer}"""
        user.update_arts_mode(role=role, prompt=prompt, answer=answer)
        message = {
            "msgtype": "markdown",
            "content": text
        }
        return (message , None)
