#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-1-29 17:11:00
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top
# @Version : $Id$

"""
爬取 1983 至 2018 年 共 36 年春晚的节目趣事，包括这些内容：

谁导演春晚次数最多？

谁主持春晚次数最多？

哪两年的除夕刚好是同一天？

谁上春晚次数最多，堪称「钉子户」？

港台明星上春晚次数对比

歌曲、小品、相声类节目数量对比

"""



# import pandas as pd

# def get_data():
#     data = pd.read_csv('chinese_newyear2.csv',encoding='utf_8_sig')
#     data = data['category\tname\tactor\tyear'].str.split('\t',expand=True)
#     data.columns = ['category','name','actor','year']
#     # # data['actor'].str.split('、',expand=True)
#     # data2 = data['actor'].str.split('、',expand=True)
#     # # print(type(data2))
#     # data = pd.merge(data,pd.DataFrame(data2),how='left',left_index=True, right_index=True)
#     # # print(data.columns)
#     data.to_csv('chinese_newyear4.csv',encoding='utf_8_sig',index=0)

#     print(data)
#     # print(data.describe())
#     # return data

# get_data()


"""
列拆分合并
https://zhuanlan.zhihu.com/p/30529129

"""

import pandas as pd
import matplotlib.pyplot as plt
import pylab
import numpy as np
import matplotlib.dates as mdates
import matplotlib as mpl


plt.style.use('ggplot')
fig = plt.figure(figsize=(5,8))
colors = '#6D6D6D' #黑色
colorstitle = '#EE9922'


# 春晚官网提取五种颜色，
color1 = '#D50700'
color2 = '#DB2B08'
color3 = '#E14F10'
color4 = '#E77318'
color5 = '#EE9922'

fontsize_title = 15
fontsize_text = 10



# 分析导演、主持人 # # # # # # # # # # # # # # # # # #
def get_infodata():
    data = pd.read_csv('chinese_newyear3.csv',encoding='utf_8_sig')

    # 筛选导演主持人
    data = data[data['category'] == '导演']
    # data = data[data['category'] == '主持']
    data2 = data['content'].str.split('、',expand=True)

    # 统计出现次数
    data2 = data2.apply(pd.value_counts)
    data2['col_num'] = data2.sum(axis=1)
    data2.sort_values(by='col_num',ascending=False,inplace=True)
    data2 = data2['col_num'][:10][::-1]
    return data,data2


def analysis1(data,data2):
    data = data.set_index('year')
    data2.sort_values(ascending=False,inplace=True)
    lst = list(data2.index)[:10]
    lst_num = list(data2)[:10]

    colorsall = [color1,color2,color3,color4,color5,color1,color2,color3,color4,color5]
    for i,name in enumerate(lst):
        data3 = data['content'].str.contains(name,na=False).astype('int')
        data3 = pd.DataFrame(data3[data3.values == 1])
        data3['year'] = data3.index

        axs = fig.add_subplot(1, 10, 1+i)
        data3.plot(
            ax=axs,
            x='content',
            y = 'year',
            kind = 'scatter',
            subplots=True,
            sharey=True,
            color=colorsall[i],
            )
        new_ticks = np.linspace(1980,2020,41)

        plt.yticks(new_ticks)
        plt.tick_params(direction='in')  #标签朝里
        plt.tick_params(which='major',length=0)  # 不显示刻度标签长度
        plt.xticks([]) #去掉坐标标签
        plt.xlabel('%i次' %(lst_num[i]),fontsize=10)
        plt.xlim(0,2)

        plt.title(name,color=color5,fontsize=10)
        # plt.tight_layout(pad=3.4, w_pad=0.5, h_pad=1.0)
        fig.subplots_adjust(hspace=0,wspace=0) # 调整子图间距为0

    plt.suptitle('导演次数最多的导演 TOP 10',color=color1,fontsize=18)
    # 添加总标题
    # plt.tight_layout()
    plt.savefig('导演次数最多的导演 TOP 10.png',dpi=200)
    plt.show()




