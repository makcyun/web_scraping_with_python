#-*- coding: utf-8 -*-

import urllib
import requests
from requests.exceptions import RequestException
import re
from bs4 import BeautifulSoup
import json
import time
from lxml import etree

# 教程参考
# https://mp.weixin.qq.com/s?__biz=MzI5NDY1MjQzNA==&mid=2247483860&idx=1&sn=9cc3e4a6b3a98e7fb60e13fa47c4769d&chksm=ec5edea9db2957bf3864d2c84d205f9f1a90130b8d11b3ad17d5e9717c421e28f384b878b2f9&scene=21#wechat_redirect


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        # 不加headers爬不了
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        return None


# 1 用正则提取内容
def parse_one_page(html):
    pattern = re.compile(
        '<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    # re.S表示匹配任意字符，如果不加.无法匹配换行符
    items = re.findall(pattern, html)
    # print(items)
    for item in items:
        yield {
            'index': item[0],
            'thumb': get_thumb(item[1]),
            'name': item[2],
            'star': item[3].strip()[3:],
            # 'time': item[4].strip()[5:],
            # 用函数分别提取time里的日期和地区
            'time': get_release_time(item[4].strip()[5:]),
            'area': get_release_area(item[4].strip()[5:]),
            'score': item[5].strip() + item[6].strip()
        }

        # 用yield的好处是可以迭代，利于多页输出


# 2 用lxml结合xpath提取内容
# https://mp.weixin.qq.com/s/LlT1vZFypn-kGKS57Qz0qA 豆瓣图书爬虫
def parse_one_page2(html):
    parse = etree.HTML(html)
    items = parse.xpath('//*[@id="app"]//div//dd')
    # 完整的是//*[@id="app"]/div/div/div[1]/dl/dd
    # print(type(items))
    # *代表匹配所有节点，@表示属性
    # 第一个电影是dd[1],要提取页面所有电影则去掉[1]
    # xpath://*[@id="app"]/div/div/div[1]/dl/dd[1]
    # lst = []
    for item in items:
        yield{
            'index': item.xpath('./i/text()')[0],
            #./i/text()前面的点表示从items节点开始
            #/text()提取文本
            'thumb': get_thumb(str(item.xpath('./a/img[2]/@data-src')[0].strip())),
            # 'thumb': 要在network中定位，在elements里会写成@src而不是@data-src，从而会报list index out of range错误。
            'name': item.xpath('./a/@title')[0],
            'star': item.xpath('.//p[@class = "star"]/text()')[0].strip(),
            'time': get_release_time(item.xpath(
                './/p[@class = "releasetime"]/text()')[0].strip()[5:]),
            'area': get_release_area(item.xpath(
                './/p[@class = "releasetime"]/text()')[0].strip()[5:]),
            'score' : item.xpath('.//p[@class = "score"]/i[1]/text()')[0] + \
            item.xpath('.//p[@class = "score"]/i[2]/text()')[0]
        }

        # lst.append({'index': index, 'thumb': thumb,
        # 'name': name, 'star': star, 'time': time, 'area': area, 'score': score})

    # frame = pd.DataFrame(lst)
    # print(frame.head())


# 3 用beautifulsoup + css选择器提取
def parse_one_page3(html):
    soup = BeautifulSoup(html, 'lxml')
    # print(content)
    # print(type(content))
    # print('------------')
    items = range(10)
    for item in items:
        yield{

            'index': soup.select('dd i.board-index')[item].string,
            # iclass节点完整地为'board-index board-index-1',写board-index即可
            'thumb': get_thumb(soup.select('a > img.board-img')[item]["data-src"]),
            # 表示a节点下面的class =
            # board-img的img节点,注意浏览器eelement里面是src节点，而network里面是data-src节点，要用这个才能正确返回值

            'name': soup.select('.name a')[item].string,
            'star': soup.select('.star')[item].string.strip()[3:],
            'time': get_release_time(soup.select('.releasetime')[item].string.strip()[5:]),
            'area': get_release_area(soup.select('.releasetime')[item].string.strip()[5:]),
            'score': soup.select('.integer')[item].string + soup.select('.fraction')[item].string

        }


# 4 用beautifulsoup + find_all提取
def parse_one_page4(html):
    soup = BeautifulSoup(html, 'lxml')
    items = range(10)
    for item in items:
        yield{

            'index': soup.find_all(class_='board-index')[item].string,
            'thumb': soup.find_all(class_='board-img')[item].attrs['data-src'],
            # 用.get('data-src')获取图片src链接，或者用attrs['data-src']
            'name': soup.find_all(name='p', attrs={'class': 'name'})[item].string,
            'star': soup.find_all(name='p', attrs={'class': 'star'})[item].string.strip()[3:],
            'time': get_release_time(soup.find_all(class_='releasetime')[item].string.strip()[5:]),
            'area': get_release_time(soup.find_all(class_='releasetime')[item].string.strip()[5:]),
            'score': soup.find_all(name='i', attrs={'class': 'integer'})[item].string.strip() + soup.find_all(name='i', attrs={'class': 'fraction'})[item].string.strip()


        }

# -----------------------------------------------------------------------------


# 提取时间函数
def get_release_time(data):
    pattern = re.compile(r'(.*?)(\(|$)')
    items = re.search(pattern, data)
    if items is None:
        return '未知'
    return items.group(1)  # 返回匹配到的第一个括号(.*?)中结果即时间


# 提取国家函数
def get_release_area(data):
    pattern = re.compile(r'.*\((.*)\)')
    # $表示匹配一行字符串的结尾，这里就是(.*?)；\(|$,表示匹配字符串含有(,或者只有(.*?)
    items = re.search(pattern, data)
    if items is None:
        return '未知'
    return items.group(1)


# 获取封面大图
# http://p0.meituan.net/movie/5420be40e3b755ffe04779b9b199e935256906.jpg@160w_220h_1e_1c
# 去掉@160w_220h_1e_1c就是大图
def get_thumb(url):
    pattern = re.compile(r'(.*?)@.*?')
    thumb = re.search(pattern, url)
    return thumb.group(1)


# 数据存储到csv
def write_to_file(items):
    with open('猫眼top100.csv', 'a', encoding='utf_8_sig') as f:
        # 'a'为追加模式（添加）
        # utf_8_sig格式导出csv不乱码
        f.write(json.dumps(items, ensure_ascii=False) + '\n')
        print('第%s部电影爬取完毕' % items['index'])
        # items是字典形式，需用json.dumps转为字符串
        # json.dumps存数据时会使用unicode的16进制格式，所以中文在保存文件中是\u开头的,添加ensure_ascii =
        # False，即可保留中文


def write_to_file2(item):
    with open('猫眼top100.csv', 'a', encoding='utf_8_sig', newline='') as f:
        # 'a'为追加模式（添加）
        # utf_8_sig格式导出csv不乱码
        fieldnames = ['index', 'thumb', 'name',
                      'star', 'time', 'area', 'score']
        w = csv.DictWriter(f, fieldnames=fieldnames)
        # w.writeheader()
        w.writerow(item)


# 数据存储到csv4
def write_to_file3(item):
    with open('猫眼top100.csv', 'a', encoding='utf_8_sig', newline='') as f:
        w = csv.writer(f)
        # w.writerow(dict.keys())
        w.writerow(item.values())
        # 添加newline=''防止产生空行


# 封面下载
def download_thumb(name, url, num):
    try:
        response = requests.get(url)
        with open('封面图/' + name + '.jpg', 'wb') as f:
            f.write(response.content)
            print('第%s部电影封面下载完毕' % num)
            print('------')
    except RequestException as e:
        print(e)
        pass
     # 不能是w，否则会报错，图片是二进制数所以要用wb


def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    # print(html)
    # parse_one_page2(html)

    for item in parse_one_page(html):  # 切换内容提取方法
        print(item)
        # write_to_file(item)

        # 下载封面图
        # download_thumb(item['name'], item['thumb'],item['index'])


# if __name__ == '__main__':
#     for i in range(10):
#         main(i * 10)
        # time.sleep(0.5)
        # 猫眼增加了反爬虫，设置0.5s的延迟时间

# 2 使用多进程提升抓取效率
from multiprocessing import Pool
if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 10 for i in range(1)])


