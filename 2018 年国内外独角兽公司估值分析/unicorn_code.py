#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-2-17 09:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @Link    : http://www.makcyun.top




"""
pyecharts 地图
地图安装包
https://github.com/pyecharts/pyecharts

# 主题设置方法
https://github.com/pyecharts/pyecharts/blob/master/docs/zh-cn/themes.md#essos

"""

from pyecharts import Map, Page, Style, Geo # 地图
from pyecharts import Bar, Pie, Boxplot
import pandas as pd
from pyecharts import Grid # 控制图表布局

# 更改默认主题
from pyecharts import configure
# 代码置于首部
configure(global_theme='dark')

# 获取数据
def get_data():
    data = pd.read_csv('./unicorn_worldwide.csv')  # 全球
    data2 = pd.read_csv('./unicorn_china.csv')
    return data, data2


# 1 全球独角兽公司分布
def unicorn_world(data):
    data = data.groupby(by='Country').count()
    data.sort_values(by='Company', ascending=False, inplace=True)
    attr = list(data.index)
    value = list(data['Company'].values)

    # 1 绘制地图
    map = Map(
        "全球独角兽公司分布",
        '326 家公司分布在 26 个国家',
        title_color="#fff", title_pos="left",  # 标题颜色位置
        # background_color='#404a59' #背景色
    )

    map.add("", attr, value,
            maptype="world",  # 世界地图
            visual_range=[0, 160],  # 值范围
            visual_text_color="#fff",
            is_visualmap=True, is_label_show=False,
            label_formatter='{b}'  # {a}{b}{c}显示不同标签、值格式
            )

    map.render(path='全球独角兽公司分布.png', pixel_ration=1)

    # 2 绘制柱状图
    bar = Bar("各国独角兽公司数量对比", '美中制霸', title_pos="center")
    bar.add("", attr, value,
            is_label_show=True,
            xaxis_interval=0,
            xaxis_rotate=45,
            )

    # Grid 控制图表布局范围，避免坐标标签折断
    grid = Grid()
    grid.add(bar, grid_bottom='25%')  # 图表距离底边25%，x 轴标签能够充分显示
    grid.render(path='各国独角兽公司数量.png', dpi=200)


# 2 各国独角兽公司估值对比饼图
def unicorn_world2(data):
    data = data.groupby(by='Country').sum()
    data = data.sort_values(by='Valuation', ascending=False)

    data2 = data[:5]['Valuation']  # 前5国家
    data3 = data[5:]['Valuation'].sum()  # 后5国家全部划分为其他
    data2.loc['Else'] = data3

    attr = list(data2.index)
    value = list(data2.values)

    chart = Pie(
        '各国独角兽公司估值对比',
        '中美占据 80%',
        title_pos='center',
    )

    chart.add('', attr, value,
              is_label_show=True,
              is_legend_show=False,
              )

    chart.render(path='各国独角兽公司市值对比.png')


# 3 中美top10独角兽企业
def unicorn_world3(data):
    data1 = data.query("Country == 'China'")
    # data1 = data.query("Country == 'United States'")
    data1 = data1.sort_values(by='Valuation', ascending=False)[:10]

    attr = list(data1['Company'])
    value = list(data1['Valuation'])

    bar = Bar("中国独角兽公司估值前十名", '差距比较大', title_pos="center")
    # bar = Bar("美国独角兽公司估值前十名",'差距不大,都在 100 亿美金以上',title_pos="center")
    bar.add("",
            attr,
            value,
            is_label_show=True,
            xaxis_interval=0,  # 强制x轴显示全部标签
            xaxis_rotate=45,  # 45度倾斜
            )

    # Grid 控制图表布局，避免坐标标签折断
    grid = Grid()
    grid.add(bar, grid_bottom='25%')

    grid.render(path='中国独角兽企业市值前十名.png', dpi=200)


# 全国独角兽公司分布
def unicorn_china(data):
    data = data.groupby(by='Headquarter').count()
    data.sort_values(by='Company', ascending=False, inplace=True)

    value = list(data['Company'].values)
    attr = list(data.index)
    # print(value,attr)

    map = Geo("大中华区独角兽公司分布", '北京突出', title_color="#fff",
              title_pos="center", background_color='#404a59')
    # type="effectScatter", is_random=True, effect_scale=5  使点具有发散性

    # 发散圆点图
    map.add("", attr, value, type="effectScatter",
            is_random=True, effect_scale=5,
            visual_range=[0, 80],
            visual_text_color="#fff",
            symbol_size=5,
            is_visualmap=True,
            )

    map.render(path='./国内独角兽公司城市分布.png', pixel_ration=1)