# 分析除夕日期
def get_date():
    fig = plt.figure(figsize=(5,8))
    ax = fig.add_subplot(111)
    data = pd.read_csv('chinese_newyear3.csv',encoding='utf_8_sig')
    data = data[data['category'] == '播出日期']

    data = data['content'].str.extract(r'.*?年(.*?)月(.*?)日.*?')
    data = data.reset_index(drop=True)
    data.columns = ['month','day']
    data['year'] = np.arange(1983,2019)

    # int 转 string
    data = data.applymap(str)
    data['year2'] = '1900'
    data['date'] = data['year2'].str.cat([data['month'],data['day']],sep='/')
    data = data.apply(pd.to_numeric,errors='ignore')
    data['date'] = pd.to_datetime(data['date'])

    ax.plot(
        data['date'],
        data['year'],
        )

    new_yticks = np.linspace(1980,2020,41)
    date_format = mpl.dates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(date_format)

    plt.yticks(new_yticks)
    plt.tick_params(direction='in')  #标签朝里

    content = list(zip(data['date'],data['year']))
    # print(content)

    # for x, y in content:
    #     x2 = '%s' %x.strftime('%m/%d') # 只显示月日格式
    #     # print(x,'\n',y)
    #     plt.text(x, y+0.2,x2, ha='center', color=color4)

    # plt.title('历年农历除夕日期变化',color=color4,fontsize=14)
    # plt.tight_layout()
    # plt.savefig('除夕日期变化.png',dpi=200,)
    # plt.show()



# 处理节目数据
def get_data():
    data = pd.read_csv('chinese_newyear.csv',encoding='utf_8_sig')
    data2 = data['actor'].str.split('、',expand=True) # 拆分人员名单
    data = pd.merge(data,pd.DataFrame(data2),how='left',left_index=True, right_index=True)
    return data


# 表演次数最多的演员TOP 20
def analysis2(data):
    cols = data.columns.size - 6

    cols = list(range(47))
    data = data[cols]

    # 统计演员出现次数
    data = data.apply(pd.value_counts)
    # 列求和计算出现总次数
    data['col_sum'] = data.sum(axis=1)

    data.sort_values(by='col_sum',ascending=False,inplace=True)
    # 取TOP20 [::-1]，反转顺序便于条形图大值在上
    data = data['col_sum'][:20][::-1]

    # data.plot(
    #     kind = 'barh',
    #     color = color1
    #     )
    # for y,x in enumerate(list(data.values)):
    #     plt.text(x+1,y-0.15,'%i'%x,ha='center',color=color4)

    # plt.title('表演次数最多的演员 TOP 20',color=colorstitle,fontweight='bold',fontsize=fontsize_title)

    # plt.tight_layout()
    # plt.xticks([])
    # plt.savefig('表演次数最多的演员TOP20.png',dpi=200)
    # plt.show()

    return data


# 各类节目数量对比
def analysis3(data):
    fig = plt.figure(figsize=(8,5))
    num_all = data.shape[0]
    # 歌曲节目数量
    num_song = data[data['category'].str.contains('歌|尾|开场')].shape[0]
    # 小品数量
    num_sketch = data[data['category'].str.contains('小品')].shape[0]
    # 相声数量
    num_crosstalk = data[data['category'].str.contains('相声')].shape[0]

    # 其他节目数量
    other = num_all - sum([num_song,num_sketch,num_crosstalk])
    lst = [num_song,num_sketch,num_crosstalk,other]

    sizes = [num_song,other,num_crosstalk,num_sketch]
    labels = ['歌曲','其他','相声','小品']
    colors_pie = [color1,color4,color3,color2]
    explode = [0.05,0,0,0]
    plt.pie(
        sizes,
        autopct='%.1f%%',
        labels=labels,
        colors=colors_pie,
        shadow=False,
        startangle=270,
        explode=explode,
        textprops={'fontsize':14,'color':colors}
        )
    plt.title('1983-2018 共 36 年春晚节目类型数量比较',color=colorstitle,fontsize=fontsize_title)


    plt.tight_layout()
    plt.axis('equal')
    plt.axis('off')
    plt.legend(loc='upper right')
    plt.savefig('1983-2018 共 36 年间各类节目类型数量比较.png',dpi=200)

    plt.show()


