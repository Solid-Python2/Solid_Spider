#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/24 0024 9:15            
 @Author:LG
 @Version:1.0
 @Desciption:商品MongoDB
"""
import pymongo
class ProductMongo():
    def __init__(self):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = client["taobao"]
        self.product_set=None
    def set_key(self,key):
        """
        设置集合
        :param key:集合名
        :return:
        """
        self.product_set=self.db[key]
    def delete_all(self,query_dict):
        """
        删除商品
        :param query_dict: 条件
        :return:
        """
        self.product_set.delete_many(query_dict)
    def update(self,id,item):
        """
        插入或修改数据
        :param id: 商品id
        :param item: 商品信息字典
        :return:
        """
        self.product_set.update({'product_id':id},{'$set':item},True)
    def count(self):
        """
        统计库中已有数据的条数
        :return:
        """
        self.product_set.count_documents({})