
import pandas as pd
import pymongo
import re
import matplotlib.pyplot as plt
from pyecharts import Bar


def parse_wandoujia():
    client = pymongo.MongoClient(host='localhost',port=27017)
    db = client['wandoujia5']
    collection = db['WandoujiaItem']

    data = pd.DataFrame(list(collection.find()))
    # 删除无用列
    data.drop(['_id','icon_url'],axis=1,inplace=True)

    # 删除重复值
    data = data[~data.duplicated(['app_name','comment'])]
    # dataframe 删除列中部分字符的几种方法
    data['install_count'] = data['install'].map(lambda x:x.rstrip('人安装'))
    # data['install'] = data['install'].map(lambda x:str(x)[:-3])
    # data['install'] = data['install'].str.rstrip('人安装')
    # data['install'].replace(regex=True,inplace=True,to_replace=r'万',value=r'')


    # 统一数值单位万、亿
    con = data['install_count'].str.contains('万$')
    data.loc[con, 'install_count'] = pd.to_numeric(
        data.loc[con, 'install_count'].str.replace('万', '')) * 10000

    con2 = data['install_count'].str.contains('亿$',na=False)
    data.loc[con2, 'install_count'] = pd.to_numeric(
        data.loc[con2, 'install_count'].str.replace('亿', '')) * 100000000

    data['install_count'] = pd.to_numeric(data['install_count'])
    data.sort_values('install_count',ascending=False,inplace=True)


    # 删除comment列空白
    # data['comment'] = data['comment'].apply(clean_space)
    # or
    data['comment'] = data['comment'].apply(lambda x:clean_space(x))
    data = data.reset_index(drop=True)

    # print(data.info())
    # print(data.head(10))

    data.to_csv('wandoujia3.csv',encoding='utf_8_sig')
    return data


def getdata():
    data = pd.read_csv('wandoujia3.csv',encoding='utf_8_sig',usecols=list(range(1,8)))
    return data

def clean_symbol(df, col):

    # 字符万替换为空
    con = df[col].str.contains('万$')
    df.loc[con, col] = pd.to_numeric(
        df.loc[con, col].str.replace('万', '')) * 10000
    return df[col]

def clean_space(col):
    return re.sub('\s+','',col)


# 绘图
# # # # # # # # # # # # # # # # # # # # # # # # # # # #
plt.style.use('ggplot')
colors = '#6D6D6D' #字体颜色
colorline = '#63AB47'  #红色CC2824  #豌豆荚绿
fontsize_title = 20
fontsize_text = 10

# 1下载量最多最少总排名
def analysis_maxmin(data):
    # # 最多
    data_max = (data[:10]).sort_values(by='install_count')
    data_max['install_count'] = (data_max['install_count'] / 100000000).round(1)

    # # 最少
    # data_max = (data[-10:]).sort_values(by='install_count')
    # data_max['install_count'] = (data_max['install_count']).round(1)

    data_max.plot.barh(x='app_name',y='install_count',color=colorline)
    # plt.bar(data_max['app_name'] ,data_max['install_count'])

    for y, x in enumerate(list((data_max['install_count']))):
        plt.text(x + 0.1, y - 0.08, '%s' %
                 round(x, 1), ha='center', color=colors)

    # plt.title('安装量最多的 10 款 App ?',color=colors)
    plt.title('安装量最多的 10 款 App ?',color=colors)
    plt.xlabel('下载量(亿次)')
    plt.ylabel('App')

    plt.tight_layout()
    # plt.savefig('安装量最多的App.png',dpi=200)

    plt.show()


# 2 下载量分布
def analysis_distribution(data):
    data = data.loc[10:,:]
    data['install_count'] = data['install_count'].apply(lambda x:x/10000)

    bins = [0,1,10,100,1000,10000]
    group_names = ['1万以下','1-10万','10-100万','100-1000万','1000万-1亿']

    cats = pd.cut(data['install_count'],bins,labels=group_names)
    cats = pd.value_counts(cats)

    bar = Bar('App 下载数量分布','高达 94% 的 App 下载量低于1万')
    bar.use_theme('macarons')
    bar.add(
        'App 数量',
        list(cats.index),
        list(cats.values),
        is_label_show = True,
        xaxis_interval = 0,
        is_splitline_show = 0,
        )
    bar.render(path='下载数量分布.png',pixel_ration=1)