# 演员 TOP10 出演年数分布
def analysis4(data,data1):
    data = data.set_index('year')
    data1.sort_values(ascending=False,inplace=True)
    lst = list(data1.index)[:10]
    lst_num = list(data1)[:10]

    colorsall = [color1,color2,color3,color4,color5,color1,color2,color3,color4,color5]

    # for 循环绘制子图
    for i,name in enumerate(lst):
        data2 = data['actor'].str.contains(name,na=False).astype('int')

        data2 = pd.DataFrame(data2[data2.values == 1])
        data2['year'] = data2.index
        data2 = data2.drop_duplicates(subset=['year'],keep='last')

        axs = fig.add_subplot(1, 10, 1+i)
        data2.plot(
            ax=axs,
            x='actor',
            y = 'year',
            kind = 'scatter',
            subplots=True,
            sharey=True,
            color=colorsall[i],
            )

        new_ticks = np.linspace(1980,2020,41)
        plt.yticks(new_ticks) # 完整显示所有年份
        plt.tick_params(direction='in')  #标签朝里
        plt.tick_params(which='major',length=0) # 标签长度为0
        plt.xticks([]) #去掉坐标标签
        plt.xlabel('%i次' %(lst_num[i]),fontsize=10)
        plt.xlim(0,2)
        plt.title(name,color=color5,fontsize=10)



        # plt.tight_layout()
        fig.subplots_adjust(hspace=0,wspace=0) # 调整子图间距为0

    plt.suptitle('表演次数最多的演员 TOP 10',color=color1,fontsize=18)
    plt.savefig('演员表演年份.png',dpi=200)

    plt.show()



# 港台演员出演年数分布
def analysis5(data):
    data = data.set_index('year')
    lst = ['周杰伦','成龙','刘德华','王力宏','王菲','郭富城','陈奕迅','林俊杰','林志玲','黎明',]
    lst_num = []
    for i in lst:
        data2 = data[data['actor'].str.contains(i,na=False)].shape[0]
        lst_num.append(data2)

    colorsall = [color1,color2,color3,color4,color5,color1,color2,color3,color4,color5]

    for i,name in enumerate(lst):
        data2 = data['actor'].str.contains(name,na=False).astype('int')

        data2 = pd.DataFrame(data2[data2.values == 1])
        data2['year'] = data2.index
        data2 = data2.drop_duplicates(subset=['year'],keep='last')

        axs = fig.add_subplot(1, 10, 1+i)
        data2.plot(
            ax=axs,
            x='actor',
            y = 'year',
            kind = 'scatter',
            subplots=True,
            sharey=True,
            color=colorsall[i],
            )
        new_ticks = np.linspace(1980,2020,41)
        plt.yticks(new_ticks)
        plt.tick_params(direction='in')  #标签朝里
        plt.tick_params(which='major',length=0) # 标签长度为0
        plt.xticks([]) #去掉坐标标签
        plt.xlabel('%i次' %(lst_num[i]),fontsize=10)
        plt.xlim(0,2)

        plt.title(name,color=color5,fontsize=10)
        # plt.tight_layout()
        fig.subplots_adjust(hspace=0,wspace=0) # 调整子图间距为0

    plt.suptitle('十大港台演员出演次数',color=color1,fontsize=18)
    plt.savefig('港台演员表演次数对比.png',dpi=200)
    plt.show()




if __name__ == '__main__':
    # # # 导演主持除夕时间
    # data,data2 = get_infodata()
    # analysis1(data,data2)

    # # 除夕日期
    # get_date()

    # # 节目表处理
    data = get_data()

    # 表演次数最多的演员TOP 20
    # analysis2(data)

    # 各类节目数量对比
    # analysis3(data)

    # # TOP 10 演员表演年份
    # data1 = analysis2(data)
    # analysis4(data,data1)

    # # 港台演员出演年数分布
    analysis5(data)

