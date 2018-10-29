import requests
import re
import pymongo
import random
import time
import json
import random
import numpy as np
import csv
import pandas as pd
from fake_useragent import UserAgent
import socket  # 断线重试
from urllib.parse import urlencode
# 随机ua
ua = UserAgent()

# mongodb数据库初始化
client = pymongo.MongoClient('localhost', 27017)
# 获得数据库
db = client.ITjuzi
# 获得集合
mongo_collection1 = db.itjuzi_investevent
mongo_collection2 = db.itjuzi_company
mongo_collection3 = db.itjuzi_investment
mongo_collection4 = db.itjuzi_horse


class itjuzi(object):
    def __init__(self):

        self.headers = {
            'User-Agent': ua.random,
            'X-Requested-With': 'XMLHttpRequest',
            # 主页cookie
            'Cookie': '你的cookie',
        }

        # self.url = 'http://radar.itjuzi.com/investevent/info?'    # investevent
        self.url = 'http://radar.itjuzi.com/company/infonew?'   # company
        # self.url = 'http://radar.itjuzi.com/investment/info?'   # investment
        # self.url = 'https://www.itjuzi.com/horse'               # horse

        self.session = requests.Session()

    def get_table(self, page):
        """
        1 获取投融资事件网页内容
        """
        params = {                # 1 invsestevent
        'location': 'in',
        'orderby': 'def',
        'page': page,
        'date':2014  #年份   2018 65页; 2017 451页ok; 2016 618页
        }

        # # # # # # # # # # # # # # # # # # # # # # # # # ## # # # # # # # # # # #

        # params = {                  # 2 company
        #     'page': page,
        #     # 'scope[]': 1,  # 行业 1教育
        #     'orderby': 'pv',
        #     'born_year[]': 2016,  # 只能单年，不能多年筛选，会保留最后一个
        #                             # 2018 65页 2017 332/6621 590/111792
        # }

        # # # # # # # # # # # # # # # # # # # # # # # # ## # # # # # # # # # # #
        # params = {                  # 3 investment  359页
        # 'orderby': 'num',
        # 'page': page
        # }

        # # # # # # # # # # # # # # # # # # # # # # # # # ## # # # # # # # # # # #
        # params = {                  # 4 horse 1页

        # }

        # 可能会遇到请求失败，则设置3次重新请求
        retrytimes = 3
        while retrytimes:
            try:
                response = self.session.get(
                    self.url, params=params, headers=self.headers,timeout = (5,20)).json()
                self.save_to_mongo(response)
                break
            except socket.timeout:
                print('下载第{}页，第{}次网页请求超时' .format(page,retrytimes))
                retrytimes -=1


    def save_to_mongo(self, response):
        try:

            data = response['data']['rows']  # dict可以连续选取字典层内的内容
            # data =response  # 爬取千里马时需替换为此data
            df = pd.DataFrame(data)

            table = json.loads(df.T.to_json()).values()
            if mongo_collection1.insert_many(table):      # investevent
            # if mongo_collection2.insert_many(table):    # company
            # if mongo_collection3.insert_many(table):    # investment
            # if mongo_collection4.insert_many(table):    # horse

                print('存储到mongodb成功')
                sleep = np.random.randint(3, 7)
                time.sleep(sleep)
        except Exception:
            print('存储到mongodb失败')


    def spider_itjuzi(self, start_page, end_page):
        for page in range(start_page, end_page):
            print('下载第%s页:' % (page))
            self.get_table(page)

        print('下载完成')


if __name__ == '__main__':
    spider = itjuzi()

    spider.spider_itjuzi(1, 3)