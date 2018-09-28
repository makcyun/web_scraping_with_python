import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ts.set_token('你的token')
pro = ts.pro_api()


# 双折线图
def get_stock2():
    lst = []
    ts_codes = ['000002.SZ', '600048.SH']
    for ts_code in ts_codes:
        data = pro.daily_basic(
            ts_code=ts_code, start_date='20170101', end_date='20180101')
        data['trade_date'] = pd.to_datetime(data['trade_date'])
        # 设置index为日期
        data = data.set_index(data['trade_date']).sort_index(ascending=True)

        # 按月汇总和显示
        data = data.resample('m')
        data = data.to_period()

        # 市值亿元
        market_value = data['total_mv'] / 10000
        lst.append(market_value)

    print(lst)
    return lst


def plot2(lst):
    # 设置绘图风格
    plt.style.use('ggplot')
    fig = plt.figure(figsize=(10, 6))
    ax1 = fig.add_subplot(1, 1, 1)
    colors1 = '#6D6D6D'  # 标题颜色

    data1 = lst[0]
    data2 = lst[1]

    # # # data1万科，data2保利############
    # data1.plot(
    # color = '#C42022', #折线图颜色
    # marker = 'o',markersize = 4, #标记形状、大小设置
    # label = '万科'
    # )

    # data2.plot(
    # color = '#4191C0', #折线图颜色
    # marker = 'o',markersize = 4, #标记形状、大小设置
    # label = '保利'
    # )

    # 2 改善方法####################################

    # 折线图1
    # 创建x,y轴标签
    x = np.arange(0, len(data1), 1)

    ax1.plot(x, data1.values,  # x、y坐标
             color='#C42022',  # 折线图颜色
             marker='o', markersize=4,  # 标记形状、大小设置
             label='万科'
             )
    ax1.set_xticks(x)  # 设置x轴标签
    ax1.set_xticklabels(data1.index)  # 设置x轴标签值
    # plt.xticks(rotation=90)
    for x, y in zip(x, data1.values):
        plt.text(x, y + 10, '%.0f' %
                 y, ha='center', color=colors1, fontsize=10)
        # '%.0f' %y 设置标签格式不带小数

    # 折线图2
    x = np.arange(0, len(data2), 1)
    ax1.plot(x, data2.values,  # x、y坐标
             color='#4191C0',  # 折线图颜色
             marker='o', markersize=4,  # 标记形状、大小设置
             label='保利'
             )
    ax1.set_xticks(x)  # 设置x轴标签
    ax1.set_xticklabels(data2.index)  # 设置x轴标签值
    # plt.xticks(rotation=90)
    for x, y in zip(x, data2.values):
        plt.text(x, y + 10, '%.0f' %
                 y, ha='center', color=colors1, fontsize=10)
        # '%.0f' %y 设置标签格式不带小数

    # 设置标题及横纵坐标轴标题
    plt.title('2017年万科与保利地产市值对比', color=colors1, fontsize=16)
    plt.xlabel('月份')
    plt.ylabel('市值(亿元)')

    plt.savefig('stock1.png', bbox_inches='tight', dpi=300)
    plt.legend()  # 显示图例
    plt.show()


def main():
    # basic_stock()
    # basic_stock_handling()

    # data = basic_stock_handling()
    # 单折线图
    # plot(data)

    # 双折线图
    lst = get_stock2()
    plot2(lst)

if __name__ == '__main__':
    main()
