#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-1-13 09:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top



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
from fake_useragent import UserAgent
ua = UserAgent()

client = pymongo.MongoClient('localhost', 27017)
db = client.wandoujia
mongo_collection = db.wandou

logging.basicConfig(filename='wandoujia.log',filemode='w',level=logging.DEBUG,format='%(asctime)s %(message)s',datefmt='%Y/%m/%d %I:%M:%S %p')

logging.warning("warn message")
logging.error("error message")


headers = {
    'User-Agent': ua.random,
    'X-Requested-With': 'XMLHttpRequest',
}

# 首先获取主分类和子分类的数值代码 # # # # # # # # # # # # # # # #
class Get_category():
    def __init__(self):
        self.url = 'https://www.wandoujia.com/category/app'

    # def get_content(self):
    #     response = requests.get(self.url, headers=headers)
    #     return self.parse_category(response)
    #     # 要添加 return  否则返回空值

    # 第2种方式 获取分类方式，保存到本地txt文件
    def get_content2(self):
        if not os.path.exists('category.txt'):
            response = requests.get(self.url, headers=headers)
            return self.parse_category(response)
            # 要添加 return  否则返回空值
        else:
            print('category.txt 文件已存在')

    def parse_category(self, response):
        doc = pq(response.text)
        category = doc('.parent-cate').items()

        data = [{
            'cate_name': item('.cate-link').text(),
            'cate_code': self.get_category_code(item),
            'child_cate_codes': self.get_child_category(item),
        } for item in category]

        # return data
        # 第二种方式，写入到文件中
        return self.write_category(data)

    # 获取所有主分类标签数值代码
    def get_category_code(self, item):
        cate_url = item('.cate-link').attr('href')

        pattern = re.compile(r'.*/(\d+)')  # 提取主类标签代码
        cate_code = re.search(pattern, cate_url)
        return cate_code.group(1)

    # 获取所有子分类标签数值代码
    def get_child_category(self, item):
        child_cate = item('.child-cate a').items()

        child_cate_url = [{
            'child_cate_name': child.text(),
            'child_cate_code': self.get_child_category_code(child)
        } for child in child_cate]

        return child_cate_url

    # 正则提取子分类
    def get_child_category_code(self, child):
        child_cate_url = child.attr('href')
        pattern = re.compile(r'.*_(\d+)')  # 提取小类标签编号
        child_cate_code = re.search(pattern, child_cate_url)
        return child_cate_code.group(1)

    # 可以选择保存到txt 文件
    def write_category(self, data):
        for item in data:
            child_cates = item['child_cate_codes']
            for cate in child_cates:
                cate_code = item['cate_code']
                cate_name = item['cate_name']
                child_cate_code = cate['child_cate_code']
                child_cate_name = cate['child_cate_name']

                with open('category.txt', 'a', encoding='utf_8_sig', newline='') as f:
                    w = csv.writer(f)
                    w.writerow(
                        [cate_code, cate_name, child_cate_code, child_cate_name])

# # # # # # # # # # # # # # # # # # # # # # # #
class Get_page():
    def __init__(self):
        # 首页url
        self.url = 'https://www.wandoujia.com/category/'
        # 调用 spider 类用于后续数据存储和图标下载
        # ajax 请求url
        self.ajax_url = 'https://www.wandoujia.com/wdjweb/api/category/more'
        self.spider = Spider()

        # 代理ip,需根据自己的替换
        proxies = [{'http': 'socks5://127.0.0.1:1080'}, {'https': 'socks5://127.0.0.1:1080'},
                   {'http': 'http://27.189.203.73:1080'}, {'https': 'https://27.189.203.73:1080'}]
        self.proxies = random.choice(proxies)


    def get_code(self):
        with open('category.txt', 'r', encoding='utf_8_sig', newline='') as f:
            items = []
            for line in f.readlines():
                item = line.strip().split(',')
                items.append(item)
            return items

    def get_page(self, cate_code, child_cate_code, page):
        if page == 1:
            # 构造首页url
            category_url = '{}{}_{}' .format(
                self.url, cate_code, child_cate_code)
            # 不使用代理
            content = requests.get(category_url, headers=headers).text
            # # 使用代理
            # content = requests.get(category_url, headers=headers,proxies=self.proxies).text

        else:
            params = {
                'catId': cate_code,  # 大类别
                'subCatId': child_cate_code,  # 小类别
                'page': page,
            }
            # # 不使用代理
            response = requests.get(
                self.ajax_url, headers=headers, params=params)
            # 使用代理
            # response = requests.get(
                            # self.ajax_url, headers=headers, params=params,proxies=self.proxies)

            content = response.json()['data']['content']
        return content


    def parse_page(self, content, cate_name, child_cate_code, num):
        # 请求和解析网页内容
        contents = pq(content)('.card').items()
        data = []
        for content in contents:
            num += 1
            data1 = {
                'cate_name': cate_name,
                'child_cate_name': child_cate_name,
                'app_name': self.clean_name(content('.name').text()) + str('_%s' % num),
                'install': content('.install-count').text(),
                'volume': content('.meta span:last-child').text(),
                'comment': content('.comment').text(),
                # 图标 url 个坑，url 有所不同需要 if 分别处理
                'icon_url': self.get_icon_url(content('.icon-wrap a img')),
            }
            data.append(data1)
        if data:
            # # 写入MongoDB
            self.spider.write_to_mongodb(data)

            # 写入csv
            # self.spider.write_to_csv(data)

            # 下载图标
            self.spider.download_icon_pic(data)
            return num

    # 名称清除方法1 去除不能用于文件命名的特殊字符
    def clean_name(self, name):
        rule = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |')
        name = re.sub(rule, '', name)
        return name

    def get_icon_url(self, item):
        if page == 1:
            if item.attr("src").startswith('https'):
                url = item.attr("src")
            else:
                url = item.attr('data-original')
        # ajax页url提取
        else:
            url = item.attr('data-original')

        # if url:  # 不要在这里添加url存在判断，否则空url 被过滤掉 导致编号对不上
        return url


