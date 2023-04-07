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
    # TODO 目前只支持PDF
    PDFReader = download_loader("PDFReader")
    loader = PDFReader()
    path = f"tools/download/{fileid}.{ext}"
    document = loader.load_data(file=Path(path))
    
    doc_index = GPTSimpleVectorIndex.from_documents(
        document, service_context=service_context
    ) 
    
    doc_index.save_to_disk(f'tools/index/index_embedding_{fileid}.json')
    

