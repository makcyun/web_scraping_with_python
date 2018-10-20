import tushare as ts
ts.set_token('你的token')
pro = ts.pro_api()

import pandas as pd
import numpy as np
# from datetime import datetime
import matplotlib.pyplot as plt

# 1获取个股历史交易数据（包括均线数据）
# data = ts.get_hist_data('002717')


# 行业分类
# data = ts.get_industry_classified()
# data.to_csv('classified.csv',mode='a',encoding = 'utf_8_sig',index = True)
# data = data.query("c_name == '环境保护'")
# print(data)

# 中小板分类
# data = ts.get_sme_classified()
#


# 每日指标
# 获取全部股票每日重要的基本面指标，可用于选股分析、报表展示等
# start = datetime(2015,1,1)

def basic_stock():
    # 1全部股票列表基础信息
    data = ts.get_stock_basics()
    data = pro.stock_basic(exchange_id='', is_hs='',
                           fields='ts_code,symbol,name,is_hs,list_date,list_status')
    data.to_csv('get_stock_basics.csv', mode='w',
                encoding='utf_8_sig', index=False)
    # 注意要写mode='w'，而不是缩写为'w'
    # print('股市基本数据提取完毕')

    data['list_date'] = pd.to_datetime(data['list_date'])
    # print(data) #测试数据ok
    print(data.info())


def basic_stock_handling():
    data = pd.read_csv('get_stock_basics.csv',
                       encoding='utf-8', converters={'symbol': str})
    # converters = {'code':str} 将数字前面不显示的0转为str显示

    # 日期格式由数值型改为日期型
    data['list_date'] = data['list_date'].apply(str)
    data['list_date'] = pd.to_datetime(data['list_date'])
    data = data.set_index(data['list_date'])

    # # 1按日期筛选数据
    # # 按年度
    # # 单一年度
    # data = data['2017']
    # # 按多个年度
    # data = data['2015':'2017']

    # # 按月度
    # data = data['2017-1']

    # # 按具体天
    # data = data['2017-1-12']

    # # 2按日期显示数据
    # # 按年
    # data = data.to_period('A')

    # # 按季度
    # data = data.to_period('Q')

    # # 按月度
    # data = data.to_period('M')

    # 3 按日期统计数据
    # # 按年度
    # data = data.resample('AS').count()['name']

    # # 按季度
    # data = data.resample('Q').count()['name']

    # 按季度
    # data = data.resample('M').count()['name']

    # 4 统计和显示结合
    data = data.resample('AS').count()['name']
    data = data.to_period('A')

    # 汇总各年上市公司数量
    # data = data.set_index(['list_date'])
    # data = data.resample('AS').count()['name']
    # data = data.to_period('A')

    # print(data.head())
    # print(data.tail())
    print(type(data))

    return data


def main():
    # basic_stock()
    # basic_stock_handling()


if __name__ == '__main__':
    main()
