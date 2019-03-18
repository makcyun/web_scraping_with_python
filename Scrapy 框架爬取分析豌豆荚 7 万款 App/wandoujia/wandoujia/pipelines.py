# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pymongo
from scrapy.pipelines.images import ImagesPipeline
import sys
from scrapy.exceptions import DropItem

class MongoPipeline(object):
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url = crawler.settings.get('MONGO_URL'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )
    
    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self,item,spider):
        name = item.__class__.__name__
        # self.db[name].insert(dict(item))
        self.db[name].update_one(item, {'$set': item}, upsert=True)
        return item

    def close_spider(self,spider):
        self.client.close()
    
# 下载到同一个文件夹
# class ImagedownloadPipeline(ImagesPipeline):
#     def get_media_requests(self,item,info):
#         if item['icon_url']:
#             yield scrapy.Request(item['icon_url'])

#     def item_completed(self,results,item,info):
#         image_path = [x['path'] for ok,x in results if ok]
#         if not image_path:
#             raise DropItem('Item contains no images')
#         return item

# 分文件夹下载
class ImagedownloadPipeline(ImagesPipeline):
    def get_media_requests(self,item,info):
        if item['icon_url']:
            yield scrapy.Request(item['icon_url'],meta={'item':item})

    def file_path(self, request, response=None, info=None):
        name = request.meta['item']['app_name']
        cate_name = request.meta['item']['cate_name']
        child_cate_name = request.meta['item']['child_cate_name']

        # path1 = os.getcwd()
        path1 = r'/wandoujia/%s/%s' %(cate_name,child_cate_name)
        path = r'{}\{}.{}'.format(path1, name, 'jpg')
        return path

    def item_completed(self,results,item,info):
        image_path = [x['path'] for ok,x in results if ok]
        if not image_path:
            raise DropItem('Item contains no images')
        return item