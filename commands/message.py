import socks
import socket
import os
from itertools import chain

from .executor import CommandStrategy
from logs.logger import Logger
from conf.config import get_config
from app.user import  User,UserMode

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
    
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
            message_db = RedisChatMessageHistory(url='redis://localhost:6379/0', ttl=3600, session_id=memory_key)
            memory = ConversationBufferWindowMemory(memory_key=memory_key, 
                                                    k=5, chat_memory=message_db, 
                                                    return_messages=True)
            memory_buffer = memory.load_memory_variables({})
            chat_history = []
            if memory_key in memory_buffer:
                chat_history = memory_buffer[memory_key]
            system_message_prompt = SystemMessage(content="You are a helpful assistant to me.")
            human_message_prompt=HumanMessage(content=command_arg)
            chat_prompt_message = [system_message_prompt] + chat_history + [human_message_prompt]
            
            reply = chat(chat_prompt_message)
            
            message_db.add_user_message(command_arg)
            message_db.add_ai_message(reply.content)
            answer = reply.content
            
        if user.mode == UserMode.ARTS:
            template = user.arts_template
            ai_answer = user.arts_answer
            
            memory_key = f"{robot.user_id}_{user.arts_role}_history"
            
            message_db = RedisChatMessageHistory(url='redis://localhost:6379/0', ttl=3600, session_id=memory_key)
            memory = ConversationBufferWindowMemory(memory_key=memory_key, 
                                                    k=5, chat_memory=message_db, 
                                                    return_messages=True)
            
            system_message = SystemMessage(content=template)
            example_ai = SystemMessage(content=ai_answer)
#             human_template="""对话内容:{text}
# 返回格式请以'emoji' + {角色}[Bot]: 开头,其中'emoji' 要选择与{角色}最匹配的图标，只选择一个
# 例如
# ---
# 🥷 魔术师[Bot]: 
# 👴 IT架构师[Bot]:
# """
            # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            # human_message = human_message_prompt.format(text=command_arg,角色=user.arts_role)
            human_message = HumanMessage(content=command_arg)
            memory_buffer = memory.load_memory_variables({})
            arts_chat_history = []
            if memory_key in memory_buffer:
                arts_chat_history = memory_buffer[memory_key]
                # 如果有历史记录，则将历史记录加入到对话中
                chat_prompt_message = [system_message] + arts_chat_history + [human_message]
            else:
                # 否则，将示例加入到对话中
                chat_prompt_message = [system_message] + example_ai + [human_message]    

            reply = chat(chat_prompt_message)
            message_db.add_user_message(command_arg)
            message_db.add_ai_message(reply.content)
            answer = f"""🥷**角色模式**： <font color='#e67700'>**`{user.arts_role}`**</font> \n\n{reply.content}"""
        
        
        message = {
            "msgtype": "markdown",
            "content": answer
        }
        return (message , None)
