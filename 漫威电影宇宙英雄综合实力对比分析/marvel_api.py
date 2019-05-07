# -*- coding: utf-8 -*-

"""
漫威电影票房和英雄实力分析
Created on Mon May 5 12:57:10 2019
@author: 高级农民工
@blog: https://www.makcyun.top/data_analysis&mining05.html
"""

import requests
import pandas as pd
import re
from requests.exceptions import RequestException
import time
from multiprocessing import Process, Pool
import pymongo
import os

import threading
from queue import Queue

# https://superheroapi.com/，facebook 登陆即可自动获取token
token = '101939884363403'


def getapi(i):
    url = 'https://superheroapi.com/api/%s/%s' % (token, i)
    data = requests.get(url).json()
    return data


def parseapi(item):
    lst = {
        'id': item['id'],
        'name': item['name'],

        # 提取人物战斗力值
        'intelligence': item['powerstats']['intelligence'],
        'strength': item['powerstats']['strength'],
        'speed': item['powerstats']['speed'],
        'durability': item['powerstats']['durability'],
        'power': item['powerstats']['power'],
        'combat': item['powerstats']['combat'],


        # 提取人物特征
        'gender': item['appearance']['gender'],
        'race': item['appearance']['race'],
        'height': item['appearance']['height'][1],  # 取cm
        'weight': item['appearance']['weight'][1],  # 取kg

        # 提取人物头像url
        'image': item['image']['url'],

        'publisher': item['biography']['publisher'],  # 出版方 Marvel/DC
        'alignment': item['biography']['alignment']  # 正派/反派
    }

    # 写入csv
    write_csv(lst)

    # 或者写入MongoDB
    # write_mongodb(lst)

    # # 下载图片
    image = item['image']['url']
    save(image)


def write_mongodb(lst):
    client = pymongo.MongoClient('localhost', 27017)
    db = client.marvel
    mongo_collection = db.marvel_stats

    if mongo_collection.update_one(lst, {'$set': lst}, upsert=True):
        pass
    else:
        print('存储失败')
    print('id:%s 存储完成' % lst['id'])


def write_csv(lst):
    content = pd.DataFrame([lst])
    content.to_csv('./marvel.csv', mode='a', encoding='utf_8_sig',
                   index=False, header=None)


def save(image):
    # 获取头像编号
    num = re.search('https:.*\/(.*?).jpg', image).group(1)
    dir = os.getcwd() + '\\marvel\\'
    if not os.path.exists(dir):
        os.mkdir(dir)

    file_path = '{0}\\{1}.{2}'.format(dir, num, 'jpg')

    try:
        response = requests.get(image)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
                print('编号：%s下载完成' % num)
    except exceptions:
        pass


def main(i):
    data = getapi(i)
    parseapi(data)


if __name__ == '__main__':
    start = time.time()
    pool = Pool()

    for i in range(1, 732):
        # 多进程非阻塞
        pool.apply_async(main, args=[i, ])

    pool.close()
    pool.join()

    end = time.time()
    print('总共用时{}s'.format((end - start)))
