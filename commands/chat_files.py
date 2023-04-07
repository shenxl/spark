import os

from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
    
from langchain.schema import (
    HumanMessage,
    SystemMessage
)


import promptlayer
from pathlib import Path
from llama_index import download_loader
from llama_index import (
    PromptHelper,
    LLMPredictor,
    ServiceContext,
    QuestionAnswerPrompt,
    RefinePrompt,
    GPTSimpleVectorIndex
)

from langchain.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)


from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import PromptLayerChatOpenAI
from llama_index.prompts.default_prompts import DEFAULT_TEXT_QA_PROMPT_TMPL, DEFAULT_REFINE_PROMPT_TMPL
import promptlayer

def create_index(fileid,ext):
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-embedding-ada-002"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    # TODO 目前只支持PDF
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    path = f"tools/download/{fileid}.{ext}"
    document = loader.load_data(file=Path(path))
    
    doc_index = GPTSimpleVectorIndex.from_documents(
        document, service_context=service_context
    ) 
    
    doc_index.save_to_disk(f'tools/index/index_embedding_{fileid}.json')


def filesChat(command_arg,user,chatllm):
    file_id = user.file_id
    path = f"tools/index/index_embedding_{file_id}.json"
    if os.path.exists(path):
        file_index = GPTSimpleVectorIndex.load_from_disk(path)
        chat_predictor = LLMPredictor(llm=chatllm)
        chat_service_content = ServiceContext.from_defaults(llm_predictor=chat_predictor)
    
        QA_PROMPT_TMPL = (
            "以下内容是我们对问题的上下文信息\n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            "基于以上信息，请回答: {query_str}\n"
            "如果上下文中无法回答问题，请回复'以上背景无法回答问题，请忽略'\n"
        )
        
        # Refine Prompt
        CHAT_REFINE_PROMPT_TMPL_MSGS = [
            HumanMessagePromptTemplate.from_template("问题：{query_str}"),
            AIMessagePromptTemplate.from_template("已有答案：{existing_answer}"),
            HumanMessagePromptTemplate.from_template(
                "我们还有以下背景信息来，用于补充已有答案\n"
                "------------\n"
                "{context_msg}\n"
                "------------\n"
                "根据新的背景信息，完善已有答案以更好回答问题。\n"
                "如果上下文没有用处，则返回原始的已有答案。\n"
            ),
        ]

        CHAT_REFINE_PROMPT_LC = ChatPromptTemplate.from_messages(CHAT_REFINE_PROMPT_TMPL_MSGS)
        
        QA_PROMPT = QuestionAnswerPrompt(QA_PROMPT_TMPL)
        CHAT_REFINE_PROMPT = RefinePrompt.from_langchain_prompt(CHAT_REFINE_PROMPT_LC)
        
        response = file_index.query(
            command_arg,
            response_mode="tree_summarize",
            service_context=chat_service_content,
            text_qa_template=QA_PROMPT,
            refine_template=CHAT_REFINE_PROMPT,
            )
        answer = f"""📑**文件**： <font color='#e67700'>**`{user.file_name}`**</font> \n\n{response}"""
        return answer   
    else:
        create_index(file_id,"pdf")
        filesChat(command_arg,user,chatllm)