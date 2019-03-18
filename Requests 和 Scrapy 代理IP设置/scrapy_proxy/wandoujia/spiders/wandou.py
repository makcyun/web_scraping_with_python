#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-26 09:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @blog    : http://www.makcyun.top


"""
Scrapy 代理 IP 设置
代理方法1：使用middlewares 设置中间件
代理方法2：使用阿布云付费代理
代理方法3：使用 scrapy-proxies 库

测试每种方法时，需注释掉另外两种方法
建议使用方法1和2

运行方法：
建议使用vscode，右键：在终端运行python 文件
输入以下命令并回车
scrapy crawl wandou
"""

import scrapy
from wandoujia.items import WandoujiaItem
import requests
import re
import random
import logging

logging.basicConfig(filename='wandoujia.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
# https://juejin.im/post/5aee70105188256712786b7f
logging.warning("warn message")
logging.error("error message")


class WandouSpider(scrapy.Spider):
    name = 'wandou'
    allowed_domains = ['www.wandoujia.com']
    start_urls = ['http://www.wandoujia.com/']

    def __init__(self):
        self.cate_url = 'https://icanhazip.com'

    def start_requests(self):
        items = []
        for i in range(1, 6):
            print('第%s次请求'%i)
            item = yield scrapy.Request(self.cate_url, callback=self.get_category)
            items.append(item)
        return items

    def get_category(self, response):
        print(response.text)