# 可视化分析
# -----------------------------------------------------------------------------
# 1电影评分最高top10
# import pandas as pd
# import matplotlib.pyplot as plt
# import pylab as pl  #用于修改x轴坐标


# plt.style.use('ggplot')   #默认绘图风格很难看，替换为好看的ggplot风格
# fig = plt.figure(figsize=(8,5))   #设置图片大小
# colors1 = '#6D6D6D'  #设置图表title、text标注的颜色

# columns = ['index', 'thumb', 'name', 'star', 'time', 'area', 'score']  #设置表头
# df = pd.read_csv('maoyan_top100.csv',encoding = "utf-8",header = None,names =columns,index_col = 'index')  #打开表格
# # index_col = 'index' 将索引设为index

# def annalysis_1():
#     df_score = df.sort_values('score',ascending = False)  #按得分降序排列

#     name1 = df_score.name[:10]      #x轴坐标
#     score1 = df_score.score[:10]    #y轴坐标
#     plt.bar(range(10),score1,tick_label = name1)  #绘制条形图，用range()能搞保持x轴正确顺序
#     plt.ylim ((9,9.8))  #设置纵坐标轴范围
#     plt.title('电影评分最高top10',color = colors1) #标题
#     plt.xlabel('电影名称')      #x轴标题
#     plt.ylabel('评分')          #y轴标题

