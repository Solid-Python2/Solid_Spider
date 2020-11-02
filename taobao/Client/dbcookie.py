#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/10/23 0023 21:12   LG      1.0         存储cookie的数据库
"""
import pymongo
class CookieMongo():
    def __init__(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = client["taobao"]
        self.cookie_set=self.db.cookies

    def insert(self,cookies):
        """
        插入cookie
        :param cookies: cookie值
        :return:
        """
        self.cookie_set.insert_one(cookies)
    def delete_all(self,dict):
        """
        删除大量用户
        :param dict:
        :return:
        """
        self.cookie_set.delete_many(dict)

    def delete(self, user):
        """
        Delete cookies.
        """
        self.cookie_set.delete_one({"user": user})
    def update_cookie_flag(self,user,cookies,t):
        """
        添加用户的cookies到数据库中
        :param user: 用户名
        :param cookies: cookies
        :param t: 超时
        :return:
        """
        self.cookie_set.update({'user': user}, {'$set': {"flag": 0, "cookies": cookies, "time": t}},True)
    def update_cookie_flag2(self,user):
        """
        将该用户标记成暂时不可用
        :param user: 用户名
        :return:
        """
        self.cookie_set.update({'user': user}, {'$set': {"flag": 1}})

    def update_cookie_flag3(self, user):
        """
        将该用户标记成不可用
        :param user: 用户名
        :return:
        """
        self.cookie_set.update({'user': user}, {'$set': {"flag": 2}})
    def find_cookies(self,flag=0):
        """
        查询指定标志的cookies
        :param flag:标志
        :return:如果cookie存在,则输出cookie,反之返回None
        """
        q = self.cookie_set.find_one({"flag": flag})
        if q:
            return q
        else:
            return None
    def get_requests_cookie(self):
        """
        获取请求cookies
        :return:
        """
        q = self.cookie_set.find_one({"flag":0})
        d = {}
        if q:
            cookies = q['cookies']
            for cookie in cookies:
                d[cookie.get('name')] = cookie.get('value')
            return d
        else:
            return None