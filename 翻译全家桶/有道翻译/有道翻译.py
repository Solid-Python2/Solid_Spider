import requests
import time, hashlib
import random
from project.Proxy import PROXY
import random

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    'Referer': 'http://fanyi.youdao.com/',
    'Cookie': 'OUTFOX_SEARCH_USER_ID=-1088907749@10.108.160.17; OUTFOX_SEARCH_USER_ID_NCOO=495345382.15496266; _ga=GA1.2.1246759559.1599640216; JSESSIONID=aaaNrvedkNBo1etBN17rx; ___rl__test__cookies=1599806307868',
}
url='http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
nav = "年后"
lts = str(int(time.time() * 1000))
salt = lts + str(random.randint(0, 10))
sign = hashlib.md5(f"fanyideskweb{nav}{salt}]BjuETDhU)zqSxf-=B#7m".encode()).hexdigest()
data = {
    'i': nav,
    'from': 'AUTO',
    'to': 'AUTO',
    'smartresult': 'dict',
    'client': 'fanyideskweb',
    'salt': salt,
    'sign': sign,
    'lts': lts,
    'bv': 'cae1ccfe9ff58b23f321b76ea781684b',
    'doctype': 'json',
    'version': '2.1',
    'keyfrom': 'fanyi.web',
    'action': 'FY_BY_REALTlME',
}
print(requests.post(url, headers=headers, data=data).json())