# 3分类排名最多最少20
def analysis_category(data):
    data = data['cate_name'].value_counts(ascending=True)
    data.plot.barh(color=colorline)

    for y,x in enumerate(data.values):
        plt.text(x+250,y-0.15,'%s'%(round(x,1)),ha='center',color=colors)
    # plt.show()

    plt.xlabel('APP 数量(款)',color=colors)
    plt.ylabel('App 类别',color=colors)
    plt.title('App 数量最多的是「生活休闲」类',color=colors)

    plt.tight_layout()
    plt.savefig('各分类下的 App 数量.png',dpi=200)


# 小分类排名 最多最少 20
def analysis_subcategory(data):
    data1 = data['child_cate_name'].value_counts(ascending=True)[-10:]
    data2 = data['child_cate_name'].value_counts(ascending=True)[:10]

    fig = plt.figure(figsize=(10,12))
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2)

    data1.plot.barh(
        ax =ax1,
        y = data1.values,
        xlim = (0,1600),
        color = colorline)

    data2.plot.barh(
            ax =ax2,
            y = data2.values,
            xlim = (0,350),
            color = colorline)

    for y, x in enumerate(data1.values):
        ax1.text(x+80, y-0.05, '%s' %
                 round(x, 0), ha='center', color=colors)

    for y, x in enumerate(data2.values):
            ax2.text(x+20, y-0.05, '%s' %
                     round(x, 0), ha='center', color=colors)

    # 添加标签

    ax1.set_xlabel('App 数量')
    ax1.set_ylabel('App 子类别')
    ax2.set_xlabel('App 数量')

    ax1.set_title(' App 数量最多的是「收音机」',color=colors)
    ax2.set_title(' App 数量最少的是「壁纸」',color=colors)

    plt.tight_layout()
    plt.savefig('App子类别数量排名.png',dpi=200)

    # plt.show()
    # print(data)

def analysis_cate_distributionn(data):
    data = data[1000:-1000]
    data.boxplot(column='install_count',by='cate_name')
    plt.show()



# 查找重名的 Appp
def find_duplcateapp(data):
    # # 查找总重复数
    # data = data[data.duplicated(['app_name'])].reset_index(drop=True)

    # data.to_csv('duplicated_app.csv',encoding='utf_8_sig')

    # # app具体重复数量分布
    data = data['app_name'].value_counts()[:10].sort_values(ascending=True)


    data.plot.barh(color=colorline)

    for y,x in enumerate(data.values):
        plt.text(x+1,y-0.15,'%s'%(round(x,1)),ha='center',color=colors)


    plt.xlabel('APP 数量(款)',color=colors)
    plt.ylabel('App 名称',color=colors)
    plt.title('重名最多的 App',color=colors)

    plt.tight_layout()
    plt.savefig('重名最严重的的App TOP10.png',dpi=200)
    plt.show()


    # bar = Bar('重名最严重的的App TOP10','叫「一键锁屏」的 App 居然多达 40 款')
    # bar.use_theme('macarons')
    # bar.add(
    #     '名称重复的 App',
    #     list(data.index),
    #     list(data.values),
    #     is_label_show=True,
    #     xaxis_interval=0,
    #     # xaxis_rotate=30,
    #     is_splitline_show=False,
    #     legend_text_size=legend_text_size,
    #     legend_text_color=legend_text_color,
    #     # label_formatter = '{c}', #a,b,c,d,e分别表示系列名，数据名，数据值
    #     # https://pyecharts.readthedocs.io/en/latest/zh-cn/%E5%9B%BE%E5%BD%A2%E7%AF%87/
    #     # is_convert=True #不要颠倒xy轴有bug
    #     )
    # bar.render('duplicated_app.png',pixel_ration=1)

    # data.plot.bar(color=colorline)

    # plt.show()


