#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-10-28 13:52:54

"""
分析部分

"""

import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import jieba
import os
from PIL import Image
from os import path


plt.style.use('ggplot')
fig= plt.figure(figsize=(8,5))
# fig,ax = plt.subplots(figsize=(16,9))
ax1 = fig.add_subplot(1,1,1)
colors = '#6D6D6D'  #设置标题颜色为灰色
color_line = '#CC2824'
# colors = '#242424'  #设置标题颜色为灰色
fontsize_title = 20
fontsize_text = 10

# 数据清洗处理
#  # #  # #  # #  # #  # #  # #  # #  # #  # #  # #  # #  # #  # #  # #  # #
def parse_huxiu():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['Huxiu']
    collection = db['huxiu_news']

    # 将数据库数据转为dataframe
    data = pd.DataFrame(list(collection.find()))

    # 删除无用的_id列
    data.drop(['_id'],axis=1,inplace=True)
    # 删除特殊符号©
    data['name'].replace('©','',inplace=True,regex=True)

    # 判断整行是否有重复值
    # print(any(data.duplicated()))
    # 显示yes，表明有重复值，进一步提取出重复值数量
    data_duplicated = data.duplicated().value_counts()
    # print(data_duplicated) # 显示2 True ，表明有2个重复值
    # 删除重复值
    data = data.drop_duplicates(keep='first')

    # # 判断整行是否有缺失值，显示为true，表示有，进一步检查每行每列空值个数
    # print(any(data.isnull()))
    # # 查看每列缺失值个数
    # data_colnull = data.shape[0] - data.count()
    # print(data_colnull) #ok

    # # 查看每行缺失值个数,数量太多,不用
    # data_rownull = data.shape[1] - data.count(axis=1)
    # print(data_rownull)


    # 将是数值列的改为数值列
    data = data.apply(pd.to_numeric,errors='ignore')

    # 修改时间,并转换为 datetime 格式
    # data = data[data['write_time'].str.contains('.*小时前')]
    data['write_time'] = data['write_time'].replace('.*前','2018-10-31',regex=True)
    # data = data[data['write_time'].str.contains('.*天前')]
    data['write_time'] = pd.to_datetime(data['write_time'])


    # 删除部分行后，index中断，需重新设置index
    # data.index = (range(len(data.index)))
    # 或者
    data = data.reset_index(drop=True)

    # 增加标题长度列
    data['title_length'] = data['title'].apply(len)
    # 年份列
    data['year'] = data['write_time'].dt.year

    # print(data.shape)  # 查看行数和列数
    # print(data.info())
    # print(data)

    return data


# 以下是分析部分
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 查看总体概括、文章发布变化
def analysis1(data):
    # # 汇总统计
    # print(data.describe())
    # print(data['name'].describe())
    # print(data['write_time'].describe())

    data.set_index(data['write_time'],inplace=True)
    data = data.resample('Q').count()['name'] #以季度汇总
    data = data.to_period('Q')

    # 创建x,y轴标签
    x = np.arange(0,len(data),1)
    ax1.plot(x,data.values, #x、y坐标
        color = color_line , #折线图颜色为红色
        marker = 'o',markersize = 4 #标记形状、大小设置
        )
    ax1.set_xticks(x) # 设置x轴标签为自然数序列
    ax1.set_xticklabels(data.index) # 更改x轴标签值为年份
    plt.xticks(rotation=90) # 旋转90度，不至太拥挤

    for x,y in zip(x,data.values):
        plt.text(x,y + 10,'%.0f' %y,ha = 'center',color = colors,fontsize=fontsize_text )
        # '%.0f' %y 设置标签格式不带小数
    # 设置标题及横纵坐标轴标题
    plt.title('虎嗅网文章数量发布变化(2012-2018)',color = colors,fontsize=fontsize_title)
    plt.xlabel('时期')
    plt.ylabel('文章(篇)')
    plt.tight_layout()  # 自动控制空白边缘
    plt.savefig('虎嗅网文章数量发布变化.png',dpi=200)
    plt.show()


