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
from retrying import Retrying, retry
from proxy.proxy import Proxy
import telnetlib
import traceback
from urllib.request import urlopen
import urllib.request
import redis
db  = redis.Redis(host='localhost', port=6379,password="redis",decode_responses=True)
logger = Logger(__name__)


cookies = {
    'Hm_lvt_b27c6e108bfe7b55832e8112042646d8': '1631193620',
    'PHPSESSID': '82e312b1861d2671854bb2c715bae594',
    'Hm_lpvt_b27c6e108bfe7b55832e8112042646d8': '1631435613',
    'CKISP': '0f1b33454e1766fcdfd63ce0c172adfb%7C1631435613',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.67',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'If-None-Match': 'W/"613dbb5c-5ee1"',
    'If-Modified-Since': 'Sun, 12 Sep 2021 08:33:32 GMT',
}
mapper = {"background-position:0 -120px":"5","background-position:0 -108px":"4.5","background-position:0 -96px":"4","background-position:0 -84px":"3.5",
"background-position:0 -72px":"3","background-position:0 -60px":"2.5","background-position:0 -48px":"2",
"background-position:0 -36px":"1.5","background-position:0 -24px":"1","background-position:0 -12px":"0.5","background-position:0 -0px":"0"}
pattern = re.compile(r"[(](.*?)[)]", re.S)
file_path = os.getcwd()+"//App//apk//"
executor = ThreadPoolExecutor(max_workers=8)
obj_list = []
p = Proxy()
ips = p.ips

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
def craw_app_list_page(url):   
# 46 ed
    ip = random.choice(ips)
    print(ip)
    proxies = {'http': "http://45.199.148.3:80", 'https': 'http://localhost:8888'}
    # session = requests.Session()
    # session.max_redirects = 10
    # page  = session.get("http://www.anzhi.com/sort_42_%i_hot.html"%page_num)
    # 42只有一页
    page = requests.get(
        url=url, proxies=proxies,cookies=cookies,
         headers=headers)
    if page.status_code == 200: 
        page = page.text
        logger.get_log().debug("访问应用列表页面  成功")
    else:
        ips.remove(ip)
        raise Exception("页面请求失败", page.status_code)
         
    apps = etree.HTML(page).xpath("//*[@class='app_list border_three']/ul/li")
    return apps


def download(id, name):
    """
    下载一个apk，下载完毕前，文件后缀为.tmp
    :param id: apk id
    :param name: apk名称
    :return: 
    """
    tmp_path = file_path + name + ".tmp"
    save_path = file_path + name +".apk"
    open(tmp_path,"w").close()
    params = (
        ('s', id),
        ('n', '5'),
    )
    logger.get_log().debug("开始下载应用：  "+name)
    # ip  = random.choice(ips)
    # proxy = urllib.request.ProxyHandler({'http':"http://113.238.142.208:3128"})
    # opener = urllib.request.build_opener(proxy,urllib.request.HTTPHandler)
    # urllib.request.install_opener(opener)
    # proxies = {'http': random.choice(ips), 'https': 'http://localhost:8888'}
    try:
        url = 'http://www.anzhi.com/dl_app.php?s='+ id[0] +"n=5"
    except TypeError:
        print("error",str(id[0]))
    try:
        u = urlopen(url)
        with open(tmp_path,'wb') as f:
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                f.write(buffer)
        os.rename(tmp_path,save_path)
        logger.get_log().error("下载成功" + name)
        return True

    except Exception as e:
        # ips.remove(ip)
        logger.get_log().error("下载失败" + name)
        logger.get_log().error(e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(save_path):
            os.remove(save_path)
        return False
    

def craw_download_urls(apps):
    arr = []
    for app in apps:
        try:
            name = app.xpath("./div[2]/span/a")[0].text
            version = app.xpath("./div[2]/div/span")[0].text
            download_num = app.xpath("./div[2]/div/span")[1].text
            desc = app.xpath("./div[2]/p")[0].text
            key = app.xpath("./div[2]/div/span[3]/span[2]")[0].attrib["style"]
            rating = mapper[key]
            id = app.xpath("./div[3]/a")[0].attrib["onclick"]
            id = re.findall(pattern, str(id))
            db.hmset(name,{'id':id[0],'version':version,'download_num':download_num,
            'desc':desc,'rating':rating})
            obj = executor.submit(download,id,name)
            obj_list.append(obj)
        except Exception as e :
            logger.get_log().error("下载 "+ name +"失败",e)
            break
    for future in as_completed(obj_list):
        result = future.result()
        if result:
            logger.get_log().debug("下载返回结果成功")
    logger.get_log().debug("应用描述信息爬取成功")
    with open(os.getcwd()+"\App\data\download_url.json","a",encoding='utf8') as f:
        f.write(json.dumps(arr,ensure_ascii=False)+"\n")
    logger.get_log().debug("应用描述信息存储成功")
    # 44包含游戏
for i in (47,56):
    for j in range(2,20):
        url = "http://www.anzhi.com/sort_%i_%i_hot.html"%(i,j)
        logger.get_log().debug("访问应用列表页面%i"%j)
    
        apps = craw_app_list_page(url)
        if len(apps)==0:
            break
        craw_download_urls(apps)
# for ip in ips:
#     if test_ip(ip):
#         print("ok")
