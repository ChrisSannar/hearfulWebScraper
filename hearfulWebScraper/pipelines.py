# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

# from scrapy.conf import settings

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# The overall pipeline for the project
class HearfulwebscraperPipeline:

  def process_item(self, item, spider):
    return item

# Saves each item to the database
class AmazonItemsMongoDBPipeline:
  
  def __init__(self):
    pass

  # Initialize the database
  # def open_spider(self, spider):
  #   self.client = pymongo.MongoClient(spider.MONGODB_URI)
  #   self.db = self.client[spider.MONGODB_DB]

  # Make sure to close the connection when we're done
  def close_spider(self, spider):
    # self.client.close()
    spider.client.close()

  # Simply inserts the item when we're finished
  def process_item(self, item, spider):
    spider.db[spider.MONGODB_REVIEWS_COLLECTION].insert_one(item)
    return item

MONGODB2_URI = "mongodb://username:password@localhost:27017"
MONGODB2_DB = "testing"
MONGODB2_COLLECTION = "test"

# Handle adding the quotes to the database for the quotes crawler
class QuotesMongoDBPipeline:

  def open_spider(self, spider):
    self.client = pymongo.MongoClient(MONGODB2_URI)
    self.db = self.client[MONGODB2_DB]
    self.db[MONGODB2_COLLECTION].delete_many({})

  def close_spider(self, spider):
    self.client.close()

  def process_item(self, item, spider):
    self.db[MONGODB2_COLLECTION].insert_one(item)
    return item
