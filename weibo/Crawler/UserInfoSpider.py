#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/26 0026 13:03            
 @Author:LG
 @Version:1.0
 @Desciption:微博用户信息爬取
"""
import random
import re
import sys
from collections import OrderedDict
from time import sleep

from weibo.config import sqlDb,PROXY
import requests,json
from queue import Queue
import threading
class UserInfoSpider:
    def __init__(self):
        self.sqldb=sqlDb
        self.create_userInfo()
        self.user_id_list=[]
        self.user_dic={}
        self.q_userinfo_url=Queue()
        self.userinfo_list = []
        self.count=0
        self.save_count=0
        self.sleep_count=0
        self.headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000'
        }
        self.run()
    def Get_user_id(self):
        key=['user_id','screen_name']
        user_tuple=self.sqldb.select_All_Userid(key)
        self.user_dic={x[0]:x[1] for x in user_tuple}
        self.user_id_list=[x[0] for x in user_tuple]

    def create_userInfo(self):
        # 创建'user'表
        sql = """
                CREATE TABLE IF NOT EXISTS userinfo (
                id int NOT NULL AUTO_INCREMENT,
                user_id varchar(20),
                screen_name varchar(30),
                gender varchar(10),
                statuses_count INT,
                followers_count INT,
                follow_count INT,
                registration_time varchar(20),
                sunshine varchar(20),
                birthday varchar(40),
                location varchar(200),
                education varchar(200),
                company varchar(200),
                description varchar(400),
                profile_url varchar(200),
                profile_image_url varchar(200),
                avatar_hd varchar(200),
                urank INT,
                mbrank INT,
                verified BOOLEAN DEFAULT 0,
                verified_type INT,
                verified_reason varchar(140),
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
    def userinfo_to_mysql(self,userinfo_list):
        self.sqldb.insert('userinfo', data_list=userinfo_list)
    def get_json(self,url):
        proxy = random.choice(PROXY)  # 本地代理
        proxies = {
            'http': 'http://' + proxy,
        }
        try:

            r = requests.get(url, headers=self.headers, proxies=proxies)
            return r.json()
        except:
            print('这里遇到反爬措施,即将暂停爬虫一会')
            # 等待2分钟
            sleep(120)

    def parse_userinfo(self,js):
        if js['ok']:
            info = js['data']['userInfo']
            user_info = OrderedDict()
            user_info['user_id'] = self.user_id
            user_info['screen_name'] = info.get('screen_name', '')
            user_info['gender'] = '女' if info.get('gender', '')=='f' else '男'
            userinfo_url='https://m.weibo.cn/api/container/getIndex?containerid=230283{}_-_INFO'.format(self.user_id)
            zh_list = [
                u'生日', u'所在地', u'小学', u'初中', u'高中', u'大学', u'公司', u'注册时间',
                u'阳光信用'
            ]
            en_list = [
                'birthday', 'location', 'education', 'education', 'education',
                'education', 'company', 'registration_time', 'sunshine'
            ]
            for i in en_list:
                user_info[i] = ''
            js = self.get_json(userinfo_url)
            if js['ok']:
                cards = js['data']['cards']
                if isinstance(cards, list) and len(cards) > 1:
                    card_list = cards[0]['card_group'] + cards[1]['card_group']
                    for card in card_list:
                        if card.get('item_name') in zh_list:
                            user_info[en_list[zh_list.index(
                                card.get('item_name'))]] = card.get(
                                'item_content', '')
            user_info['statuses_count'] = info.get('statuses_count', 0)
            user_info['followers_count'] = info.get('followers_count', 0)
            user_info['follow_count'] = info.get('follow_count', 0)
            user_info['description'] = info.get('description', '')
            user_info['profile_url'] = info.get('profile_url', '')
            user_info['profile_image_url'] = info.get('profile_image_url', '')
            user_info['avatar_hd'] = info.get('avatar_hd', '')
            user_info['urank'] = info.get('urank', 0)
            user_info['mbrank'] = info.get('mbrank', 0)
            user_info['verified'] = info.get('verified', False)
            user_info['verified_type'] = info.get('verified_type', -1)
            user_info['verified_reason'] = info.get('verified_reason', '')
            user_info = self.standardize_info(user_info)
            return user_info
    def get_userinfo(self):
        while True:
            if self.q_userinfo_url.empty():
                break
            page_url=self.q_userinfo_url.get()
            self.user_id=re.search('containerid=100505(\d+)',page_url)[1]
            js=self.get_json(page_url)
            if js:
                userinfo=self.parse_userinfo(js)
                if userinfo:
                    self.count+=1
                    self.userinfo_list.append(userinfo)
                    print('正在爬取id为{},用户名为{}的用户信息......'.format(self.user_id,self.user_dic[self.user_id]))
            else:
                self.q_userinfo_url.put(page_url)
            if self.count%20==0:
                userinfo_lst=self.userinfo_list[self.save_count:self.count]
                self.save_count=self.count
                self.userinfo_to_mysql(userinfo_lst)
                print('已经存储了{}条数据'.format(self.count))
            self.q_userinfo_url.task_done()
            random_pages = random.randint(1, 5)
            if (self.count - self.sleep_count) % random_pages == 0:
                sleep(random.randint(6, 10))
                self.sleep_count = self.count
                random_pages = random.randint(1, 5)
    def run(self):
        self.Get_user_id()
        for user_id in self.user_id_list:
            url='https://m.weibo.cn/api/container/getIndex?containerid=100505{}'.format(user_id)
            self.q_userinfo_url.put(url)
        thread_list=[]
        for i in range(5):
            Treq_spi = threading.Thread(target=self.get_userinfo())
            thread_list.append(Treq_spi)
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        for q in [self.q_userinfo_url]:
            q.join()
        print('结束')
if __name__ == '__main__':
    UserInfoSpider()