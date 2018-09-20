
import pandas as pd
import tushare as ts
from datetime import datetime

import matplotlib.pyplot as plt
plt.style.use('ggplot')

ts.set_token('404ba015bd44c01cf09c8183dcd89bb9b25749057ff72b5f8671b9e6')
pro = ts.pro_api()


def get_code():
    # 所有股票列表
    data = ts.get_stock_basics()
    # data = data.query('industry == "环境保护"')
    # 或者
    data = data[data.industry =='环境保护']
    # 提取股票代码code并转化为list
    data['code2'] = data.index
    # apply方法添加.SZ后缀
    data['code2'] = data['code2'].apply(lambda i:i+'.SZ')
    data = data.set_index(['code2'])
    # 将code和name转为dict
    data = data['name']
    data = data.to_dict()
    # 增加东方园林
    data['002310.SZ'] = '东方园林'
    # print(data) #测试返回的环保股dict ok
    return data

def stock(key,start,end,value):
    data = pro.daily_basic(ts_code=key, start_date=start, end_date=end) # 获取每只股票时间段数据

    # 替换掉末尾的.SZ,regex设置为true才行
    data['code'] = data['ts_code'].replace('.SZ','',regex = True)
    data['name'] = value
    # print(data)
    data.to_csv('environment.csv',mode='a',encoding = 'utf_8_sig',index = False,header = 0)

def parse_code():
    df = pd.read_csv('environment1.csv',encoding = 'utf-8')
    df.columns = ['ts_code','trade_date','close','turnover_rate','volume_ratio','pe','e_ttm','pb','ps','ps_ttm','total_share','float_share','free_share','total_mv','circ_mv', 'code','name']
    df['trade_date'] = pd.to_datetime(df['trade_date'])

    ## 设置总市值数字格式由万元变为亿元
    df['total_mv'] = pd.to_numeric(df['total_mv'],errors = 'ignore')
    df['total_mv'] = (df['total_mv']/10000)

    # 保留四列,并将交易日期设为index
    df = df[['ts_code','trade_date','total_mv','name']]
    df = df.set_index('trade_date')

    df = df[df.name == value]
    # # 不能用query方法
    # # df = df.query('name == ')

    df = df.resample('AS').mean()/10000  #年平均市值
    df = df.to_period('A')
    # # 增加code列
    df['code'] = value
    # # 重置index
    df = df.reset_index()

    # 重命名为d3.js格式
    # 增加一列空type
    df['type'] = ''
    df = df[['code','type','total_mv','trade_date']]
    df.rename(columns = {'code':'name','total_mv':'value','type':'type','trade_date':'date'})
    df.to_csv('parse_environment.csv',mode='a',encoding = 'utf_8_sig',index = False,float_format = '%.1f',header = 0)
    float_format = '%.1f' #设置输出浮点数格式

    # print(df)
    # print(df.info())


def main():
    # get_code()  #提取环保股dict
    start = '20090101'
    end = '201809010'
    ts_codes = get_code()
    # dict_values转list
    keys = list(ts_codes.keys())
    values = list(ts_codes.values())

    for key,value in ts_codes.items():
        stock(key,start,end,value)

    for value in values:
        parse_code(value)

if __name__ == '__main__':
    main()