def find_app(data):

    # data = data.quantile([0.01,0.5,0.99])
    # data = data.describe([0.01,0.5,0.99])

    data['install_count'] = data['install_count'].apply(lambda x:x/10000).round()
    data['rank'] = data.index + 1

    data2 = pd.read_csv('kuan.csv',encoding='utf8',usecols=['name','download','score']).sort_values(by='download',ascending=False).reset_index()
    data2['kuan_rank'] = data2.index + 1
    data3 = data2.merge(data,left_on='name',right_on='app_name',how='inner')[['name','download','install_count','kuan_rank','rank','score']]

    data3.sort_values(by='download',ascending=False,inplace=True)
    # data2 = data2.reset_index(drop=True) #重置索引
    print(data3['download'].corr(data3['install_count']))

    # data3 = data3.set_index('name')
    # data3 = data3[['install_count','download']][:10].sort_values(by='download',ascending=True)

    # data3.plot.barh(
    #     color = (colorline,'#7FC161')
    #     )

    # plt.xlabel('APP 下载量(万次)',color=colors)
    # plt.ylabel('App 名称',color=colors)
    # plt.title('两个平台的下载量差别很大',color=colors)

    # plt.tight_layout()
    # plt.savefig('平台对比.png',dpi=200)
    # plt.show()


    # 包含与不包含app数量分布
    # data4 = pd.DataFrame({'App':['包含 App','未包含 App'],'数量':[data3.shape[0],data2.shape[0] - data3.shape[0]]},index=['包含','未包含'])

    include = data3.shape[0]
    notinclude = data2.shape[0] - data3.shape[0]
    sizes= [include,notinclude]
    labels = [u'包含',u'不包含']
    explode = [0,0.05]
    plt.pie(
        sizes,
        autopct = '%.1f%%',
        labels = labels,
        colors = [colorline,'#7FC161'], # 豌豆荚绿
        shadow = False,
        startangle = 90,
        explode = explode,
        textprops = {'fontsize':14,'color':colors}
        )
    plt.title('豌豆荚仅包括酷安上一半的 App 数量',color=colorline,fontsize=16)
    plt.axis('equal')
    plt.axis('off')



    # # 3不在名单内的app分布
    # data4 = pd.concat([data2,data3],sort=False)
    # data4 = data4.drop_duplicates(subset='name',keep=False)
    # data4 = data4[data4.score > 4][:20].sort_values(by='download',ascending=True)

    # fig = plt.figure(figsize=(10,12))
    # ax1 = fig.add_subplot(1,2,1)
    # ax2 = fig.add_subplot(1,2,2)

    # data4.plot.barh(
    #     ax = ax1,
    #     x = 'name',
    #     y = 'download',
    #     xlim = (0,6000),
    #     sharey = True,
    #     color = colorline)

    # data4.plot.barh(
    #     ax = ax2,
    #     x = 'name',
    #     y = 'score',
    #     xlim = (0,5.5),
    #     sharey = True,
    #     color = colorline)

    # for y,x in enumerate(data4['download'].values):
    #     ax1.text(x+400,y-0.1,'%s'%(round(x,0)),ha='center',color=colors)

    # for y,x in enumerate(data4['score'].values):
    #     ax2.text(x+0.2,y-0.1,'%s'%(round(x,1)),ha='center',color=colors)

    # ax1.set_xlabel('APP 下载量(万次)')
    # ax1.set_ylabel('App 名称')
    # ax2.set_xlabel('App 评分')
    # ax1.set_title('下载量最多的佳软 App',color=colors)
    # ax2.set_title('App 得分都很高',color=colors)

    # ax1.legend(loc=4)
    # ax2.legend(loc=4)

    plt.tight_layout()
    plt.savefig('包含不保包含.png',dpi=200)

    plt.show()




if __name__ == '__main__':

    # data = parse_wandoujia()
    data = getdata()

    # 1安装量最多最少图
    # analysis_maxmin(data)

    # 2安装量分布图
    analysis_distribution(data)

    # 3 分类数量分布
    # analysis_category(data)

    # 4 子分类数量分布
    # analysis_subcategory(data)

    # 5 重名app
    # find_duplcateapp(data)


    # find_app(data)

    # analysis_cate_distributionn(data)
    # find_duplcateapp(data)
    #