# 大中华区独角兽公司估值前二十名
def unicorn_china2(data):
    data.sort_values(by='Valuation', ascending=False, inplace=True)
    data = data[:20][::-1]

    attr = list(data['Company'].values)
    value = list(data['Valuation'].values)
    # print(value,attr)

    bar = Bar("大中华区独角兽公司估值前二十名", '巨无霸蚂蚁金服', title_pos="center")

    bar.add("单位(亿人民币)",
            attr,
            value,
            is_label_show=True,
            label_pos='right',
            xaxis_interval=0,
            yaxis_roate=45,
            is_convert=True,
            legend_pos='right'
            )

    # Grid 控制图表布局，避免坐标标签折断
    grid = Grid(width=600, height=1000)  # 修改图形尺寸
    grid.add(bar, grid_left='15%')

    grid.render(path='大中华区独角兽企业估值前二十.png', dpi=200)


# 五大城市独角兽公司估值范围对比
def unicorn_china3(data):
    data1 = list(data.query("Headquarter == '北京'")['Valuation'].values)
    data2 = list(data.query("Headquarter == '上海'")['Valuation'].values)
    data3 = list(data.query("Headquarter == '广州'")['Valuation'].values)
    data4 = list(data.query("Headquarter == '深圳'")['Valuation'].values)
    data5 = list(data.query("Headquarter == '杭州'")['Valuation'].values)

    x_axis = ['北京', '上海', '广州', '深圳', '杭州']
    y_axis = [data1, data2, data3, data4, data5]

    chart = Boxplot('五大城市独角兽公司估值范围对比', title_pos='center')
    chart.add('单位(亿人民币)',
              x_axis, y_axis,
              legend_pos='right'
              )

    chart.render('五大城市独角企业市值值对比.png')


# 各城市top3
def unicorn_china4(data):
    def top(data):
        top = data.sort_values(by=['Valuation'], ascending=False)
        return top[:3]

    data = data.groupby(by=['Headquarter']).apply(top)

    data['add'] = 1  # 辅助
    data['top'] = data.groupby(by='Headquarter')['add'].cumsum()
    data = data[['Company', 'Valuation', 'Industry', 'top']]

    print(data)


# 按行业估值
def unicorn_china5(data):
    data = data.groupby(by='Industry').sum()
    data = data.sort_values(by='Valuation', ascending=False)

    data2 = data[:10]['Valuation']
    data3 = data[10:]['Valuation'].sum()

    data2.loc['其他行业'] = data3
    data2 = data2[::-1]

    attr = list(data2.index)
    value = list(data2.values)

    bar = Bar("独角兽公司所在行业估值对比", '互联网金融行业成香饽饽', title_pos="center")

    bar.add('单位(亿人民币)',
            attr,
            value,
            is_label_show=True,
            label_pos='right',
            xaxis_interval=0,
            # yaxis_roate=45,
            is_convert=True,
            legend_pos='right'
            )

    # Grid 控制图表布局，避免坐标标签折断
    grid = Grid(width=600, height=1000)  # 修改图形尺寸
    grid.add(bar, grid_left='15%')
    grid.render(path='独角兽公司所在行业估值对比.png', dpi=200)


# 各行业估值top3公司
def unicorn_china6(data):
    def top(data):
        top = data.sort_values(by=['Valuation'], ascending=False)
        return top[:3]

    data = data.groupby(by=['Industry']).apply(top)

    data['add'] = 1  # 辅助
    data['top'] = data.groupby(by='Industry')['add'].cumsum()
    data = data[['Company', 'top', 'Valuation']]

    print(data)


if __name__ == '__main__':
    data, data2 = get_data()

    # 全球独角兽公司分布
    unicorn_world(data)

    # 各国独角兽公司估值对比饼图
    unicorn_world2(data)

    # 中美top10独角兽企业对比
    unicorn_world3(data)

    # 大中华区独角兽公司分布
    unicorn_china(data2)

    # 大中华区独角兽公司估值前二十名
    unicorn_china2(data2)

    # 五大城市独角兽公司估值对比
    unicorn_china3(data2)

    # 各城市top3
    unicorn_china4(data2)

    # 按行业估值
    unicorn_china5(data2)

    # 各行业估值top3公司
    unicorn_china6(data2)
