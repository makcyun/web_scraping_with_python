# 下载网页中的图片

import requests
from bs4 import BeautifulSoup
import re
import os
from hashlib import md5
from requests.exceptions import RequestException
from multiprocessing import Pool
from urllib.parse import urlencode


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }


def get_page_index():
    # 下载1页
    url = 'http://data.163.com/special/datablog/'
    # 增加异常捕获语句
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
            # print(response.text)  # 测试网页内容是否提取成功
    except RequestException:
        print('网页请求失败')
        return None


def parse_page_index(html):

    pattern = re.compile(r'"url":"(.*?)".*?"title":"(.*?)".*?"img":"(.*?)".*?"time":"(.*?)".*?"comment":(.*?),',re.S)

    items = re.findall(pattern,html)
    # print(items)
    for item in items:
        yield{
        'url':item[0],
        'title':item[1],
        'img':item[2],
        'time':item[3],
        'comment':item[4][1:-1]
        }

def get_page_detail(item):
    url = item.get('url')
        # 增加异常捕获语句
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            # print(url) #测试url ok
            return response.text
    except RequestException:
        print('网页请求失败')
        return None


# 4 BeautifulSoup.find_all
# # 这种提取方式对部分图片失效，所以不能采用该法
def parse_page_detail(html):
    soup = BeautifulSoup(html,'lxml')
    # 获取title
    title = soup.h1.string
    # 每个网页只能拥有一个<H1>标签,因此唯一
    item = soup.find_all(name='img',width =['100%','600'])
    # print(item) # 测试

    for i in range(len(item)):
        pic = item[i].attrs['src']
        yield{
        'title':title,
        'pic':pic,
        'num':i  # 图片添加编号顺序
        }
        # print(pic) #测试图片链接ok

def parse_page_detail2(html):
    soup = BeautifulSoup(html,'lxml')
    items = soup.select('p > a > img')
    # print(len(items))
    title = soup.h1.string
    for i in range(len(items)):
        pic = items[i].attrs['src']
        yield{
        'title':title,
        'pic':pic,
        'num':i  # 图片添加编号顺序
        }

def save_pic(pic):
    title = pic.get('title')
    title = re.sub('[\/:*?"<>|]','-',title)
    url = pic.get('pic')
    # 设置图片编号顺序
    num = pic.get('num')

    if not os.path.exists(title):
        os.mkdir(title)


    # 获取图片url网页信息
    response = requests.get(url,headers = headers)
    try:
    # 建立图片存放地址
        if response.status_code == 200:
            file_path = '{0}\{1}.{2}' .format(title,num,'jpg')
            file_path = '{0}\{1}.{2}' .format(title,num,'jpg')
            # 文件名采用编号方便按顺序查看，而未采用哈希值md5(response.content).hexdigest()
            if not os.path.exists(file_path):
                # 开始下载图片
                with open(file_path,'wb') as f:
                    f.write(response.content)
                    print('该图片已下载完成',title)
            else:
                print('该图片%s 已下载' %title)
    except RequestException as e:
        print(e,'图片获取失败')
        return None


def main():
    # get_page_index() # 测试网页内容是获取成功
    html = get_page_index()
    # parse_page_index(html) # 测试网页内容是否解析成功

    data = parse_page_index(html)
    dict = []
    for item in data:
    #     # print(item) #测试dict
        dict.append(item)

    for item in dict:
        # get_page_detail(item) #测试url ok
        html = get_page_detail(item)
        if html:
            # parse_page_detail3(html)
            data = parse_page_detail2(html)
            if data:
                for pic in data:
                    # print(pic)
                    save_pic(pic)

# 单进程
if __name__ == '__main__':
    main()

# 多进程
# if __name__ == '__main__':
    # pool = Pool()
    # pool.map(main,[i for i in range(1,2)])
    # pool.close()
    # pool.join()