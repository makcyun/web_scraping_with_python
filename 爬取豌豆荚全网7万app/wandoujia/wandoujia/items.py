# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class WandoujiaItem(scrapy.Item):
    cate_name = scrapy.Field() #分类名
    child_cate_name = scrapy.Field() #分类编号
    app_name = scrapy.Field()   # 子分类名
    install = scrapy.Field()    # 子分类编号
    volume = scrapy.Field()     # 体积
    comment = scrapy.Field()    # 评论
    icon_url = scrapy.Field()   # 图标url
    