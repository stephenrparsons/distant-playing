from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
import csv

client = MongoClient()
db = client['items']
collection = db['moby_items']

# graph games per year
cursor = (collection.aggregate([
    {'$group':{'_id':'$year','total':{'$sum':1}}}
]))
gamesPerYear = sorted([[record['_id'], record['total']] for record in cursor])

# dict(gamesPerYear) could be stored to avoid calculating this every time

years = [item[0] for item in gamesPerYear]
games = [item[1] for item in gamesPerYear]

fig, ax = plt.subplots(1)
ax.plot(years, games)

fig.autofmt_xdate()

plt.show()

# with open('gamesPerYear.csv', 'wb') as f:
#     w = csv.DictWriter(f, gamesPerYear.keys())
#     w.writeheader()
#     w.writerow(gamesPerYear)
