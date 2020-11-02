#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Modify Time: 2020/10/26 0026 13:03            
 @Author:LG
 @Version:1.0
 @Desciption:获取用户指定时间段的微博
"""
import random
import re
import sys
from lxml import etree
from collections import OrderedDict
from datetime import date, timedelta, datetime
from time import sleep

from weibo.config import *
import requests,json
from queue import Queue
import threading
class UserBlogSpider:
    def __init__(self):
        self.sqldb = sqlDb
        self.create_userBlog()
        self.user_id_list = []
        self.user_dic = {}
        self.since_date=since_date
        self.since_date_list={}
        self.filter=filter
        self.q_userblog_url = Queue()
        self.userblog_list = []
        self.weibo_id_list = []  # 存储爬取到的所有微博id
        self.count = 0
        self.save_count = 0
        self.sleep_count = 0
        self.headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.6.1000'
        }
        self.run()

    def Get_user_id(self):
        key = ['user_id', 'screen_name','since_date']
        user_tuple = self.sqldb.select_All_Userid(key)
        self.user_dic = {x[0]: x[1] for x in user_tuple}
        self.user_id_list = [x[0] for x in user_tuple]
        if self.since_date:
            if isinstance(self.since_date, int):
                self.since_date = date.today() - timedelta(self.since_date)
            self.since_date=str(self.since_date)
            self.since_date_list={x[0]:self.since_date for x in user_tuple}
        else:
            self.since_date_list = {x[0]: x[2] for x in user_tuple}
    def create_userBlog(self):
        # 创建'user'表
        sql = """
                CREATE TABLE IF NOT EXISTS weibo (
                id int NOT NULL AUTO_INCREMENT,
                blog_id varchar(20) NOT NULL,
                bid varchar(12) NOT NULL,
                user_id varchar(20),
                screen_name varchar(30),
                text varchar(2000),
                article_url varchar(100),
                topics varchar(200),
                at_users varchar(1000),
                pics varchar(3000),
                video_url varchar(1000),
                location varchar(100),
                created_at DATETIME,
                source varchar(30),
                attitudes_count INT,
                comments_count INT,
                reposts_count INT,
                retweet_id varchar(20),
                PRIMARY KEY (id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        self.sqldb.create_table(sql)
    def userblog_to_mysql(self,userblog_list):
        self.sqldb.insert('weibo', data_list=userblog_list)
    def get_json(self, url):
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
    def is_date(self, since_date):
        """判断日期格式是否正确"""
        try:
            datetime.strptime(since_date, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    def get_long_weibo(self, id):
        """获取长微博"""
        for i in range(5):
            url = 'https://m.weibo.cn/detail/%s' % id
            html = requests.get(url,self.headers).text
            html = html[html.find('"status":'):]
            html = html[:html.rfind('"hotScheme"')]
            html = html[:html.rfind(',')]
            html = '{' + html + '}'
            js = json.loads(html, strict=False)
            weibo_info = js.get('status')
            if weibo_info:
                weibo = self.parse_weibo(weibo_info)
                return weibo
            sleep(random.randint(6, 10))
    def get_pics(self, weibo_info):
        """获取微博原始图片url"""
        if weibo_info.get('pics'):
            pic_info = weibo_info['pics']
            pic_list = [pic['large']['url'] for pic in pic_info]
            pics = ','.join(pic_list)
        else:
            pics = ''
        return pics

    def get_live_photo(self, weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        live_photo = weibo_info.get('pic_video')
        if live_photo:
            prefix = 'https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/'
            for i in live_photo.split(','):
                if len(i.split(':')) == 2:
                    url = prefix + i.split(':')[1] + '.mov'
                    live_photo_list.append(url)
            return live_photo_list

    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ''
        video_url_list = []
        if weibo_info.get('page_info'):
            if weibo_info['page_info'].get('media_info') and weibo_info[
                'page_info'].get('type') == 'video':
                media_info = weibo_info['page_info']['media_info']
                video_url = media_info.get('mp4_720p_mp4')
                if not video_url:
                    video_url = media_info.get('mp4_hd_url')
                    if not video_url:
                        video_url = media_info.get('mp4_sd_url')
                        if not video_url:
                            video_url = media_info.get('stream_url_hd')
                            if not video_url:
                                video_url = media_info.get('stream_url')
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return ';'.join(video_url_list)
    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def get_article_url(self, selector):
        """获取微博中头条文章的url"""
        article_url = ''
        text = selector.xpath('string(.)')
        if text.startswith(u'发布了头条文章'):
            url = selector.xpath('//a/@data-url')
            if url and url[0].startswith('http://t.cn'):
                article_url = url[0]
        return article_url

    def get_topics(self, selector):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ','.join(topic_list)
        return topics
    def get_at_users(self, selector):
        """获取@用户"""
        a_list = selector.xpath('//a')
        at_users = ''
        at_list = []
        for a in a_list:
            if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                at_list.append(a.xpath('string(.)')[1:])
        if at_list:
            at_users = ','.join(at_list)
        return at_users
    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        weibo_info = info['mblog']
        title = weibo_info.get('title')
        if title and title.get('text') == u'置顶':
            return True
        else:
            return False
    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = int(string[:-2] + '0000')
        elif string.endswith(u'万'):
            string = int(string[:-1] + '0000')
        return int(string)
    def standardize_date(self, created_at):
        """标准化微博发布时间"""
        if u'刚刚' in created_at:
            created_at = datetime.now().strftime('%Y-%m-%d')
        elif u'分钟' in created_at:
            minute = created_at[:created_at.find(u'分钟')]
            minute = timedelta(minutes=int(minute))
            created_at = (datetime.now() - minute).strftime('%Y-%m-%d')
        elif u'小时' in created_at:
            hour = created_at[:created_at.find(u'小时')]
            hour = timedelta(hours=int(hour))
            created_at = (datetime.now() - hour).strftime('%Y-%m-%d')
        elif u'昨天' in created_at:
            day = timedelta(days=1)
            created_at = (datetime.now() - day).strftime('%Y-%m-%d')
        elif created_at.count('-') == 1:
            year = datetime.now().strftime('%Y')
            created_at = year + '-' + created_at
        return created_at
    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u'\u200b', '').encode(
                    sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
        return weibo
    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = ''
            weibo['screen_name'] = ''
        weibo['blog_id'] = int(weibo_info['id'])
        weibo['bid'] = weibo_info['bid']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        weibo['text'] = etree.HTML(text_body).xpath('string(.)')
        weibo['article_url'] = self.get_article_url(selector)
        weibo['pics'] = self.get_pics(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        weibo['topics'] = self.get_topics(selector)
        weibo['at_users'] = self.get_at_users(selector)
        return self.standardize_info(weibo)

    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info['mblog']
            weibo_id = weibo_info['id']
            retweeted_status = weibo_info.get('retweeted_status')
            is_long = weibo_info.get('isLongText')
            if retweeted_status and retweeted_status.get('id'):  # 转发
                retweet_id = retweeted_status.get('id')
                is_long_retweet = retweeted_status.get('isLongText')
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
                if is_long_retweet:
                    retweet = self.get_long_weibo(retweet_id)
                    if not retweet:
                        retweet = self.parse_weibo(retweeted_status)
                else:
                    retweet = self.parse_weibo(retweeted_status)
                retweet['created_at'] = self.standardize_date(
                    retweeted_status['created_at'])
                weibo['retweet'] = retweet
            else:  # 原创
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
            weibo['created_at'] = self.standardize_date(
                weibo_info['created_at'])
            return weibo
        except Exception as e:
            print('get_one_weibo')
            print(e)
    def get_one_page(self,weibo,user_id,page):
        try:
            url='https://m.weibo.cn/api/container/getIndex?containerid=107603{}&page={}'.format(user_id,page)
            js = self.get_json(url)
            if js['ok']:
                weibos = js['data']['cards']
                for w in weibos:
                    if w['card_type'] == 9:
                        wb = self.get_one_weibo(w)
                        if wb:
                            if wb['blog_id'] in self.weibo_id_list:
                                continue
                            created_at = datetime.strptime(
                                wb['created_at'], '%Y-%m-%d')
                            since_date = datetime.strptime(self.since_date_list[user_id], '%Y-%m-%d')
                            if created_at < since_date:
                                if self.is_pinned_weibo(w):
                                    continue
                                else:
                                    print(u'{}已获取{}({})的第{}页微博{}'.format(
                                        '-' * 30, self.user_dic[user_id],
                                        user_id, page, '-' * 30))
                                    return True
                            if (not self.filter) or (
                                    'retweet' not in wb.keys()):
                                weibo.append(wb)
                            else:
                                print(u'正在过滤转发微博')
            print(u'{}已获取{}({})的第{}页微博{}'.format(
                '-' * 30, self.user_dic[user_id],
                user_id, page, '-' * 30))
        except Exception as e:
            print('get_one_page')
            print(e)

    def get_pages(self,user_id,page_count):
        try:
            since_date = datetime.strptime(self.since_date_list[user_id],'%Y-%m-%d')
            today = datetime.strptime(str(date.today()), '%Y-%m-%d')
            if since_date <= today:
                wrote_count = 0
                page1 = 0
                random_pages = random.randint(1, 5)
                weibo = []
                count=0
                for page in range(1, page_count + 1):
                    is_end = self.get_one_page(weibo,user_id,page)
                    if is_end:
                        break
                    if page % 20 == 0:  # 每爬20页写入一次文件
                        userblog_lst = weibo[wrote_count:page]
                        wrote_count = page
                        print(userblog_lst)
                        self.userblog_to_mysql(userblog_lst)
                    if (page - page1) % random_pages == 0:
                        sleep(random.randint(6, 10))
                        page1 = page
                        random_pages = random.randint(1, 5)
                count +=len(weibo)
                print(len(weibo[wrote_count:]))
                self.userblog_to_mysql(weibo[wrote_count:])  # 将剩余不足20页的微博写入文件
            print(u'用户名:{}的微博爬取完成，共爬取{}条微博'.format(self.user_dic[user_id],count))
            self.q_userblog_url.task_done()
        except Exception as e:
            print('get_pages')
            print(e)


    def get_userblog(self):
        while True:
            if self.q_userblog_url.empty():
                break
            page_url = self.q_userblog_url.get()
            self.user_id = re.search('containerid=107603(\d+)', page_url)[1]
            js=self.get_json(page_url)
            try:
                if js['ok']==1:
                    page_count = js.get('data').get('cardlistInfo').get('total',0)
                    self.get_pages(self.user_id,page_count)
                    print(u'{}信息抓取完毕'.format(self.user_dic[self.user_id]))
                    print('*' * 100)
            except Exception as e :
                print('get_userblog')
                print(e)
    def run(self):
        self.Get_user_id()
        for user_id in self.user_id_list:
            url = 'https://m.weibo.cn/api/container/getIndex?containerid=107603{}&page=1'.format(user_id)
            self.q_userblog_url.put(url)
        thread_list = []
        for i in range(2):
            Treq_spi = threading.Thread(target=self.get_userblog())
            thread_list.append(Treq_spi)
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        for q in [self.q_userblog_url]:
            q.join()
        print('结束')
if __name__ == '__main__':
    UserBlogSpider()