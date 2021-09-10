from logging import error
from random import random
from sys import version
import requests
import json,os,random
import re
import html
from bs4 import BeautifulSoup
from lxml import etree
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed
from logs.logger import Logger
from retrying import retry
from proxy.proxy import Proxy
import telnetlib
logger = Logger(__name__)
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://www.anzhi.com/',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'If-None-Match': 'W/"6130be67-b379"',
    'If-Modified-Since': 'Thu, 02 Sep 2021 12:07:03 GMT',
}
mapper = {"background-position:0 -120px":"5","background-position:0 -108px":"4.5","background-position:0 -96px":"4","background-position:0 -84px":"3.5",
"background-position:0 -72px":"3","background-position:0 -60px":"2.5","background-position:0 -48px":"2",
"background-position:0 -36px":"1.5","background-position:0 -24px":"1","background-position:0 -12px":"0.5","background-position:0 -0px":"0"}
pattern = re.compile(r"[(](.*?)[)]", re.S)
file_path = os.getcwd()+"//App//apk//"
executor = ThreadPoolExecutor(max_workers=5)
obj_list = []
ips = Proxy().ips

def test_ip(url):
    ip = url.split(":")[1][2:]
    port  = url.split(":")[2]

    try:
        telnetlib.Telnet(ip,port, timeout=1)
        return True
    except Exception as e:
        return False
def get_ip(ips):
    for ip in ips:
        if test_ip(ip):
            return ip
    return ""
        
@retry(stop_max_attempt_number=3)
def craw_app_list_page(page_num):

    proxies = {'http': random.choice(ips), 'https': 'http://localhost:8888'}
    page = requests.get(
        url="http://www.anzhi.com/sort_45_%i_hot.html"%page_num, proxies=proxies,
         headers=headers,verify=False)
    if page.status_code == 200: 
        page = page.text
        logger.get_log().debug("访问应用列表页面 page %i 成功"%page_num)
    else:
        raise Exception("页面请求失败")
        
    apps = etree.HTML(page).xpath("//*[@class='app_list border_three']/ul/li")
    return apps

@retry(stop_max_attempt_number=3)
def download(id, name):
    """
    下载一个apk，下载完毕前，文件后缀为.tmp
    :param id: apk id
    :param name: apk名称
    :return:
    """
    tmp_path = file_path + name + ".tmp"
    open(tmp_path,"w").close()
    params = (
        ('s', id),
        ('n', '5'),
    )
    logger.get_log().debug("开始下载应用：  "+name)

    proxies = {'http': random.choice(ips), 'https': 'http://localhost:8888'}
    response = requests.get('http://www.anzhi.com/dl_app.php', headers=headers, proxies=proxies,params=params,stream=True, verify=False)
    

     
    # stream = True流式请求
    with open(tmp_path,"wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    os.rename(tmp_path, file_path+name+".apk")
    
    return name

def craw_download_urls(apps):
    arr = []
    for app in apps:
        name = app.xpath("./div[2]/span/a")[0].text
        version = app.xpath("./div[2]/div/span")[0].text
        download_num = app.xpath("./div[2]/div/span")[1].text
        desc = app.xpath("./div[2]/p")[0].text
        key = app.xpath("./div[2]/div/span[3]/span[2]")[0].attrib["style"]
        rating = mapper[key]
        id = app.xpath("./div[3]/a")[0].attrib["onclick"]
        id = re.findall(pattern, str(id))
        arr.append({'name':name,'id':id[0],'version':version,'download_num':download_num,
        'desc':desc,'rating':rating})
        try:
            result = executor.submit(download,id,name)
            for data in as_completed([result]):
                if data.result():
                    logger.get_log().debug("应用 %s 下载成功"%data.result())
                print("download success "+name)
        except :
            logger.get_log().debug("下载 "+ name +"失败")
            break

    logger.get_log().debug("应用url爬取成功")
    with open(os.getcwd()+"\App\data\download_url.json","a",encoding='utf8') as f:
        f.write(json.dumps(arr,ensure_ascii=False)+"\n")
    logger.get_log().debug("应用url存储成功")

for i in range(1,20):
    apps = craw_app_list_page(i)
    craw_download_urls(apps)
# for ip in ips:
#     if test_ip(ip):
#         print("ok")
