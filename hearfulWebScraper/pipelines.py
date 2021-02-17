import pymongo

from scrapy.utils.project import get_project_settings

# The overall pipeline for the project
class HearfulwebscraperPipeline:

  def process_item(self, item, spider):
    return item

# Saves each item to the database
class AmazonItemsMongoDBPipeline:
  
  def __init__(self):
    self.settings = get_project_settings()
    pass

  # Make sure to close the connection when we're done and let the spider handle it's own connection
  def close_spider(self, spider):
    spider.client.close()

  # Simply inserts the item when we're finished
  def process_item(self, item, spider):
    spider.db[self.settings.get('MONGODB_REVIEWS_COLLECTION')].insert_one(item)
    return item
