#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/26 0026 12:36            
 @Author:xxx
 @Version:1.0
 @Desciption:
"""
import pymysql


class MysqlDb:
    def __init__(self, mysql_config):
        """
        数据库初始化
        :param mysql_config:数据库配置
        """
        # 数据库连接
        self.conn = pymysql.connect(**mysql_config)

    def create_table(self, sql):
        """
        创建sql表
        :param sql:sql语句
        :return:
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
        except Exception as e:
            print(e)
            print("创建失败!!!")

    def insert(self, table, data_list):
        """
        插入信息,当插入相同数据时进行更新数据
        :param table:表名
        :param data_list:数据
        :return:
        """
        keys = ', '.join(data_list[0].keys())
        values = ', '.join(['%s'] * len(data_list[0]))
        sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
                             DUPLICATE KEY UPDATE""".format(table=table,
                                                            keys=keys,
                                                            values=values)
        update = ','.join([
            ' {key} = values({key})'.format(key=key)
            for key in data_list[0]
        ])
        sql += update
        with self.conn.cursor() as cursor:
            cursor.executemany(
                sql, [tuple(data.values()) for data in data_list])
            self.conn.commit()
    def select_by_Id(self,table_name,key,id):
        """
        通过id查询内容
        :param table_name:表名
        :param id:id
        :return: 查询结果返回类型为元组
        """
        sql='select * from {} where {}={};'.format(table_name,key,id)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            res=cursor.fetchall()
            if len(res):
                return res
            else:
                print('未查找到数据')
                return None
    def select_All_Userid(self,key):
        """
        专门用于查询用户名的所有userid
        :return: 查询结果
        """
        sql="""select {} from user""".format(','.join(key));
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            res=cursor.fetchall()
            if len(res):
                return res
            else:
                print('未查找到数据')
                return None
    def __del__(self):
        """
        关闭连接
        :return:
        """
        if self.conn:
            self.conn.close()
