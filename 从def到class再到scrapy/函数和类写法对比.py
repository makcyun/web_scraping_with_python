#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-6 15:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top
# @Version : $Id$


"""
16:从 def 到 Class

案例1 爬取豆瓣电影 top 250
案例2 登陆 IT 桔子
案例3 遍历爬取虎嗅文章

"""

# 案例1 豆瓣电影# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import requests
import json
import csv
import pandas as pd
from urllib.parse import urlencode


def get_content(start_page):
    url = 'https://api.douban.com/v2/movie/top250?'
    params = {
        'start': start_page,
        'count': 50
    }
    response = requests.get(url, params=params).json()
    movies = response['subjects']
    data = [{
        'rating': item['rating']['average'],
        'genres':item['genres'],
        'name':item['title'],
        'actor':get_actor(item['casts']),
        'original_title':item['original_title'],
        'year':item['year'],
    } for item in movies]
    write_to_file(data)


def get_actor(actors):
    actor = [i['name'] for i in actors]
    return actor


def write_to_file(data):
    with open('douban3.csv', 'a', encoding='utf_8_sig', newline='') as f:
        w = csv.writer(f)
        for item in data:
            w.writerow(item.values())


def get_douban(total_movie):
    # 每页50条，start_page循环5次
    for start_page in range(0, total_movie, 50):
        get_content(start_page)


if __name__ == '__main__':
    get_douban(250)


# # # # # # # # # # # # # # # # # #
# 类写法
class Douban(object):

    def __init__(self):
        self.url = 'https://api.douban.com/v2/movie/top250?'

    def get_content(self, start_page):
        params = {
            'start': start_page,
            'count': 50
        }
        response = requests.get(self.url, params=params).json()
        movies = response['subjects']
        data = [{
            'rating': item['rating']['average'],
            'genres':item['genres'],
            'name':item['title'],
            'actor':self.get_actor(item['casts']),
            'original_title':item['original_title'],
            'year':item['year'],
        } for item in movies]
        self.write_to_file(data)

    def get_actor(self, actors):
        actor = [i['name'] for i in actors]
        return actor

    def write_to_file(self, data):
        with open('douban_class.csv', 'a', encoding='utf_8_sig', newline='') as f:
            w = csv.writer(f)
            for item in data:
                w.writerow(item.values())

    def get_douban(self, total_movie):
        # 每页50条，start_page循环5次
        for start_page in range(0, total_movie, 50):
            self.get_content(start_page)

if __name__ == '__main__':
    douban = Douban()
    douban.get_douban(250)


# 案例2 IT桔子 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
browser = webdriver.Chrome()
browser.maximize_window()  # 最大化窗口
wait = WebDriverWait(browser, 10)  # 等待加载10s


def login():
    browser.get('https://www.itjuzi.com/user/login')
    account = browser.find_element(By.ID, "create_account_email")
    password = browser.find_element(By.ID, "create_account_password")
    account.send_keys('irw27812@awsoo.com')  # 输入账号和密码
    password.send_keys('test2018')
    submit = browser.find_element(By.ID, "login_btn")
    submit.click()  # 点击登录按钮
    get_content()


def get_content():
    browser.get('http://radar.itjuzi.com/investevent')
    print(browser.page_source)  # 输出网页源码

if __name__ == '__main__':
    login()

# # # # # # # # # # # # # # # # # #
# 类写法


class Spider(object):

    def __init__(self, account, password):
        self.login_url = 'https://www.itjuzi.com/user/login'
        self.get_url = 'http://radar.itjuzi.com/investevent'
        self.account = account
        self.password = password

    def login(self):
        browser.get(self.login_url)
        account = browser.find_element(By.ID, "create_account_email")
        password = browser.find_element(By.ID, "create_account_password")
        account.send_keys(self.account)  # 输入账号和密码
        password.send_keys(self.password)
        submit = browser.find_element(By.ID, "login_btn")
        submit.click()  # 点击登录按钮
        self.get_content()   # 调用下面的方法

    def get_content(self):
        browser.get(self.get_url)
        print(browser.page_source)  # 输出网页源码

if __name__ == '__main__':
    spider = Spider(account='irw27812@awsoo.com', password='test2018')
    # 当有其他账号时，在这里更改即可,很方便
    # spider = Spider('fru68354@nbzmr.com','test2018')
    spider.login()


# 案例3 虎嗅文章 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import requests
import json
import time
import numpy as np
from pyquery import PyQuery as pq
import csv
import pymongo
import pandas as pd

