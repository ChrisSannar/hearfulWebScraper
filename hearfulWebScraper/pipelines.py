# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

from scrapy import settings

# class MongoDBPipeline(object):

#   def __init__(self):
#     connection = pymongo.MongoClient(
#       settings['MONGODB_SERVER'],
#       settings['MONGODB_PORT']
#     )
#     db = connection[settings['MONGODB_DB']]
#     self.collection = db[settings['MONGODB_COLLECTION']]
#     print("INITIALIZED MONGODB PIPELINE")

#   def process_item(self, item, spider):
#     print("-------------------------------")
#     for data in item:
#       print(data)
#     print("-------------------------------")

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

MONGODB_URI = "mongodb://username:password@localhost:27017"
MONGODB_DB = "test"
MONGODB_COLLECTION = "testing"

class HearfulwebscraperPipeline:
  
  def __init__(self):
    # connection = pymongo.MongoClient(
    #   settings['MONGODB_SERVER'],
    #   settings['MONGODB_PORT']
    # )
    # db = connection[settings['MONGODB_DB']]
    # self.collection = db[settings['MONGODB_COLLECTION']]
    pass

  def open_spider(self, spider):
    self.client = pymongo.MongoClient(MONGODB_URI)
    self.db = self.client[MONGODB_DB]
    self.db[MONGODB_COLLECTION].delete_many({})
    print("MONGO CLEARED")

  def close_spider(self, spider):
    self.client.close()

  def process_item(self, item, spider):
    # print("-------------------------------")
    # print(item)
    # print("-------------------------------")
    self.db[MONGODB_COLLECTION].insert_one(item)
    return item
