#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-11-30 09:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top
# @Version : $Id$


"""
酷安爬虫分析

"""

import pandas as pd
import pymongo
import matplotlib.pyplot as plt
import seaborn as sns
from pyecharts import Bar, Grid, configure
import numpy as np


# 课设置最多显示10行数据
# pd.options.display.max_rows = 10
# 小数精度显示设置
pd.set_option('precision', 1)


plt.style.use('ggplot')  # 设置matplot 绘图风格
colors = '#6D6D6D'
colorline = '#CC2824'
fontsize_title = 20
fontsize_text = 10

configure(global_theme='macarons')  # 设置 pyecharts 绘图主题


def data_processing():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['KuAn']
    collection = db['Kuan2Item']

    # 将数据库数据转为dataframe
    df = pd.DataFrame(list(collection.find()))
    # print(df)
    # print(df.shape)
    # print(df.info())
    # print(df.describe())

    # # 处理'comment','download','follow','num_score','volume' 5列数据，将单位万转换为单位1，再转换为数值型
    str = '_ori'
    cols = ['comment', 'download', 'follow', 'num_score', 'volume']
    for col in cols:
        colori = col + str
        df[colori] = df[col]  # 复制保留原始列
        if not (col == 'volume'):
            df[col] = clean_symbol(df, col)  # 处理原始列生成新列
        else:
            df[col] = clean_symbol2(df, col)  # 处理原始列生成新列

    # 将download单独转换为万单位
    df['download'] = df['download'].apply(lambda x: x / 10000)
    # 批量转为数值型
    df = df.apply(pd.to_numeric, errors='ignore')

    return df


def clean_symbol(df, col):
    # 字符万替换为空
    con = df[col].str.contains('万$')
    df.loc[con, col] = pd.to_numeric(
        df.loc[con, col].str.replace('万', '')) * 10000
    df[col] = pd.to_numeric(df[col])
    return df[col]


def clean_symbol2(df, col):
    # 字符M替换为空
    df[col] = df[col].str.replace('M$', '')
    # 体积为K的除以 1024 转换为M
    con = df[col].str.contains('K$')
    df.loc[con, col] = pd.to_numeric(
        df.loc[con, col].str.replace('K$', '')) / 1024
    df[col] = pd.to_numeric(df[col])
    return df[col]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# pyecharts 图表选项设置
legend_text_size = 16,  # 图例文字大小
legend_text_color = '#aaa'  # 图例文字颜色


# 下载量区间分布
def analysis_general(df):


    df.to_csv('kuan.csv')



    # # # 下载量分布
    # # bins = [0,10,100,500,10000]
    # # group_names = ['<=10万','10-100万','100-500万','>500万']
    # # cats = pd.cut(df['download'],bins,labels=group_names)
    # # cats = pd.value_counts(cats)

    # # 得分分布
    # bins = [0, 3, 4, 4.5, 5]
    # group_names = ['soso(<=3分)', '中品(3-4分)', '良品(4-4.5分)', '精品(4.5-5分)']
    # cats = pd.cut(df['score'], bins, labels=group_names)
    # cats = pd.value_counts(cats)
    # # 按默认顺序更改行序
    # cats = cats.reindex(
    #     index=['soso(<=3分)', '中品(3-4分)', '良品(4-4.5分)', '精品(4.5-5分)'])

    # print(cats)
    # # pyecharts 绘制
    # # bar = Bar('App 下载数量区间分布','绝大部分 App 下载量低于 10 万')
    # bar = Bar('App 得分区间分布', '相当一部分 App 口碑都不错(4 分以上)')

    # # bar.use_theme('macarons')
    # bar.add(
    #     'App 数量 (个)',
    #     list(cats.index),
    #     list(cats.values),
    #     is_label_show=True,
    #     xaxis_interval=0,
    #     xaxis_rotate=0,
    #     is_splitline_show=False,
    #     legend_text_size=legend_text_size,
    #     legend_text_color=legend_text_color
    # )
    # # bar.render(path='download_interval.png',pixel_ration=1)
    # # bar.render(path='score_interval.png', pixel_ration=1)


