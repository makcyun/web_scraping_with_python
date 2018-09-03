
# 下载所有页的图片

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


# 1 获取索引界面网页内容
def get_page_index(i):
    # 下载1页
    # url = 'https://www.thepaper.cn/newsDetail_forward_2370041'

    # 2下载多页，构造url
    paras = {
        'nodeids': 25635,
        'pageidx': i
    }
    url = 'https://www.thepaper.cn/load_index.jsp?' + urlencode(paras)

    response = requests.get(url,headers = headers)
    if response.status_code == 200:
        return response.text
        # print(response.text)  # 测试网页内容是否提取成功ok



# 2 解析索引界面网页内容

def parse_page_index(html):
    soup = BeautifulSoup(html,'lxml')

    # 获取每页文章数
    num = soup.find_all(name = 'div',class_='news_li')
    for i in range(len(num)):
        yield{
        # 获取title
        'title':soup.select('h2 a')[i].get_text(),
        # 获取图片url，需加前缀
        'url':'https://www.thepaper.cn/' + soup.select('h2 a')[i].attrs['href']
        # print(url)  # 测试图片链接
        }




# 3 获取每条文章的详情页内容
def get_page_detail(item):
    url = item.get('url')
    # 增加异常捕获语句
    try:
        response = requests.get(url,headers = headers)
        if response.status_code == 200:
            return response.text
            # print(response.text)  # 测试网页内容是否提取成功
    except RequestException:
        print('网页请求失败')
        return None


# 4 解析每条文章的详情页内容
def parse_page_detail(html):
    soup = BeautifulSoup(html,'lxml')
    # 获取title
    if soup.h1:  #有的网页没有h1节点，因此必须要增加判断，否则会报错
        title = soup.h1.string
        # 每个网页只能拥有一个<H1>标签,因此唯一
        items = soup.find_all(name='img',width =['100%','600'])
        # 有的图片节点用width='100%'表示，有的用600表示，因此用list合并
        # https://blog.csdn.net/w_xuechun/article/details/76093950
        #
        # print(items) # 测试返回的img节点ok
        for i in range(len(items)):
            pic = items[i].attrs['src']
            # print(pic) #测试图片链接ok
            yield{
            'title':title,
            'pic':pic,
            'num':i  # 图片添加编号顺序
            }

# 5 下载图片
def save_pic(pic):
    title = pic.get('title')
    # 标题规范命名：去掉符号非法字符| 等
    # title = pic.get('title').replace(' ','').replace('|','').replace('？','').replace('“','"').replace('”','"')
    title = re.sub('[\/:*?"<>|]','-',title).strip()
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
            # 文件名采用编号方便按顺序查看，而未采用哈希值md5(response.content).hexdigest()
            if not os.path.exists(file_path):
                # 开始下载图片
                with open(file_path,'wb') as f:
                    f.write(response.content)
                    print('文章"{0}"的第{1}张图片下载完成' .format(title,num))
            else:
                print('该图片%s 已下载' %title)
    except RequestException as e:
        print(e,'图片获取失败')
        return None


# 4 BeautifulSoup.find_all
def parse_page_detail(html):
    soup = BeautifulSoup(html,'lxml')
    if soup.h1:   # 部分文章没有h1 title节点
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



def main(i):
    # get_page_index(i) # 测试索引界面网页内容是否获取成功ok

    html = get_page_index(i)
    data = parse_page_index(html)  # 测试索引界面url是否获取成功ok
    for item in data:
        # print(item)  #测试返回的dict
        html = get_page_detail(item)
        if html:
            data = parse_page_detail(html)
            if data:
                for pic in data:
                    save_pic(pic)

# # 单进程
# if __name__ == '__main__':
#     for i in range(1,26):
#         main(i)


# 多进程
if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[i for i in range(1,26)])
    pool.close()
    pool.join()