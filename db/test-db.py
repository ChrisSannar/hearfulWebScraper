from pymongo import MongoClient
from pprint import pprint
client = MongoClient("mongodb://username:password@localhost:27017")
db = client['testing']
collection_name = "test"
# status = db.command("serverStatus")
# pprint(status)

# Crud operations
db[collection_name].delete_many({})
db[collection_name].insert_one({
  'test': "Izza test"
})
print("Record inserted")
db[collection_name].update_one({}, { "$set": { "test": "Izzanother test" }})
resp = db[collection_name].find_one()
print(resp)