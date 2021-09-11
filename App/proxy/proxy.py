import os
import json


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
