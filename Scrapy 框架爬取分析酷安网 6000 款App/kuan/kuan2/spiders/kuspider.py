# -*- coding: utf-8 -*-
import scrapy
from kuan2.items import Kuan2Item
import re
import logging  # 要先安装好

logging.basicConfig(filename='kuan.log', filemode='w', level=logging.WARNING,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')
# https://juejin.im/post/5aee70105188256712786b7f
logging.warning("warn message")
logging.error("error message")


class KuspiderSpider(scrapy.Spider):
    name = 'kuspider'
    allowed_domains = ['www.coolapk.com']
    start_urls = ['https://www.coolapk.com/apk/']

    # 每个请求之间设置延迟
    # https://stackoverflow.com/questions/30404364/scrapy-delay-request
    custom_settings = {
        # "DOWNLOAD_DELAY": 2,  # 延迟2s
        # "CONCURRENT_REQUESTS_PER_DOMAIN": 8 # 每秒默认并发8次，可适当降低
    }
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }

    # 循环爬取第一种方法，直接构造全部url
    def start_requests(self):
        pages = []
        for page in range(1,2):  # 一共有610页
            url = 'https://www.coolapk.com/apk/?page=%s' % page
            page = scrapy.Request(
                url, callback=self.parse, headers=self.headers)
            pages.append(page)
        return pages

    def parse(self, response):
        # print(response.text)
        contents = response.css('.app_left_list>a')
        for content in contents:
            url = content.css('::attr("href")').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse_url)

        # # 循环爬取第二种方法获取翻页节点，循环爬取下一页
        # next_page = response.css('.pagination li:nth-child(8) a::attr("href")').extract_first()
        # url = response.urljoin(next_page)
        # # print(url) # test ok
        # yield scrapy.Request(url,callback=self.parse )

    def parse_url(self, response):
        item = Kuan2Item()
        item['name'] = response.css('.detail_app_title::text').extract_first()
        results = self.get_comment(response)
        item['volume'] = results[0]
        item['download'] = results[1]
        item['follow'] = results[2]
        item['comment'] = results[3]
        item['tags'] = self.get_tags(response)
        item['score'] = response.css('.rank_num::text').extract_first()
        num_score = response.css('.apk_rank_p1::text').extract_first()
        item['num_score'] = re.search('共(.*?)个评分', num_score).group(1)
        yield item

    def get_comment(self, response):
        messages = response.css('.apk_topba_message::text').extract_first()
        result = re.findall(
            r'\s+(.*?)\s+/\s+(.*?)下载\s+/\s+(.*?)人关注\s+/\s+(.*?)个评论.*?', messages)

        if result:  # 不为空
            results = list(result[0])
            return results

    def get_tags(self, response):
        data = response.css('.apk_left_span2')
        tags = [item.css('::text').extract_first() for item in data]
        return tags
