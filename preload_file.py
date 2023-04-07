import os
import socks
import socket
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
from logs.logger import Logger
from conf.config import get_config

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

def create_index(fileid,ext):
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-embedding-ada-002"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    path = f"tools/download/{fileid}.{ext}"
    document = loader.load_data(file=Path(path))
    
    doc_index = GPTSimpleVectorIndex.from_documents(
        document, service_context=service_context
    )
    
    doc_index.save_to_disk(f'tools/index/index_embedding_{fileid}.json')
    

def query_file(fileid,query):
    
    path = f"tools/index/index_embedding_{fileid}.json"
    if os.path.exists(path):
        
        file_index = GPTSimpleVectorIndex.load_from_disk(path)
                
        chatllm = PromptLayerChatOpenAI(temperature=0.5, pl_tags=["chat-file","woa"])
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
            query,
            response_mode="tree_summarize",
            service_context=chat_service_content,
            text_qa_template=QA_PROMPT,
            refine_template=CHAT_REFINE_PROMPT,
            )
        print(response)
        
    else:
        create_index(fileid,"pdf")
        print("文件索引不存在，已重新创建索引")
        query_file(fileid,query)