#     # 为每个条形图添加数值标签
#     for x,y in enumerate(list(score1)):
#         plt.text(x,y+0.01,'%s' %round(y,1),ha = 'center',color = colors1)

#     pl.xticks(rotation=270)   #x轴名称太长发生重叠，旋转为纵向显示
#     plt.tight_layout()    #自动控制空白边缘，以全部显示x轴名称
#     # plt.savefig('电影评分最高top10.png')   #保存图片
#     plt.show()



# # ------------------------------
# # 2各国家的电影数量比较
# def annalysis_2():
#     area_count = df.groupby(by = 'area').area.count().sort_values(ascending = False)

#     # 绘图方法1
#     area_count.plot.bar(color = '#4652B1')  #设置为蓝紫色
#     pl.xticks(rotation=0)   #x轴名称太长重叠，旋转为纵向


#     # 绘图方法2
#     # plt.bar(range(11),area_count.values,tick_label = area_count.index)

#     for x,y in enumerate(list(area_count.values)):
#         plt.text(x,y+0.5,'%s' %round(y,1),ha = 'center',color = colors1)
#     plt.title('各国/地区电影数量排名',color = colors1)
#     plt.xlabel('国家/地区')
#     plt.ylabel('数量(部)')
#     plt.show()
# # plt.savefig('各国(地区)电影数量排名.png')


# # ------------------------------
# # 3电影作品数量集中的年份
# # 从日期中提取年份
# def annalysis_3():
#     df['year'] = df['time'].map(lambda x:x.split('/')[0])
#     # print(df.info())
#     # print(df.head())

#     # 统计各年上映的电影数量
#     grouped_year = df.groupby('year')
#     grouped_year_amount = grouped_year.year.count()
#     top_year = grouped_year_amount.sort_values(ascending = False)


#     # 绘图
#     top_year.plot(kind = 'bar',color = 'orangered') #颜色设置为橙红色
#     for x,y in enumerate(list(top_year.values)):
#         plt.text(x,y+0.1,'%s' %round(y,1),ha = 'center',color = colors1)
#     plt.title('电影数量年份排名',color = colors1)
#     plt.xlabel('年份(年)')
#     plt.ylabel('数量(部)')

#     plt.tight_layout()
#     # plt.savefig('电影数量年份排名.png')

#     plt.show()

# # ------------------------------
# # 4拥有电影作品数量最多的演员
# #表中的演员位于同一列，用逗号分割符隔开。需进行分割然后全部提取到list中
# def annalysis_4():
#     starlist = []
#     star_total = df.star
#     for i in df.star.str.replace(' ','').str.split(','):
#         starlist.extend(i)
#     # print(starlist)
#     # print(len(starlist))

#     # set去除重复的演员名
#     starall = set(starlist)
#     # print(starall)
#     # print(len(starall))

#     starall2 = {}
#     for i in starall:
#         if starlist.count(i)>1:
#             # 筛选出电影数量超过1部的演员
#             starall2[i] = starlist.count(i)

#     starall2 = sorted(starall2.items(),key = lambda starlist:starlist[1] ,reverse = True)

#     starall2 = dict(starall2[:10])  #将元组转为字典格式

#     # 绘图
#     x_star = list(starall2.keys())      #x轴坐标
#     y_star = list(starall2.values())    #y轴坐标

#     plt.bar(range(10),y_star,tick_label = x_star)
#     pl.xticks(rotation = 270)
#     for x,y in enumerate(y_star):
#         plt.text(x,y+0.1,'%s' %round(y,1),ha = 'center',color = colors1)

#     plt.title('演员电影作品数量排名',color = colors1)
#     plt.xlabel('演员')
#     plt.ylabel('数量(部)')
#     plt.tight_layout()
#     plt.show()
# # plt.savefig('演员电影作品数量排名.png')

# annalysis_1()