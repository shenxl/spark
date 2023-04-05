
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
    
from langchain.schema import (
    HumanMessage,
    SystemMessage
)

def artsChat(command_arg,user,memory_key,chat):
    
    template = user.arts_template
    ai_answer = user.arts_answer
    
    message_db = RedisChatMessageHistory(url='redis://localhost:6379/0', ttl=3600, session_id=memory_key)
    memory = ConversationBufferWindowMemory(memory_key=memory_key, 
                                            k=5, chat_memory=message_db, 
                                            return_messages=True)
    
    system_message = SystemMessage(content=template)
    example_ai = SystemMessage(content=ai_answer)
#   human_template="""对话内容:{text}
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
        chat_prompt_message = [system_message, example_ai, human_message]    

    reply = chat(chat_prompt_message)
    message_db.add_user_message(command_arg)
    message_db.add_ai_message(reply.content)
    answer = f"""🥷**角色**： <font color='#e67700'>**`{user.arts_role}`**</font> \n\n{reply.content}"""
    return answer