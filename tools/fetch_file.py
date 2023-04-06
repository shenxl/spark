'''
网络请求相关函数
load_cookie 加载cookie
get_html 获取网页信息
fetch_download_url 请求下载接口
fetch_minio_url 获得 minio 地址
fetch_file 下载文件

'''
import requests
import http.cookiejar
import re
import json
import urllib.parse
import time
import random

from requests_html import HTMLSession

from logs import logger

from logs.logger import Logger
from conf.config import get_config


# 设置日志
logger = Logger(__name__)


def load_cookie():
    cookiejar = http.cookiejar.MozillaCookieJar()
    cookiejar.load('app/private/me.txt')
    cookie_dict = requests.utils.dict_from_cookiejar(cookiejar)
    return cookie_dict


def get_html(url):
    session = HTMLSession()
    cookie_dict = load_cookie()
    r = session.get(url,cookies=cookie_dict)
    info_url =fetch_info_url(r.html.text)
    if  info_url == '':
        raise Exception("权限校验失败，请检查 me.cookie 文件")
    fileinfo = fetch_file_info(info_url)
    # minio_url = fetch_minio_url(download_url)
    return fileinfo

def fetch_file_info(url):
    session = HTMLSession()
    cookie_dict = load_cookie()
    response = session.get(url,cookies=cookie_dict)
    content = response.json()
    return content

def fetch_info_url(str):
    file_ids = re.findall(r'"file":{"id":"(.*?)","name"',str, re.M|re.S)
    # group_ids =re.findall(r'"group_id":"(.*?)","supportTag"',str, re.M|re.S)
    # if len(file_ids) > 0 and len(group_ids) > 0:
    if len(file_ids) > 0 :
        file_id = file_ids[0]
        # group_id = group_ids[0]
        return f"{get_config().DRIVE_BASE_URL}/api/v5/links/{file_id}"
    return ""

def fetch_minio_url(url):
    session = HTMLSession()
    cookie_dict = load_cookie()
    response = session.get(url,cookies=cookie_dict)
    content = response.json()
    return content["url"]

def export_pdf_url(fileid,again=False,version=None):
    session = HTMLSession()
    cookie_dict = load_cookie()
    payload = {
        "url": f"{get_config().KDOC_BASE_URL}/l/{fileid}",
        "url_param": "pdfExport&simple&export=true&hideguide&disableNps&adaptiveWidth",
        "margin_top": 0.7,
        "margin_bottom": 0.7,
        "margin_left": 0.7,
        "margin_right": 0.7,
        "user_token": {
            "token": "",
            "expire": 0
        },
        "store_type": "ks3",
        "paper_width": 20,
        "print": False
    }
    headers = {
        "referer":f"{get_config().KDOC_BASE_URL}/l/{fileid}",
        "origin":f"{get_config().KDOC_BASE_URL}"}

    url = f"{get_config().KDOC_BASE_URL}/api/v3/office/outline/file/{fileid}/version/{version}/export/pdf"
    
    if again == True:
        url = url + "/get"
    else:
        url = url + "/preload"
    
    response = session.post(url,headers=headers,
                        data=json.dumps(payload),cookies=cookie_dict)
    return response.json()
    
def get_url(url):
        # 发起POST请求
        version = generate_random_string()
        preload_result = export_pdf_url(url,version=version)
        # 轮询检查status
        logger.info("正在生成PDF文件，请稍后...")
        logger.info(f"preload url...{preload_result}")
        if preload_result.get("result") == "permissionDenied":
            return "permissionDenied"
        while preload_result.get("status") == "Building":
            time.sleep(3)
            preload_result = export_pdf_url(url, again=True,version=version)
            logger.info(f"get url...{preload_result}")

        return preload_result.get("url") 
    
def fetch_file(folder,id,miniourl):
    session = HTMLSession()
    cookie_dict = load_cookie()
    response = session.get(miniourl,cookies=cookie_dict)
    # 获取文件名和扩展名
    extension = None
    logger.info(f"正在下载文件，请稍后...{miniourl}")
    # 从响应头中提取文件名和扩展名
    if 'Content-Disposition' in response.headers:
        content_disposition = response.headers['Content-Disposition']
        filename_start = content_disposition.find('filename*=utf-8\'\'') + len('filename*=utf-8\'\'')
        filename_encoded = content_disposition[filename_start:]
        name = urllib.parse.unquote(filename_encoded)
        extension = name.split('.')[-1]
        name = id + '.' + extension
        # 打印文件名和扩展名
        f = open(folder + name, 'wb').write(response.content)
        return folder + name
    
def generate_random_string():
    return f"{random.randint(1000, 9999)}_{random.randint(1, 9)}_{random.randint(1, 9)}"