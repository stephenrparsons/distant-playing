from pymongo import MongoClient

client = MongoClient()
db = client['items']
collection = db['moby_items']

# Remove items that have no description or genre (91).
collection.delete_many({"$and":[
    {"description":{"$exists":False}},
    {"genre":{"$exists":False}},
]})
