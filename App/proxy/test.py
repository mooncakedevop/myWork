import os,json
import requests
from lxml import etree
from threading import Timer
from apscheduler.schedulers.background import BackgroundScheduler


headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}
def write_proxy():
    arr = []
    for i in range(1,3):
        
        response = requests.get('https://ip.jiangxianli.com/?page=%i'%i, headers=headers).text
        ips = etree.HTML(response).xpath("//*[@class='layui-btn layui-btn-sm btn-copy']")
        for ip in ips:
            arr.append(ip.attrib["data-url"])
        print("第"+ str(i) + "页代理爬取完毕")

    with open ("D:\\myWork\\User\\myWork\\App\\data\\ip.json","w") as f:
        f.write(json.dumps(arr,ensure_ascii=False)+"\n")
        f.close()
        
write_proxy()
scheduler = BackgroundScheduler()
scheduler.add_job(write_proxy,'interval',minutes=5)
scheduler.start()