def category_rank(df, category):
    # 筛选掉下载量1万以下的
    df = df.query('(download >= 1) & (score >= 4)')

    # 分类排名
    df = df[df.tags.str.contains(category)]
    df['score_total'] = df['score'] * df['download']

    # score_total 标准化为 0-1000 分
    col = df['score_total']
    df['score_total'] = (col - col.min()) / (col.max() - col.min()) * 1000

    # 根据总分筛选出前 20
    df = df.sort_values(by=['score_total'], ascending=False)[:20]

    print(df[['name', 'score_total', 'score', 'download']])
    print(df.info())
    return df


def analysis_top20(df):

    # 下载量top20
    # data = df.sort_values(by='download',ascending=False)[:20]
    # data = data.set_index('name')[::-1]  # 反转顺序，便于条形图大值在上

    # # 下载量last20
    # data = df.sort_values(by='download',ascending=True)[:20]
    # data['download_ori'] = data['download_ori'].astype(int)
    # data = data.set_index('name')

    # 评分top20
    # data = df.sort_values(by=['score','download'],ascending=False)[:20]
    # data = data.set_index('name')[::-1]  # 反转顺序，便于条形图大值在上

    # 分类排名
    data = df.sort_values(by=['score_total'], ascending=False)
    data = data.set_index('name')[::-1]  # 反转顺序，便于条形图大值在上

    fig = plt.figure(figsize=(10, 16))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    y1 = 'score_total'
    y2 = 'score'
    y3 = 'download'

    # # pandas直接绘制
    data.plot(
        ax=ax1,
        y=y1,
        kind='barh',
        color='#C44B37',
        subplots=True,  # 设置子图
        sharey=True,  # 共享y轴
        # xlim = (0,5.5),
    )

    data.plot(
        ax=ax2,
        y=y2,
        kind='barh',
        color='#2EC7C9',
        subplots=True,
        sharey=True,
        xlim=(0, 5.3),
    )

    data.plot(
        ax=ax3,
        y=y3,
        kind='barh',
        color='#2EC7C9',
        subplots=True,
        sharey=True,
    )

    # 添加标签
    # 下载量top 20
    for y, x in enumerate(list(data[y1].values)):
        ax1.text(x + 100, y - 0.08, '%s' %
                 round(x, 0), ha='center', color=colors)
    for y, x in enumerate(list(data[y2].values)):
        ax2.text(x + 0.3, y - 0.08, '%s' %
                 round(x, 1), ha='center', color=colors)
    for y, x in enumerate(list(data[y3].values)):
        ax3.text(x + 50, y - 0.08, '%s' %
                 round(x, 1), ha='center', color=colors)

    plt.tight_layout()  # 自动控制空白边缘
    # 添加竖线
    # plt.vlines(4,0,20,colors=colorline,linestyles='dashed')
    ax1.legend(loc='lower right')  # 更改图例位置
    ax2.legend(loc='lower right')  # 更改图例位置
    ax3.legend(loc='lower right')  # 更改图例位置

    # plt.savefig('酷友作品_rank_top20.png', dpi=200)
    plt.show()


if __name__ == '__main__':
    # data = parse_kuan()
    df = data_processing()
    # 绘制总体下载和评分图
    analysis_general(df)

    # 绘制 top 20图
    # analysis_top20(df)

    # df2 = analysis(df)
    dic = {
        1: '文件|系统|清理|输入法|安全|辅助|桌面|插件|锁屏',
        2: '社交|聊天|微博|论坛',
        3: '阅读|新闻|小说|科普',
        4: '文档|记事本',
        5: '视频|音乐|播放器|直播|电台',
        6: '浏览器|通讯录|流量|通知|邮箱|WiFi',
        7: '拍照|美图|图库',
        8: '导航|地图|旅游|酒店|车|购',
        9: 'Xposed|xposed',
        10: '酷友作品'
    }
    # 1 系统工具
    # 2 社交聊天
    # 3 资讯阅读
    # 4 文档写作
    # 5 影音娱乐
    # 6 通讯网络
    # 7 摄影图片
    # 8 交通购物
    # 9 Xposed 模块
    # 10 实用工具

    # 绘制分类排名图
    # df = category_rank(df, list(dic.values())[9])
    # analysis_top20(df)
