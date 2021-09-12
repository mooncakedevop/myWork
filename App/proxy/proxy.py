import os
import json,requests


class Proxy:
    arr = []

    def __init__(self):
        f = open(os.getcwd()+"\App\data\ip.json", "r", encoding='utf8')
        while True:
            line = f.readline()
            if not line:
                break
            js = json.loads(line)
            self.arr.extend(js)

    @property
    def ips(self):
        return self.arr

    def get_ip(self):
        res = requests.get("https://ip.jiangxianli.com/api/proxy_ip",verify=False).json()
        ip = res["data"]["ip"]
        port = res["data"]["port"]
        return "http://"+ip+":"+port

