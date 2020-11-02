import random
from datetime import datetime
import requests,base64,zlib, time
from project.美团全家桶.city import CITY
from project.Proxy import PROXY
class Meituan:
    pass
def get_Sign(base_url,url,page):
    originUrl = url + f'&page={page}&partner=126&platform=1&riskLevel=1&sort=&userId=&uuid=C082368707A3F2CBB95285B68189E70F278B4EF52CC5105E0E5C3D0EA4E54390'
    s = f'"areaId=0&cateId=17&cityName={CITY[base_url]}&dinnerCountAttrId=&optimusCode=10&originUrl={originUrl}"'
    # 二进制编码
    encode_ = s.encode()
    # 压缩
    compress = zlib.compress(encode_)
    # base64编码
    b_encode = base64.b64encode(compress)
    sign = str(b_encode, encoding='utf-8')
    return sign

def Get_token(base_url,url,page):
    referrer = url[:-4]
    ts = int(datetime.now().timestamp() * 1000)
    token_dict = {
        'rId': 100900,
        'ver': '1.0.6',
        'ts': ts,
        'cts': ts + 90,
        'brVD': [1503, 332],
        'brR': [[1536, 864], [1536, 824], 24, 24],
        'bI': [url, referrer],
        'mT': [],
        'kT': [],
        'aT': [],
        'tT': [],
        'aM': '',
        'sign': get_Sign(base_url,url,page)
    }
    # 二进制编码
    encode_ = str(token_dict).encode()
    # 压缩
    compress = zlib.compress(encode_)
    # base64编码
    b_encode = base64.b64encode(compress)
    token = str(b_encode, encoding='utf-8')
    return token


def getparams(base_url,url,page):
    params = {
        'cityName': CITY[base_url],
        'cateId': 0,
        'areaId': 0,
        'sort': '',
        'dinnerCountAttrId': '',
        'page': page,
        'userId': '',
        'uuid': 'C082368707A3F2CBB95285B68189E70F278B4EF52CC5105E0E5C3D0EA4E54390',
        'platform': 1,
        'partner': 126,
        'originUrl': url,
        'riskLevel': 1,
        'optimusCode': 10,
        '_token': Get_token(base_url,url,page)
    }
    return params
if __name__ == '__main__':
    #获取所有城市url
    city_urls=CITY.keys()
    s=requests.session()
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000'
    }
    s.headers=headers
    #https://qhd.meituan.com/meishi/pn67/
    #获取每个城市的美食
    cityShop_list={}
    for city_url in city_urls:
        title=[]
        base_url=city_url
        for page in range(1,100):
            city_url=base_url+f'meishi/pn{str(page)}/'
            print(city_url)
            #获取代理IP
            proxy = random.choice(PROXY) # 本地代理
            proxies = {
                'http': 'http://' + proxy,
            }
            params=getparams(base_url,city_url,page)
            url='https://changli.meituan.com/meishi/api/poi/getPoiList?'
            res=s.get(url,params=params,proxies=proxies).json()['data']
            if not res['poiInfos']:
                break
            title.extend([x['title'] for x in res['poiInfos']])
            time.sleep(1)
        cityShop_list[CITY[base_url]]=title
        time.sleep(5)


