#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-26 09:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @blog    : http://www.makcyun.top

"""
爬取豌豆荚网站所有分类下的全部 app
数据爬取包括两个部分：
一：数据指标
1 爬取首页
2 爬取第2页开始的 ajax 页

二：图标
使用class方法下载首页和 ajax 页

分页循环两种爬取思路，
指定页数进行for 循环，和不指定页数一直往下爬直到爬不到内容为止

1 for 循环

"""

import scrapy
from wandoujia.items import WandoujiaItem

import requests
from pyquery import PyQuery as pq
import re
import csv
import pandas as pd
import numpy as np
import time
import pymongo
import json
import os
from urllib.parse import urlencode
import random
import logging

logging.basicConfig(filename='wandoujia.log',filemode='w',level=logging.DEBUG,format='%(asctime)s %(message)s',datefmt='%Y/%m/%d %I:%M:%S %p')
# https://juejin.im/post/5aee70105188256712786b7f
logging.warning("warn message")
logging.error("error message")


class WandouSpider(scrapy.Spider):
    name = 'wandou'
    allowed_domains = ['www.wandoujia.com']
    start_urls = ['http://www.wandoujia.com/']

    def __init__(self):
        self.cate_url = 'https://www.wandoujia.com/category/app'
        # 首页url
        self.url = 'https://www.wandoujia.com/category/'
        # ajax 请求url
        self.ajax_url = 'https://www.wandoujia.com/wdjweb/api/category/more?'
        # 实例化分类标签
        self.wandou_category = Get_category()

    def start_requests(self):
        yield scrapy.Request(self.cate_url,callback=self.get_category)
        
    def get_category(self,response):    
        # # num = 0
        cate_content = self.wandou_category.parse_category(response)
        for item in cate_content:
            child_cate = item['child_cate_codes']
            for cate in child_cate:
                cate_code = item['cate_code']
                cate_name = item['cate_name']
                child_cate_code = cate['child_cate_code']
                child_cate_name = cate['child_cate_name']

      
        # # 单类别下载
        # cate_code = 5029
        # child_cate_code = 837
        # cate_name = '通讯社交'
        # child_cate_name = '收音机'
        
                # while循环
                page = 1 # 设置爬取起始页数
                print('*' * 50)

                # # for 循环下一页
                # pages = []
                # for page in range(1,3):
                # print('正在爬取：%s-%s 第 %s 页 ' %
                # (cate_name, child_cate_name, page))
                logging.debug('正在爬取：%s-%s 第 %s 页 ' %
                (cate_name, child_cate_name, page))

                if page == 1:
                    # 构造首页url
                    category_url = '{}{}_{}' .format(self.url, cate_code, child_cate_code)
                else:
                    params = {
                    'catId': cate_code,  # 大类别
                    'subCatId': child_cate_code,  # 小类别
                    'page': page,
                    }
                    category_url = self.ajax_url + urlencode(params)

                dict = {'page':page,'cate_name':cate_name,'cate_code':cate_code,'child_cate_name':child_cate_name,'child_cate_code':child_cate_code}
                    
                yield scrapy.Request(category_url,callback=self.parse,meta=dict)
                            
                #     # for 循环方法
                #     pa = yield scrapy.Request(category_url,callback=self.parse,meta=dict)
                #     pages.append(pa)
                # return pages

    def parse(self, response):
        if len(response.body) >= 100:  # 判断该页是否爬完，数值定为100是因为无内容时长度是87
            page = response.meta['page']
            cate_name = response.meta['cate_name']
            cate_code = response.meta['cate_code']
            child_cate_name = response.meta['child_cate_name']
            child_cate_code = response.meta['child_cate_code']

            if page == 1:
                contents = response
            else:
                jsonresponse = json.loads(response.body_as_unicode())
                contents = jsonresponse['data']['content']
                # response 是json,json内容是html，html 为文本不能直接使用.css 提取，要先转换
                contents = scrapy.Selector(text=contents, type="html")

            contents = contents.css('.card')
            for content in contents:
                # num += 1
                item = WandoujiaItem()
                item['cate_name'] = cate_name
                item['child_cate_name'] = child_cate_name
                item['app_name'] = self.clean_name(content.css('.name::text').extract_first())
                item['install'] = content.css('.install-count::text').extract_first()
                item['volume'] = content.css('.meta span:last-child::text').extract_first()
                item['comment'] = content.css('.comment::text').extract_first().strip()
                item['icon_url'] = self.get_icon_url(content.css('.icon-wrap a img'),page)
                yield item
            
            # 递归爬下一页
            page += 1
            params = {
                    'catId': cate_code,  # 大类别
                    'subCatId': child_cate_code,  # 小类别
                    'page': page,
                    }
            ajax_url = self.ajax_url + urlencode(params)
            
            dict = {'page':page,'cate_name':cate_name,'cate_code':cate_code,'child_cate_name':child_cate_name,'child_cate_code':child_cate_code}
            yield scrapy.Request(ajax_url,callback=self.parse,meta=dict)
                


        # 名称清除方法1 去除不能用于文件命名的特殊字符
    def clean_name(self, name):
        rule = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |')
        name = re.sub(rule, '', name)
        return name

    def get_icon_url(self,item,page):
        if page == 1:
            if item.css('::attr("src")').extract_first().startswith('https'):
                url = item.css('::attr("src")').extract_first()
            else:
                url = item.css('::attr("data-original")').extract_first()
        # ajax页url提取
        else:
            url = item.css('::attr("data-original")').extract_first()

        # if url:  # 不要在这里添加url存在判断，否则空url 被过滤掉 导致编号对不上
        return url


# 首先获取主分类和子分类的数值代码 # # # # # # # # # # # # # # # #
class Get_category():
    def parse_category(self, response):
        category = response.css('.parent-cate')
        data = [{
            'cate_name': item.css('.cate-link::text').extract_first(),
            'cate_code': self.get_category_code(item),
            'child_cate_codes': self.get_child_category(item),
        } for item in category]
        return data

    # 获取所有主分类标签数值代码
    def get_category_code(self, item):
        cate_url = item.css('.cate-link::attr("href")').extract_first()

        pattern = re.compile(r'.*/(\d+)')  # 提取主类标签代码
        cate_code = re.search(pattern, cate_url)
        return cate_code.group(1)

    # 获取所有子分类标签数值代码
    def get_child_category(self, item):
        child_cate = item.css('.child-cate a')
        child_cate_url = [{
            'child_cate_name': child.css('::text').extract_first(),
            'child_cate_code': self.get_child_category_code(child)
        } for child in child_cate]

        return child_cate_url

    # 正则提取子分类
    def get_child_category_code(self, child):
        child_cate_url = child.css('::attr("href")').extract_first()
        pattern = re.compile(r'.*_(\d+)')  # 提取小类标签编号
        child_cate_code = re.search(pattern, child_cate_url)
        return child_cate_code.group(1)

    # # 可以选择保存到txt 文件
    # def write_category(self,category):
    #     with open('category.txt','a',encoding='utf_8_sig',newline='') as f:
    #         w = csv.writer(f)
    #         w.writerow(category.values())

