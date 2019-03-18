
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-26 09:55:10
# @Author  : suke1900 (johnny824lee@gmail.com)
# @blog    : http://www.makcyun.top


"""
代理 IP 的设置方式
阿布云代理 IP

免费代理 IP 网站：
国内：https://www.xicidaili.com/
国外：https://free-proxy-list.net/ (需翻墙)

参考教程：
https://chenjiabing666.github.io/2017/03/26/scrapy%E8%AE%BE%E7%BD%AE%E4%BB%A3%E7%90%86ip/


"""


import requests
import time
import random

# 测试网站
# url = "http://icanhazip.com"
# url = "https://icanhazip.com"
url = "https://www.wandoujia.com/wdjweb/api/category/more"

# 备选
# url = 'http://httpbin.org/get'
# url = 'https://www.youtube.com/' # 翻墙测试


def get_proxies():
    proxies = [
        {'http': 'socks5://127.0.0.1:1080'},
        {'https': 'socks5://127.0.0.1:1080'}]

    proxies = random.choice(proxies)
    print(proxies)

    try:
        for i in range(1, 6):
            # response = requests.get(url) # 不用代理
            response = requests.get(url, proxies=proxies, timeout=3)  # 使用代理
            # timeout 设置超时抛出异常，避免拖延太久
            print(response.status_code)
            if response.status_code == 200:
                print(response.text)

    except requests.ConnectionError as e:
        print(e.args)


def get_Abuypun_proxies():
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "HS77K12Q77V4G9MD"  # 需购买后获取
    proxyPass = "4131FFDFCE27F104"  # 需购买后获取

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    for i in range(1, 6):
        resp = requests.get(url, proxies=proxies)
        print('第%s次请求的IP为：%s' % (i, resp.text))


def main():
    get_proxies()
    # get_Abuypun_proxies()

if __name__ == '__main__':
    main()
