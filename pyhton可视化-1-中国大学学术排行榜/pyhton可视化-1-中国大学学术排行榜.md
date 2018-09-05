---
title: 'Pyhton可视化(1): 中国大学学术排行榜'
date: 2018-09-05 13:27:22
id: Python_analysis1
categories: Python
tags:Python可视化
images:
keywords: [Python可视化,Python爬虫]
---

Python爬虫中国大学学术排名并结合D3.js做动态数据可视化表。

<!-- more -->  

**摘要：**：最近在朋友圈看到一个很酷炫的动态数据可视化表，介绍了新中国成立后各省GDP的发展历程，非常惊叹竟然还有这种操作，也想试试。于是，照葫芦画瓢虎，在网上爬取了历年中国大学学术排行榜，制作了一个中国大学排名Top20强动态表。

## 作品介绍 ##

这里先放一下这个动态表是什么样的：
[https://www.bilibili.com/video/av24503002](https://www.bilibili.com/video/av24503002)

不知道你看完是什么感觉，至少我是挺震惊的，想看看作者是怎么做出来的，于是追到了作者的B站主页，发现了更多这样有意思的动态视频：
放图  
这些作品的作者是：@Jannchie见齐，他的主页：
[https://space.bilibili.com/1850091/#/video](https://space.bilibili.com/1850091/#/video)

这些会动的图表是如何做出来的呢？  
他用到的是一个动态图形显示数据的JavaScript库：D3.js，是一种前端技术，难怪不是一般地酷炫。
那么，如果不会D3.js是不是就做不出来了呢？    
当然不是，Jannchie见齐非常好心地给出了一个傻瓜式地教程：  
[https://www.bilibili.com/video/av28087807](https://www.bilibili.com/video/av28087807) 

他同时还开放了程序源码，你只需要做2步就能够实现：  
- 1 到他的Github主页下载源码到本地电脑：
  [https://github.com/Jannchie/Historical-ranking-data-visualization-based-on-d3.js](https://github.com/Jannchie/Historical-ranking-data-visualization-based-on-d3.js)  
放图

- 2 打开`dist`文件夹里面的`exampe.csv`文件，放进你想要展示的数据，再用浏览器打开`bargraph.html`网页，就可以实现动态效果了。

下面，我们稍微再说详细一点，实现这种效果的关键点。  
首先，要有数据。观察一下上面的作品可以看到，横向柱状图中的数据要满足两个条件：一是要有多个对比的对象，二是要在时间上连续。这样才可以做出动态效果来。这样的数据其实有很多。

好，看完后我立马就有了一个想法：**看看近十年中国的各个大学的排名是如何变化的**。下面我们就实际来操作一下。

## 案例操作：中国大学Top20强 ##

### 数据来源 ###
世界上最权威的大学排名有4类，分别是：
- 原上海交通大学的ARWU
   [http://www.shanghairanking.com/ARWU2018.html](http://www.shanghairanking.com/ARWU2018.html)
- 英国教育组织的QS   
  [https://www.topuniversities.com/university-rankings/world-university-rankings/2018](https://www.topuniversities.com/university-rankings/world-university-rankings/2018)
- 泰晤士的THE  
[https://www.timeshighereducation.com/world-university-rankings](https://www.timeshighereducation.com/world-university-rankings)  
- 美国的usnews   
[https://www.usnews.com/best-colleges/rankings](https://www.usnews.com/best-colleges/rankings)

关于，这四类排名的更多介绍，可以看这个：  
[https://www.zhihu.com/question/20825030/answer/71336291](https://www.zhihu.com/question/20825030/answer/71336291)

这里，我们选取相对比较权威也比较符合国情的第一个ARWU的排名结果。打开官网，可以看到有英文版和中文版排名，这里选取中文版。  
放图  
可以看到，排名非常齐全，从2003年到最新的2018年都有，非常好。
同时，可以看到这是世界500强的大学排名，而我们需要的是中国（包括港澳台）的大学的排名。   
怎么办呢？ 当然不能一年年地复制然后再从500条数据里一条条筛选出中国的，这里就要用爬虫来实现了。可以参考不久前的一篇爬取表格的文章：
放公众号文章10行代码爬取全国上市公司

### 抓取数据 ###
#### 分析url ####
首先，分析一下URL:
```html
http://www.zuihaodaxue.com/ARWU2018.html
http://www.zuihaodaxue.com/ARWU2017.html
...
http://www.zuihaodaxue.com/ARWU2009.html
```
可以看到，url非常有规律，只有年份数字在变。很简单就能构造出for循环。
格式如下：
```python
url = 'http://www.zuihaodaxue.com/ARWU%s.html' % (str(year))
```
下面就可以开始写爬虫了。  
#### 获取网页内容 ####
```python

import requests
try:
    url = 'http://www.zuihaodaxue.com/ARWU%s.html' % (str(year))

    response = requests.get(url,headers = headers)

    # 2009-2015用'gbk'，2016-2018用'utf-8'
    if response.status_code == 200:
        # return response.text  # text会乱码，content没有问题
        return response.content
    return None

except RequestException:
print('爬取失败')
```
上面需要注意的是，不同年份网页采用的编码不同，返回response.test会乱码，返回response.content则不会。关于编码乱码的问题，以后单独写一篇文章。

#### 解析内容 ####
用read_html函数一行代码来抓取表格，然后输出：
```python
tb = pd.read_html(html)[0]
print(tb)
```
可以看到，很顺利地表格就被抓取了下来：
