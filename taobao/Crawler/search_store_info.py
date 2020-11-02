#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/23 0023 22:15            
 @Author:LG
 @Version:1.0
 @Desciption:获取搜索关键词的100页商品的标题,销售量,价格,店铺,地址
"""
import requests,re
import time,os
import json,sys
import threading
from queue import Queue
from taobao.settings import cookieDb
from taobao.settings import productDb
class Crawler(threading.Thread):
    def __init__(self,keyword,search_url_Queue):
        super().__init__()
        self.cdb = cookieDb
        self.pdDb=productDb
        self.pdDb.set_key(keyword)
        self.session=None
        self.search_url_Queue=search_url_Queue

    def set_session(self):
        headers = {
            'User-Agent': '"Mozilla/5.0 (Linux; U; Android 1.6; en-us; SonyEricssonX10i Build/R1AA056) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",',
            'Connection': 'close',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'referer': 'https://www.taobao.com/'}
        #删除报错
        import urllib3
        urllib3.disable_warnings()
        s = requests.session()
        s.keep_alice = False
        s.verify = False
        s.headers=headers
        cookies=self.get_cookie()
        if cookies:
            headers['cookie']=cookies
        else:
            print('cookie都失效了请及时更新cookie')
            sys.exit()
        self.session = s

    def get_cookie(self):
        """
        获取不为空的cookie
        :return: 返回cookie,如果cookie池中的cookie都失效了则返回None
        """
        q = self.cdb.find_cookies(flag=0)
        if q == None:
            return None
        else:
            print('获取cookie')
            self.user=q['user']
            return q['cookies']

    def get_page(self, url):
        """
        解析页面
        :param url:url
        :return:
        """
        self.set_session()
        # r = self.session.get(url, headers=HEADERS, cookies=self.get_cookie())
        r = self.session.get(url, timeout=(14, 15))
        if r.text.find('亲，小二正忙，滑动一下马上回来') > 0:
            print("cookie需要验证!!!")
            self.cdb.update_cookie_flag2(self.user)
            self.search_url_Queue.put(url)
            return False
        if r.text.find('请输入') > 0:
            print("Need Login!!!")
            self.cdb.update_cookie_flag3(self.user)
            self.search_url_Queue.put(url)
            return False
        self.parse(r.text)

        time.sleep(4)
        return True
    def SaveProduct(self,auctions):
        for auction in auctions:
            item = {}
            #id
            id=auction.get('nid')
            # 商品名
            title = auction.get('raw_title')
            # 价格
            price = auction.get('view_price')
            # 销售量
            sales_counts = auction.get('view_sales', '0').replace('人收货', '').replace('人付款', '')
            # 店铺名
            store_name = auction.get('nick')
            # 地址
            adress = auction.get('item_loc')
            item['product_id']=id
            item['title'] = title
            item['price'] = price
            item['sales_counts'] = sales_counts
            item['store_name'] = store_name
            item['adress'] = adress
            self.pdDb.update(id,item)
        print('正在保存.....')
    def parse(self,html):
        pattern = re.compile(r'g_page_config = ({.*});')
        m = re.search(pattern, html)
        if not m:
            print('Cannot fount data in this page.')
            return False
        g_page_config = json.loads(m.group(1))
        auctions = g_page_config.get("mods").get("itemlist").get("data").get("auctions")
        self.SaveProduct(auctions)

    def run(self):
        while True:
            if self.search_url_Queue.empty():
                print(self.dict)
                break
            search_url=self.search_url_Queue.get()
            flag=self.get_page(search_url)
            if flag:
                self.search_url_Queue.task_done()
            else:
                print('正在更换cookie')
                #更换cookie
                self.session.headers['cookie']=self.get_cookie()


if __name__ == '__main__':
    search_url_Queue=Queue()
    keyword='洗面奶'
    for i in range(2):
        page = str(i * 44)
        url = 'https://s.taobao.com/search?q=' + keyword + '&sort=sale-desc&s=' + page
        search_url_Queue.put(url)
    mythread=[]
    for _ in range(2):
        t=Crawler(keyword,search_url_Queue)
        t.start()
        mythread.append(t)
    s=[t.join() for t in mythread]
    print('存储完成')