class Spider(object):
    def write_to_mongodb(self, data):
        for item in data:
            if mongo_collection.update_one(item, {'$set': item}, upsert=True):
                pass
            else:
                print('本页存储失败')
        print('本页数据存储成功')

    def write_to_csv(self, data):
        with open('wandoujia.csv', 'a', encoding='utf_8_sig', newline='') as f:
            for item in data:
                w = csv.writer(f)
                w.writerow(item.values())
            print('该页数据存储成功')

    def download_icon_pic(self, data):
        icon_num = 0  # 记录下载了多少图片
        for item in data:
            cate_name = item['cate_name']
            child_cate_name = item['child_cate_name']
            name = item['app_name']
            url = item['icon_url']
            if url:  # 增加空url判断
                # 不存在就创建 wandoujia\icon 文件夹
                path1 = os.getcwd()
                path2 = '\icon\%s\%s' % (cate_name, child_cate_name)
                path = path1 + path2

                # 不存在就创建 wandoujia 文件夹,每类图标单独存放
                if not os.path.exists(path):
                    os.makedirs(path)
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        file_path = '{}\{}.{}' .format(
                            path, name, 'jpg')
                        if not os.path.exists(file_path):
                            with open(file_path, 'wb') as f:
                                f.write(response.content)  # 下载icon
                                icon_num += 1
                        else:
                            print('图标 %s 已下载' % name)
                except requests.RequestException as e:
                    print(e.args, '图片下载失败')
                    return None
            else:
                print('图标 %s 不存在' % name)

        print('本页下载了 %s 个图标' % icon_num)
        print('*' * 50)


if __name__ == '__main__':
    # 实例化分类标签
    wandou_category = Get_category()
    # 实例化数据提取类
    wandou_page = Get_page()
    # 实例化数据存储类
    wandou_download = Spider()
    # 获取分类代码
    wandou_category.get_content2()

    num = 0  # 图标编号
    cate_content = wandou_page.get_code()
    for item in cate_content:
        cate_code = item[0]
        cate_name = item[1]
        child_cate_code = item[2]
        child_cate_name = item[3]

        # while 循环下一页
        # # # # # # # # # # # # # # # # # # # # # #
        page = 1  # 设置爬取起始页数
        print('*' * 50)
        while True:
            print('正在爬取：%s-%s 第 %s 页 ' %
                  (cate_name, child_cate_name, page))
            try:
                content = wandou_page.get_page(
                    cate_code, child_cate_code, page)
                # 添加循环判断，如果content 为空表示此页已经下载完成了
                if not content == '':
                    num = wandou_page.parse_page(
                        content, cate_name, child_cate_name, num)
                    page += 1

                    sleep = np.random.randint(3, 6)
                    time.sleep(sleep)

                else:
                    print('该类别已下载完最后一页')
                    break  # 更改page_last 为 True 跳出循环
            except requests.ConnectionError as e:
                print('Error', e.args)


    #         # 也可以用 for 循环
    #         for page in range(1,2):
    #             print('正在爬取：%s-%s 第 %s 页 ' %
    #               (cate_name, child_cate_name, page))

    #             content = wandou_page.get_page(
    #                 cate_code, child_cate_code, page)
    #             # 添加循环判断，如果content 为空表示此页已经下载完成了,break 跳出循环
    #             if not content == '':
    #                 num = wandou_page.parse_page(
    #                     content, cate_name, child_cate_name,num)
    #                 page +=1

    #                 # sleep = np.random.randint(3,6)
    #                 # time.sleep(sleep)

    #             else:
    #                 print('该类别已下载完最后一页')
    #                 break # 跳出循环
