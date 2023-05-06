

from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
    
from langchain.schema import (
    HumanMessage,
    SystemMessage
)

def normalChat(command_arg,memory_key,chat):
    message_db = RedisChatMessageHistory(url='redis://localhost:6379/0', ttl=3600, session_id=memory_key)
    memory = ConversationBufferWindowMemory(memory_key=memory_key, 
                                            k=3, chat_memory=message_db, 
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
    return answer