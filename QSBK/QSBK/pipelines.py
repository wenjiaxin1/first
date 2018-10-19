# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
class QsbkPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient()
        qsbk = client['qsbk']
        self.duanzi = qsbk['duanzi']
    def process_item(self, item, spider):
        #如果要插入的段子的title（哪个频道的第几页的第几个段子）已经存在于数据库，那么就更新段子内容；
        #如果title不存在数据库，则直接将该段子插入
        self.duanzi.update({'title': item.get('title')}, {'$set': dict(item)}, True)

        return item