# 2 文章收藏量分析
def analysis2(data):
    # # 总收藏排名
    # top = data.sort_values(['favorites'],ascending = False)
    # # 收藏前100
    # top.index = (range(1,len(top.index)+1)) # 重置index，并从1开始编号
    # print(top[:100][['title','favorites','comment']])

    # 评论前100
    # top = data.sort_values(['comment'],ascending = False)
    # top.index = (range(1,len(top.index)+1)) # 重置index，并从1开始编号
    # print(top[:10][['title','favorites','comment']])

    # 按年份排名
    # # 增加一列年份列
    # data['year'] = data['write_time'].dt.year
    def topn(data):
        top = data.sort_values('favorites',ascending=False)
        return top[:3]

    data = data.groupby(by=['year']).apply(topn)
    print(data[['title','favorites']])

    # 增加每年top123列，列依次值为1、2、3
    data['add'] = 1 # 辅助
    data['top'] = data.groupby(by='year')['add'].cumsum()

    # 参考刘顺祥p122
    data_reshape = data.pivot_table(index='year',columns='top',values='favorites').reset_index()
    print(data_reshape)  # ok
    data_reshape.plot(
        y=[1,2,3],
        kind='bar',
        width=0.3,
        color=['#1362A3','#3297EA','#8EC6F5']  # 设置不同的颜色
        )
    # 添加x轴标签
    years = data['year'].unique()
    plt.xticks(list(range(7)),years)
    plt.xlabel('Year')
    plt.ylabel('文章收藏数量')
    plt.title('历年 TOP3 文章收藏量比较',color = colors,fontsize=fontsize_title)
    plt.tight_layout()  # 自动控制空白边缘
    plt.savefig('历年TOP3文章收藏量比较.png',dpi=200)
    plt.show()



# 3 发文最多的媒体 top20
def analysis3(data):
    data = data.groupby(data['name'])['title'].count()
    data = data.sort_values(ascending=False)
    print(data)

    # 1 pandas 直接绘制,.invert_yaxis()颠倒顺序
    data[1:21].plot(kind='barh',color=color_line).invert_yaxis()

    for y,x in enumerate(list(data[1:21].values)):
        plt.text(x+12,y+0.2,'%s' %round(x,1),ha='center',color=colors)
    plt.xlabel('文章数量')
    plt.ylabel('作者')
    plt.title('发文数量最多的 TOP20 作者',color = colors,fontsize=fontsize_title)
    plt.tight_layout()
    plt.savefig('发文数量最多的TOP20作者.png',dpi=200)
    plt.show()


# 4 发文超过至少5篇以上的作者的文章平均收藏数排名
def analysis4(data):
    data = pd.pivot_table(data,values=['favorites'],index='name',aggfunc=[np.sum,np.size])
    data['avg'] = data[('sum','favorites')]/data[('size','favorites')]

    # 平均收藏数取整
    # data['avg'] = data['avg'].round(decimals=1)
    data['avg'] = data['avg'].astype('int')

    # flatten 平铺列
    data.columns = data.columns.get_level_values(0)
    data.columns = ['total_favorites','ariticls_num','avg_favorites']

    # 筛选出文章数至少5篇的
    data=data.query('ariticls_num > 4')
    data = data.sort_values(by=['avg_favorites'],ascending=False)

    # 查看平均收藏率第一名详情
    data = data.query('name == "重读"')
    # 查看平均收藏率倒数第一名详情
    data = data.query('name == "Yang Yemeng"')
    print(data[['title','favorites','write_time']])

    print(data[:10])
    print(data[-10:])


# 5 收藏和评论的分布直方图
def analysis5(data):
    # 1 matplot做，添加不了kde线
    # plt.hist(data['favorites'],bins=50)
    # plt.hist(data['comment'],bins=50)

    # 2pandas做
    # data['favorites'].plot(kind='hist',bins=50,edgecolor='grey',normed=True,label='所有文章收藏分布图')
    # data['favorites'].plot(kind='kde')

    # 用seaborn做简单
    sns.distplot(data['favorites'])
    plt.tight_layout()  # 自动控制空白边缘，以全部显示x轴名称
    plt.show()


# 6 散点图查看收藏和评论数的关系，发现个别异常
def analysis6(data):
    plt.scatter(data['favorites'],data['comment'],s=8,color='#1362A3')
    plt.xlabel('文章收藏量')
    plt.ylabel('文章评论数')
    plt.title('文章评论数与收藏量关系',color = colors,fontsize=fontsize_title)
    plt.tight_layout()  # 自动控制空白边缘，以全部显示x轴名称
    plt.savefig('文章评论数与收藏量关系.png',dpi=200)
    plt.show()


# 7 查看标题长度与收藏量的关系
def analysis7(data):
    plt.scatter(
        x=data['favorites'],
        y =data['title_length'],
        s=8,
        )
    plt.xlabel('文章收藏量')
    plt.ylabel('文章标题长度')
    plt.title('文章收藏量和标题长度关系',color = colors,fontsize=fontsize_title)
    plt.tight_layout()  # 自动控制空白边缘，以全部显示x轴名称
    plt.savefig('文章收藏量和标题长度关系.png',dpi=200)
    plt.show()

