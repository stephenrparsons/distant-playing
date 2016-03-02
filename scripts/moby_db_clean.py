from pymongo import MongoClient
import dateutil.parser, datetime

client = MongoClient()
db = client['items']
collection = db['moby_items']

# Remove items that have no description or genre (91 of them).
collection.delete_many({'$and':[
    {'description':{'$exists':False}},
    {'genre':{'$exists':False}},
]})

#Remove items that have year 2016 (only 1, not enough to be useful)
collection.delete_many({'year': 2016})

# Give dates standard format
def getYear(dateStr):
    return dateutil.parser.parse(dateStr, default=datetime.datetime(1,1,1,0,0)).year

def getMonth(dateStr):
    return dateutil.parser.parse(dateStr, default=datetime.datetime(1,1,1,0,0)).month

def getDay(dateStr):
    return dateutil.parser.parse(dateStr, default=datetime.datetime(1,1,1,0,0)).day

def years():
    for record in collection.find(modifiers={'$snapshot':True}):
        year = getYear(record['released'])
        # month = getMonth(record['released'])
        # day = getDay(record['released'])
        collection.update_one({'_id':record['_id']}, {'$set': {'year': year}})