client = pymongo.MongoClient('localhost', 27017)
db = client.Huxiu
mongo_collection = db.huxiu_news


class Huxiu(object):
    """docstring for huxi"""

    def __init__(self):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.url = 'https://www.huxiu.com/v2_action/article_list'

    def get_content(self, page):
        data = {
            # 'huxiu_hash_code': 'a8c7c945779d0a320bbf2c43efadfa18',
            'page': page,
            # 'last_dateline': 1540514164
        }
        response = requests.post(self.url, data=data, headers=self.headers)

        # 或者
        # # 解决response.text输出中文显示为二进制
        # data = json.loads(response.text)
        # data = json.dumps(data,ensure_ascii=False)
        # # 将json再度解码为dict
        # data = json.loads(data)

        sleep = np.random.randint(1, 5)
        time.sleep(sleep)

        self.parse_content(response)

    def parse_content(self, response):
        content = response.json()['data']
        # 注意，在sublime中，json后面需要添加()，pyspider 中则不用
        #content = response.json()['data']
        doc = pq(content)
        # print(doc)
        lis = doc('.mod-art').items()

        data = [{
            'title': item('.msubstr-row2').text(),
            'url': 'https://www.huxiu.com' + str(item('.msubstr-row2').attr('href')),
            'name': item('.author-name').text(),
            'write_time': item('.time').text(),
            'comment': item('.icon-cmt+ em').text(),
            'favorites': item('.icon-fvr+ em').text(),
            'abstract': item('.mob-sub').text()
        } for item in lis]  # 列表生成式结果返回每页提取出25条字典信息构成的list

        print(data)
        # self.save_to_file2(data)

    # 存储到csv
    def save_to_file(self, data):
        with open('huxiu.csv', 'a', encoding='utf_8_sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(data.values())

    # 存储到 mongodb
    def save_to_file2(self, data):
        df = pd.DataFrame(data)
        content = json.loads(df.T.to_json()).values()

        if mongo_collection.insert_many(content):
            print('存储到 mongondb 成功')
        else:
            print('存储失败')

    def get_huxiu(self, start_page, end_page):
        for page in range(start_page, end_page):
            print('正在爬取第 %s 页' % page)
            self.get_content(page)


if __name__ == '__main__':
    huxiu = Huxiu()
    huxiu.get_huxiu(1, 2000)


# # # # # # # # # # # # # # # # # #
# pyspider写法
from pyspider.libs.base_handler import *
import json
from pyquery import PyQuery as pq
import pandas as pd
import pymongo
from pyspider.libs.utils import md5string
import time
import numpy as np


client = pymongo.MongoClient('localhost', 27017)
db = client.Huxiu
mongo_collection = db.huxiu_pyspider2


class Handler(BaseHandler):
    crawl_config:
        {
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        }

    # 修改taskid，避免只下载一个post请求
    def get_taskid(self, task):
        return md5string(task['url'] + json.dumps(task['fetch'].get('data', '')))

    #@every(minutes=24 * 60)
    def on_start(self):
        for page in range(1, 2000):
            print('正在爬取第 %s 页' % page)
            self.crawl('https://www.huxiu.com/v2_action/article_list',
                       method='POST', data={'page': page}, callback=self.index_page)

    def index_page(self, response):
        content = response.json['data']

        doc = pq(content)
        lis = doc('.mod-art').items()
        data = [{
            'title': item('.msubstr-row2').text(),
            'url': 'https://www.huxiu.com' + str(item('.msubstr-row2').attr('href')),
            'name': item('.author-name').text(),
            'write_time': item('.time').text(),
            'comment': item('.icon-cmt+ em').text(),
            'favorites': item('.icon-fvr+ em').text(),
            'abstract': item('.mob-sub').text()
        } for item in lis]

        # 上面用了列表生成式，可参考binux
        # https://binux.blog/2015/01/pyspider-tutorial-level-2-ajax-and-more-http/
        return data

        # method2，可以为直接接save_to_mongo
        # self.save_to_mongo(data)

    def on_result(self, result):
        if result:
            self.save_to_mongo(result)

    def save_to_mongo(self, result):
        df = pd.DataFrame(result)
        print(df)
        content = json.loads(df.T.to_json()).values()
        if mongo_collection.insert_many(content):
            print('存储到 mongondb 成功')

            # 设置随机暂停
            sleep = np.random.randint(1, 5)
            time.sleep(sleep)
