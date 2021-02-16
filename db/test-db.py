from pymongo import MongoClient
from pprint import pprint
client = MongoClient("mongodb://username:password@localhost:27017")
db = client['amazon-scraper-db']
status = db.command("serverStatus")
pprint(status)