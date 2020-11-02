#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/23 0023 22:09            
 @Author:LG
 @Version:1.0
 @Desciption:配置
"""
MAX_PAGE = 99

# cookie信息
from taobao.Client.dbcookie import CookieMongo
cookieDb = CookieMongo()
#商品信息
from taobao.Client.dbproduct import ProductMongo
productDb=ProductMongo()