
import pandas as pd
import csv
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time
import re

start_time = time.time()  #计算程序运行时间
# 获取网页内容
def get_one_page(year):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
            }

            # 英文版
            # url = 'http://www.shanghairanking.com/ARWU%s.html' % (str(year))
            # 中文版
            url = 'http://www.zuihaodaxue.com/ARWU%s.html' % (str(year))
            response = requests.get(url,headers = headers)
            # 2009-2015用'gbk'，2016-2018用'utf-8'
            if response.status_code == 200:
                # return response.text  # text会乱码，content没有问题
                # https://stackoverflow.com/questions/17011357/what-is-the-difference-between-content-and-text
                return response.content
            return None

        except RequestException:
            print('爬取失败')


# 解析表格
def parse_one_page(html,i):
        tb = pd.read_html(html)[0]
        # 重命名表格列，不需要的列用数字表示
        tb.columns = ['world rank','university', 2,3, 'score',5,6,7,8,9,10]
        tb.drop([2,3,5,6,7,8,9,10],axis = 1,inplace = True)
        # 删除后面不需要的评分列

        # rank列100名后是区间，需需唯一化，增加一列index作为排名
        tb['index_rank'] = tb.index
        tb['index_rank'] = tb['index_rank'].astype(int) + 1
        # 增加一列年份列
        tb['year'] = i
        # read_html没有爬取country，需定义函数单独爬取
        tb['country'] = get_country(html)

        # print(tb) # 测试表格ok
        return tb
        # print(tb.info()) # 查看表信息
        # print(tb.columns.values) # 查看列表名称

# 提取国家名称
def get_country(html):
    soup = BeautifulSoup(html,'lxml')
    countries = soup.select('td > a > img')

    lst = []
    for i in countries:
        src = i['src']
        pattern = re.compile('flag.*\/(.*?).png')
        country = re.findall(pattern,src)[0]
        lst.append(country)
    return lst
    # print(lst) # 测试提取国家是否成功ok

# 保存表格为csv
def save_csv(tb):
    tb.to_csv(r'university.csv', mode='a', encoding='utf_8_sig', header=True, index=0)

    endtime = time.time()-start_time
    # print('程序运行了%.2f秒' %endtime)

def analysis():
    df = pd.read_csv('university.csv')
    # 包含港澳台
    # df = df.query("(country == 'China')|(country == 'China-hk')|(country == 'China-tw')|(country == 'China-HongKong')|(country == 'China-Taiwan')|(country == 'Taiwan,China')|(country == 'HongKong,China')")[['university','year','index_rank']]
    # 只包括内地
    # df = df.query("country == 'China'")

    # 美国
    df = df.query("(country == 'UnitedStates')|(country == 'USA')")

    df['index_rank_score'] = df['index_rank']
    # 将index_rank列转为整形
    df['index_rank'] = df['index_rank'].astype(int)
    #求topn名
    def topn(df):
        top = df.sort_values(['year','index_rank'],ascending = True)
        return top[:20].reset_index()
    df = df.groupby(by =['year']).apply(topn)
    # 更改列顺序
    df = df[['university','index_rank_score','index_rank','year']]
    # 重命名列
    df.rename (columns = {'university':'name','index_rank_score':'type','index_rank':'value','year':'date'},inplace = True)

    # 输出结果
    df.to_csv('university_ranking_USA.csv',mode ='w',encoding='utf_8_sig', header=True, index=False)
    # index可以设置


def main(year):
    # generate_mysql()
    for i in range(2009,year):  #抓取10年
        # get_one_page(i)
        html = get_one_page(i)
        # parse_one_page(html,i)  # 测试表格ok
        tb = parse_one_page(html,i)
        save_csv(tb)
        print(i,'年排名提取完成完成')

        # analysis()


# # 单进程
if __name__ == '__main__':
    main(2019)
    # 2016-2018采用gb2312编码，2009-2015采用utf-8编码
