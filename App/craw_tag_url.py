import requests
import os,json
import html
from bs4 import BeautifulSoup
from lxml import etree
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
url = "http://www.anzhi.com/applist.html"
index = requests.get(url,headers=headers).text

tags = etree.HTML(index).xpath("//*[@class='more']/a")
data = []
for tag in tags:
    data.append(tag.attrib["href"])

with open (os.getcwd() + "//App//data//url.json","w") as f:
    f.write(json.dumps(data))
