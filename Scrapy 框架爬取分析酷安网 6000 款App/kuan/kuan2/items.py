# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Kuan2Item(scrapy.Item):
    # define the fields for your item here like:
    # url = scrapy.Field()
    name = scrapy.Field()
    volume = scrapy.Field()
    download = scrapy.Field()
    follow = scrapy.Field()
    comment = scrapy.Field()
    tags = scrapy.Field()
    score = scrapy.Field()
    num_score = scrapy.Field()