# 8 查看标题长度与收藏量和评论数之间的关系
def analysis8(data):
    # data = data[data['title_length'] < 50]
    # print(data1)

    plt.scatter(
        x=data['favorites'],
        y =data['comment'],
        s=data['title_length']/2,
        )
    plt.xlabel('文章收藏量')
    plt.ylabel('文章评论数')
    plt.title('文章标题长度与收藏量和评论数之间的关系',color = colors,fontsize=fontsize_title)
    plt.tight_layout()  # 自动控制空白边缘，以全部显示x轴名称
    plt.show()

# 9 词云
def analysis9(data):
    jieba.load_userdict("userdict.txt")
    jieba.add_word('区块链')

    text=''
    for i in data['title'].values:
    # for i in data[data.year == 2018]['title'].values:
        # 替换无用字符
        symbol_to_replace = '[!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
        # data['name'].str.replace(symbol_to_replace,'',inplace=True,regex=True)
        i = re.sub(symbol_to_replace,'',i)
        # print(i)
        text+=' '.join(jieba.cut(i,cut_all=False))

    # text = jieba.del_word('如何')
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

    background_Image = np.array(Image.open(path.join(d, "tiger.png")))
    # background_Image = plt.imread('E:\my_Python\training\1exercise\tiger.png')

    font_path = 'C:\Windows\Fonts\SourceHanSansCN-Regular.otf'  # 思源黑,黑体simhei.ttf
    # 添加stopswords
    stopwords = set()
    # 先运行对text进行词频统计再排序，再选择要增加的停用词
    stopwords.update(['如何','怎么','一个','什么','为什么','还是','我们','为何','可能','不是','没有','哪些','成为','可以','背后','到底','就是','这么','不要','怎样','为了','能否','你们','还有','这样','这个','真的','那些'])

    wc = WordCloud(
        # background_color = '#3F3F3F',
        # background_color = 'white',
        background_color = 'black',
        font_path = font_path,
        mask = background_Image,
        stopwords = stopwords,
        max_words = 200,
        # width = 1000,height=600,
        margin =2,
        max_font_size = 100,
        random_state = 42,
        scale = 2,
        # colormap = 'viridis'
    )
    wc.generate_from_text(text)

    process_word = WordCloud.process_text(wc, text)
    # 下面是字典排序
    sort = sorted(process_word.items(),key=lambda e:e[1],reverse=True) # sort为list
    print(sort[:50])  # 输出前词频最高的前50个，然后筛选出不需要的stopwords，添加到前面的stopwords.update()方法中
    img_colors = ImageColorGenerator(background_Image)
    wc.recolor(color_func=img_colors)  # 颜色跟随图片颜色

    plt.imshow(wc,interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()  # 自动控制空白边缘，以全部显示x轴名称
    plt.savefig('huxiu5.png',dpi=200)
    plt.show()

# 10 绘制标题形式饼图
def analysis10(data):
    data1 = data[data['title'].str.contains("(.*\？.*)|(.*\?.*)")]
    data2 = data[data['title'].str.contains("(.*\！.*)|(.*\!.*)")]

    # 带有问号的标题数量
    quantity1 = data1.shape[0]
    # 带有叹号的标题数量
    quantity2 = data2.shape[0]
    # 剩余数量
    quantity = data.shape[0] - data1.shape[0] - data2.shape[0]

    sizes = [quantity2,quantity1,quantity]
    labels = [u'叹号标题',u'问号标题',u'陈述性标题']
    colors_pie = ['#1362A3','#3297EA','#8EC6F5'] #每块颜色定义
    explode = [0,0.05,0]
    plt.pie(
        sizes,
        autopct='%.1f%%',
        labels= labels,
        colors =colors_pie,
        shadow = False, #无阴影设置
        startangle =90, #逆时针起始角度设置
        explode = explode,
        # textprops={'fontsize': 14, 'color': 'w'} # 设置文字颜色
        textprops={'fontsize': 12, 'color': 'w'} # 设置文字颜色
        )
    plt.title('三分之一文章的标题喜欢用问号',color=colors,fontsize=fontsize_title)

    plt.axis('equal')

    plt.axis('off')
    plt.legend(loc = 'upper right')
    plt.tight_layout()  # 自动控制空白边缘，以全部显示x轴名称
    plt.savefig('title问号.png',dpi=200)
    plt.show()


if __name__ == '__main__':
    # parse_huxiu() # test ok
    data = parse_huxiu()
    analysis1(data)



