#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/26 0026 13:02            
 @Author:LG
 @Version:1.0
 @Desciption:爬取搜索框中所有用户名和id号
"""
import random
from collections import OrderedDict
from datetime import datetime
from time import sleep
import requests,sys
from urllib.parse import quote
from queue import Queue
import threading,re
from weibo.config import *
from fake_useragent import UserAgent


class UserSpider:
    def __init__(self,keyword):
        """
        :param keyword:关键字
        """
        super().__init__()
        self.keyword=keyword
        self.q_page_url=Queue()
        self.sqldb=sqlDb
        self.create_user()
        self.page_sleep=0
        self.ua = UserAgent()
        self.headers={
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000'
        }
        self.run()
    def create_user(self):
        # 创建'user'表
        sql = """ CREATE TABLE IF NOT EXISTS user (
                        id int NOT NULL AUTO_INCREMENT,
                        user_id varchar(20),
                        screen_name varchar(30),
                        since_date varchar(30),
                        PRIMARY KEY (id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        self.sqldb.create_table(sql)
    def standardize_info(self, user):
        """标准化信息，去除乱码"""
        for k, v in user.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                type(v)) and 'long' not in str(type(v)):
                user[k] = v.replace(u'\u200b', '').encode(
                    sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
        return user
    def get_json(self,page_url):
        proxy = random.choice(PROXY)  # 本地代理
        proxies = {
            'http': 'http://' + proxy,
        }
        try:

            r = requests.get(page_url,headers=self.headers,proxies=proxies)
            return r.json()
        except:
            print('这里遇到反爬措施,即将暂停爬虫一会')
            #等待2分钟
            sleep(120)
    def parse_user(self,js):
        user_list=[]
        if js['ok']:
            info = js['data']['cards']
            for u in info:
                if u.get('card_group'):
                    for card in u.get('card_group'):
                        # 有序字典
                        user = OrderedDict()
                        if card['card_type'] == 10:
                            user['user_id'] = card['user'].get('id')
                            user['screen_name'] = card['user'].get('screen_name', '')
                            user['since_date']=str(datetime.now().strftime('%Y-%m-%d'))
                            user=self.standardize_info(user)
                            user_list.append(user)
        print(user_list)
        print('*'*100)
        return user_list
    def user_to_mysql(self,user_list):
        self.sqldb.insert('user',data_list=user_list)
    def get_user(self):
        while True:
            if self.q_page_url.empty():
                break
            page_url=self.q_page_url.get()
            page=re.search('page=(\d+)',page_url)[1]
            js=self.get_json(page_url)
            if js:
                user_list=self.parse_user(js)
                if user_list:
                    self.user_to_mysql(user_list)
                    print('正在爬取第{}页的用户信息......'.format(page))
            else:
                self.q_page_url.put(page_url)
            random_pages = random.randint(1, 5)
            if (int(page) - self.page_sleep) % random_pages == 0:
                sleep(random.randint(6, 10))
                self.page_sleep = int(page)
                random_pages = random.randint(1, 5)
            #每当访问6到10页时暂停
            self.q_page_url.task_done()




    def run(self):
        for page in range(1,100):
            url='https://m.weibo.cn/api/container/getIndex?containerid=100103{}&page_type=searchall&page={}'.format(quote('type=3&q={}&t=0'.format(self.keyword)),page)
            self.q_page_url.put(url)
        thread_list=[]
        for i in range(2):
            Treq_spi = threading.Thread(target=self.get_user())
            thread_list.append(Treq_spi)
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        for q in [self.q_page_url]:
            q.join()
        print('结束')

if __name__ == '__main__':
    UserSpider('迪丽热巴')