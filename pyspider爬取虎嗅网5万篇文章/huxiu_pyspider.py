#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-10-27 20:56:23
# Project: huxiu

"""
虎嗅新闻爬虫
https://www.huxiu.com/

https://www.huxiu.com/v2_action/article_list
每页 25条
https://binux.blog/2015/01/pyspider-tutorial-level-2-ajax-and-more-http/
截至2018.11.1 2002页

"""
from pyspider.libs.base_handler import *
import json
from pyquery import PyQuery as pq
import pandas as pd
import pymongo
from pyspider.libs.utils import md5string
import time
import numpy as np


client = pymongo.MongoClient('localhost',27017)
db = client.Huxiu
mongo_collection = db.huxiu_pyspider

class Handler(BaseHandler):
    crawl_config:{
        "headers":{
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }
    }

    # 修改taskid，避免只下载一个post请求
    def get_taskid(self,task):
        return md5string(task['url']+json.dumps(task['fetch'].get('data','')))

    #@every(minutes=24 * 60)
    def on_start(self):
        for page in range(2,2002):
            # print(len(query_list)/100)
            self.crawl('https://www.huxiu.com/v2_action/article_list',method='POST',data={'page':page}, callback=self.index_page)

    def index_page(self, response):
        content = response.json['data']
        doc = pq(content)
        lis = doc('.mod-art').items()
        data = [{
            'title': item('.msubstr-row2').text(),
            'url':'https://www.huxiu.com'+ str(item('.msubstr-row2').attr('href')),
            'name': item('.author-name').text(),
            'write_time':item('.time').text(),
            'comment':item('.icon-cmt+ em').text(),
            'favorites':item('.icon-fvr+ em').text(),
            'abstract':item('.mob-sub').text()
            } for item in lis ]

        #上面用了列表生成式，可参考binux
        # https://binux.blog/2015/01/pyspider-tutorial-level-2-ajax-and-more-http/
        return data

        #method2，可以为直接接save_to_mongo
        #self.save_to_mongo(data)


    def on_result(self,result):
        if result:
            self.save_to_mongo(result)

    def save_to_mongo(self,result):
        df = pd.DataFrame(result)
        # print(df)
        content = json.loads(df.T.to_json()).values()
        # print(content)
        if mongo_collection.insert_many(content):
            print('存储到 mongondb 成功')

            # 随机暂停
            sleep = np.random.randint(1,5)
            time.sleep(sleep)


