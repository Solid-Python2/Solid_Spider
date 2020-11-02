# encoding: utf-8
import json

from taobao.taobao_notcookie.config import *
import requests
import hashlib
import time
from urllib.parse import quote
import threading,re
from queue import Queue


class TaoBao(threading.Thread):
    def __init__(self,str_searchContent,appKey ,search_data_Queue):
        super().__init__()
        self.search_data_Queue=search_data_Queue
        self.appKey = appKey
        self.cookie = ''
        self.token = ''
        self.L_itemId = []
        self.pdDb=productmongo
        self.pdDb.set_key(str_searchContent)
        self.first_requests()  # 可以在此调整获取cookie的频率

    def first_requests(self):
        # 第一次请求,无cookie请求,获取cookie
        base_url = 'https://h5api.m.taobao.com/h5/mtop.alimama.union.sem.landing.pc.items/1.0/?jsv=2.4.0&appKey=12574478&t=1582738149318&sign=fe2cf689bdac8258a1d12507a06bd289&api=mtop.alimama.union.sem.landing.pc.items&v=1.0&AntiCreep=true&dataType=jsonp&type=jsonp&ecode=0&callback=mtopjsonp1&data=%7B%22keyword%22%3A%22%E8%8B%B9%E6%9E%9C%E6%89%8B%E6%9C%BA%22%2C%22ppath%22%3A%22%22%2C%22loc%22%3A%22%22%2C%22minPrice%22%3A%22%22%2C%22maxPrice%22%3A%22%22%2C%22ismall%22%3A%22%22%2C%22ship%22%3A%22%22%2C%22itemAssurance%22%3A%22%22%2C%22exchange7%22%3A%22%22%2C%22custAssurance%22%3A%22%22%2C%22b%22%3A%22%22%2C%22clk1%22%3A%22%22%2C%22pvoff%22%3A%22%22%2C%22pageSize%22%3A%22100%22%2C%22page%22%3A%22%22%2C%22elemtid%22%3A%221%22%2C%22refpid%22%3A%22%22%2C%22pid%22%3A%22430673_1006%22%2C%22featureNames%22%3A%22spGoldMedal%2CdsrDescribe%2CdsrDescribeGap%2CdsrService%2CdsrServiceGap%2CdsrDeliver%2C%20dsrDeliverGap%22%2C%22ac%22%3A%22%22%2C%22wangwangid%22%3A%22%22%2C%22catId%22%3A%22%22%7D'
        try:
            with requests.get(base_url) as response:
                get_cookies = requests.utils.dict_from_cookiejar(
                    response.cookies)
                _m_h5_tk = get_cookies['_m_h5_tk']
                _m_h5_tk_enc = get_cookies['_m_h5_tk_enc']
                self.token = _m_h5_tk.split('_')[0]
                self.cookie = '_m_h5_tk={}; _m_h5_tk_enc={}'.format(
                    _m_h5_tk, _m_h5_tk_enc)
        except Exception as e:
            print('first_requests 出错: ', e)

    def sign(self, token, tme, appKey, data):
        st = token+"&"+tme+"&"+appKey+"&"+data
        m = hashlib.md5(st.encode(encoding='utf-8')).hexdigest()
        return(m)

    def second_requests(self,str_data):
        print('{}正在爬取第{}页内容'.format(self.name,re.search('"page":"(\d+)"',str_data)[1]))
        print(str_data)
        # 第二次带cookie请求,返回数据并存储
        data = quote(str_data, 'utf-8')

        tme = str(time.time()).replace('.', '')[0:13]

        sgn = self.sign(self.token, tme, self.appKey, str_data)

        url = 'https://h5api.m.taobao.com/h5/mtop.alimama.union.sem.landing.pc.items/1.0/?jsv=2.4.0&appKey={}&t={}&sign={}&api=mtop.alimama.union.sem.landing.pc.items&v=1.0&AntiCreep=true&dataType=jsonp&type=jsonp&ecode=0&callback=mtopjsonp2&data={}'.format(
            appKey, tme, sgn, data)
        proxies = {
            "http": 'http://' + random.choice(PROXY),
        }
        headers = {'cookie': self.cookie}
        try:
            with requests.get(url, headers=headers,proxies=proxies) as res:
                html = res.text
                json_=re.search('mtopjsonp2\((.*?)\)$',html)
                if json_:
                    res_list = json.loads(json_.group(1)).get('data',{}).get('mainItems',{})

                    if res_list:
                        self.Save_Product_To_Mongo(res_list)
                    else:
                        print('Cannot fount data in this page.')
        except Exception as e:
            print('second_requests 出错: ', e)



    def Save_Product_To_Mongo(self,reslist):
        for res in reslist:
            item={}
            #id
            id=res.get('itemId')
            cout_dic[id]=cout_dic.get(id,0)+1
            #标题
            title=res.get('title')
            #销售量
            sellCount=res.get('sellCount')
            #价格
            price=res.get('price')
            #平均评分
            avg_dsr=(float(res.get('dsrDeliver','0'))+float(res.get('dsrDescribe','0'))+float(res.get('dsrService','0')))/3
            #地址
            loc=res.get('loc')
            item['product_id']=id
            item['title']=title
            item['sellCount']=sellCount
            item['price']=price
            item['avg_dsr']=float('{:.1f}'.format(avg_dsr))
            item['loc']=loc
            self.pdDb.update(id,item)
        print('正在保存....')



    def run(self):
        while True:
            if self.search_data_Queue.empty():
                break
            print('搜索页面 线程启动: ', self.name)
            str_data = self.search_data_Queue.get()
            self.second_requests(str_data)

if __name__ == "__main__":
    cout_dic={}
    search_data_Queue = Queue()
    keyword = '洗面奶'
    for page in range(1,50):
        str_data = '{"keyword":"' + keyword + '","ppath":"","loc":"","minPrice":"","maxPrice":"","ismall":"","ship":"","itemAssurance":"","exchange7":"","custAssurance":"","b":"","clk1":"","pvoff":"","pageSize":"' + str(num_pageSize) + '","page":"' + \
                   str(page) + '","elemtid":"1","refpid":"","pid":"430673_1006","featureNames":"spGoldMedal,dsrDescribe,dsrDescribeGap,dsrService,dsrServiceGap,dsrDeliver, dsrDeliverGap","ac":"","wangwangid":"","catId":""}'
        search_data_Queue.put(str_data)
    mythread = []
    for _ in range(4):
        t = TaoBao( keyword,appKey,search_data_Queue)
        t.start()
        mythread.append(t)
    s = [t.join() for t in mythread]
    print('存储完成')

