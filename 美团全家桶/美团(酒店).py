import requests, json
from project.Proxy import PROXY
import random,datetime
import pandas as pd
url='https://ihotel.meituan.com/hbsearch/HotelSearch'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000',
    'Origin': 'https://hotel.meituan.com',
    'Referer': 'https://hotel.meituan.com/guangzhou/'
}

params = {
    'version_name': 999.9,
    'cateId': 20,
    'attr_28': 129,
    'cityId': 20,
    'offset': 0,
    'limit': 20,
    'startDay': datetime.datetime.now().strftime('%Y%m%d'),
    'endDay': datetime.datetime.now().strftime('%Y%m%d'),
}
res = []
for page in range(0,2):
    proxy = random.choice(PROXY)  # 本地代理
    proxies = {
        'http': 'http://' + proxy,
    }
    params['offset']=page*20
    result=requests.get(url, headers=headers, proxies=proxies, params=params).json()

    #获取所有酒店的poiid
    for hotel_data in result['data']['searchresult']:

        lst=[]
        #酒店名
        hotel_name=hotel_data['name']
        lst.append(hotel_name)
        #酒店类型
        hotel_type=hotel_data['poiRecommendTag']
        lst.append(hotel_type)
        #平均评分
        avgScore=hotel_data['avgScore']
        lst.append(avgScore)
        #评论数
        commentsCount=hotel_data['commentsCountDesc']
        lst.append(commentsCount)
        #平均消费
        historySaleCount=hotel_data['historySaleCount']
        lst.append(historySaleCount)
        #地址
        address=hotel_data['addr']
        lst.append(address)
        #可提供服务
        serviceIcons=[]
        for s in hotel_data['forward']['serviceIcons']:
            serviceIcons.append(s['attrDesc'])
        lst.append('|'.join(serviceIcons))
        res.append(lst)
writer=pd.ExcelWriter('./美团酒店信息表.xls')
df=pd.DataFrame(
    data=res,
    columns=['酒店名','酒店类型','平均评分','评论数','平均消费','地址','可提供服务'],
)
df.to_excel(writer,sheet_name='广州')
writer.save()
writer.close()
print("保存成功")