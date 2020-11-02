import requests
from World import WORLD
url = 'http://cn.bing.com/ttranslatev3?isVertical=1&&IG=E5F3338A3FB64FE5A2EC784A5C65FA25&IID=translator.5028.3'
data = {
    'fromLang':'auto-detect',
    'text':'I like English',
    'to':'en'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000',
    'Accept-Language': 'zh-CN',
    'Content-type': 'application/x-www-form-urlencoded'
}
print(requests.post(url, headers=headers, data=data).json())