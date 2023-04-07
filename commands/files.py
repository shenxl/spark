import socks
import socket
import os

from .executor import CommandStrategy
from logs.logger import Logger
from conf.config import  get_config
from app.user import  User
from tools.fetch_file import get_html,fetch_file,get_url,fetch_minio_url
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
chat = PromptLayerChatOpenAI(temperature=0.9, pl_tags=["woa_chat"])

# 设置日志
logger = Logger(__name__)
class FilesCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        #user_id = robot["user_id"]
        card_text ="""##### 1️⃣ 提供文档\n\n
##### 2️⃣ 发送指令\n\n
  通过指令 `%files ask <id>%` 进行角色设定, 例如：`%files ask cgPpL1tqMyUe%`\n\n
##### 3️⃣ 对话\n\n
  接受到返回指令后，可以 @BOT  对话，Bot会依据此文件内容，与你进行交流\n\n
### **🎉🎉 玩的开心**"""
        message = {
            "msgtype": "link",
            "link": {
                "title": "📑 文件卡片",
                "text": card_text
            }
        }
        
        
        return (message , None)
    
class FilesASKCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        if command_arg is None:
            user = User.get_user(robot.user_id)
            chatllm = PromptLayerChatOpenAI(temperature=0.5, pl_tags=[robot.user_id,user.file_name,"woa_chat"])
            query = "请针对文档内容，提出三个问题，以便提问者可以基于这些问题，深入了解文档内容"
            answer = filesChat(query,user=user,chatllm=chatllm)
            
            message = {
                "msgtype": "markdown",
                "content": answer
            }
            return (message , None)
        else:
            User.update_files_mode(robot.user_id, fileid=command_arg,filename="未知文档",filetype="pdf")
            message = {
                "msgtype": "markdown",
                "content": f"切换文档成功{command_arg}"
            }
            return (message , None)

class FilesInitCommandStrategy(CommandStrategy):
    def execute(self, robot, command_arg):
        user_id = robot["user_id"]
        folder = f"tools/download/"
        url = f"{get_config().KDOC_BASE_URL}/l/{command_arg}"

        fileinfo = get_html(url)
        
        if "fileinfo" in fileinfo:
            info = fileinfo["fileinfo"]
            fname = info["fname"]
            groupid = info["groupid"]
            fid = info["id"]
            extension = fname.split('.')[-1]
            # logger.info(f"文件名:{fname} groupid:{groupid} fid:{fid} extension:{extension}")
            
            if extension == "otl":
                url = get_url(command_arg)
            else:
                url =  f'{get_config().DRIVE_BASE_URL}/api/v5/groups/{groupid}/files/{fid}/download?support_checksums=md5,sha1,sha224,sha256,sha384,sha512'
                url = fetch_minio_url(url)
            
            if url is not None and url != "permissionDenied":
                # 下载文件
                (id, type) =  fetch_file(folder,command_arg,url)
                # 更新用户文件信息
                User.update_files_mode(user_id, fileid=command_arg,filename=fname,filetype=type)
                # 进行索引建立
                message = {
                    "msgtype": "markdown",
                    "content": (f"### 文档{fname}处理完成\n\n"
                                "- 请使用命令`%files ask%` 对文档进行问答 \n\n"
                                "- 使用命令%files% 查看文档卡片 \n\n"
                                "- 使用命令%files ls% 展示文档上传的列表 \n\n" )
                }
                return (message , None)
            elif url == "permissionDenied":
                message = {
                    "msgtype": "markdown",
                    "content": f"### 文件:{fname}权限不足"
                }
                return (message , None)
            
            message = {
                "msgtype": "markdown",
                "content": ("### 文档处理失败\n\n"
                            f"请确认{command_arg}参数是否正确")
            }

        return (message , None)
