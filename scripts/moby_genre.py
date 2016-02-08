from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
import csv

client = MongoClient()
db = client['items']
collection = db['moby_items']

# graph games per year
def showGamesPerYear():
    cursor = collection.aggregate([
        {'$group': {'_id': '$year', 'total': {'$sum': 1}}},
    ])
    gamesPerYear = sorted([[record['_id'], record['total']] for record in cursor])
    # dict(gamesPerYear) could be stored to avoid calculating this
    # every time.

    years = [item[0] for item in gamesPerYear]
    games = [item[1] for item in gamesPerYear]

    fig, ax = plt.subplots(1)
    ax.plot(years, games)

    fig.autofmt_xdate()

    plt.show()

# graph genres over time
def showGenresOverTime():
    cursor = collection.aggregate([
        {'$unwind': '$genre'},
        {'$group': {'_id': {'year': '$year', 'genre': '$genre'}, 'total': {'$sum': 1}}},
    ])

    # If a game has multiple genres, each one is given equal
    # weight. This could (maybe should) be reconsidered.
    genresOverTime = sorted([[record['_id'], record['total']] for record in cursor])
    years = sorted(list(set([record[0]['year'] for record in genresOverTime])))
    genres = sorted(list(set([record[0]['genre'] for record in genresOverTime])))

    dataDict = {}
    for record in genresOverTime:
        if record[0]['year'] not in dataDict.keys():
            dataDict[record[0]['year']] = {}
        dataDict[record[0]['year']][record[0]['genre']] = record[1]

    dataArray = [[0 for j in range(len(years))] for i in range(len(genres))]
    for i in range(len(genres)):
        for j in range(len(years)):
            if years[j] in dataDict.keys():
                if genres[i] in dataDict[years[j]].keys():
                    dataArray[i][j] = dataDict[years[j]][genres[i]]

    fig, ax = plt.subplots(1)

    y = np.row_stack(dataArray)
    percent = y / y.sum(axis=0).astype(float)*100
    ax.stackplot(years, percent)
    ax.margins(0,0)
    ax.set_title("Genre shares over time")
    ax.set_ylabel('Percent of total games (%)')
    ax.set_xlabel('Year')

    fig.autofmt_xdate()

    plt.show()

# graph themes over time
def showThemesOverTime():
    cursor = collection.aggregate([
        {'$unwind': '$theme'},
        {'$group': {'_id': {'year': '$year', 'theme': '$theme'}, 'total': {'$sum': 1}}},
    ])

    # If a game has multiple themes, each one is given equal
    # weight. This could (maybe should) be reconsidered.
    themesOverTime = sorted([[record['_id'], record['total']] for record in cursor])
    years = sorted(list(set([record[0]['year'] for record in themesOverTime])))
    themes = sorted(list(set([record[0]['theme'] for record in themesOverTime])))

    dataDict = {}
    for record in themesOverTime:
        if record[0]['year'] not in dataDict.keys():
            dataDict[record[0]['year']] = {}
        dataDict[record[0]['year']][record[0]['theme']] = record[1]

    dataArray = [[0 for j in range(len(years))] for i in range(len(themes))]
    for i in range(len(themes)):
        for j in range(len(years)):
            if years[j] in dataDict.keys():
                if themes[i] in dataDict[years[j]].keys():
                    dataArray[i][j] = dataDict[years[j]][themes[i]]

    fig, ax = plt.subplots(1)

    y = np.row_stack(dataArray)
    percent = y / y.sum(axis=0).astype(float)*100
    ax.stackplot(years, percent)
    ax.margins(0,0)
    ax.set_title("Theme shares over time")
    ax.set_ylabel('Percent of total games (%)')
    ax.set_xlabel('Year')

    fig.autofmt_xdate()

    plt.show()


# showGamesPerYear()
showGenresOverTime()
showThemesOverTime()
