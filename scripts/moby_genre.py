from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler

client = MongoClient()
db = client['items']
collection = db['moby_items']

# graph title lengths in words
def showTitleLengths():
    cursor = collection.find({}, {'title': True, 'year': True}, modifiers={'$snapshot': True})

    titleLengthsByYear = {}

    for record in cursor:
        numWords = len(record['title'].split())
        if record['year'] in titleLengthsByYear.keys():
            titleLengthsByYear[record['year']].append(numWords)
        else:
            titleLengthsByYear[record['year']] = [numWords]

    for year in titleLengthsByYear.keys():
        lengths = titleLengthsByYear[year]
        titleLengthsByYear[year] = {'average': float(sum(lengths)) / len(lengths), 'std_dev': np.std(titleLengthsByYear[year])}

    averageLengthByYear = sorted([[int(year), titleLengthsByYear[year]['average'], titleLengthsByYear[year]['std_dev']] for year in titleLengthsByYear.keys()])

    years = [item[0] for item in averageLengthByYear]
    averageLengths = [item[1] for item in averageLengthByYear]
    std_devs = [item[2] for item in averageLengthByYear]

    fig, ax = plt.subplots(1)
    ax.set_title('Average title length in words by year')
    ax.set_ylabel('Average title length')
    ax.set_xlabel('Year')
    ax.plot(years, averageLengths)

    fig.autofmt_xdate()

    plt.show()

    fig, ax = plt.subplots(1)

    ax.set_title('Standard deviation of title length in words by year')
    ax.set_ylabel('Title length std_dev')
    ax.set_xlabel('Year')
    ax.plot(years, std_devs)

    fig.autofmt_xdate()

    plt.show()

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
    ax.set_title('Games per year')
    ax.set_ylabel('Games')
    ax.set_xlabel('Year')
    ax.plot(years, games)

    fig.autofmt_xdate()

    plt.show()

# graph a moby database field (str) over time in a 100% stacked plot
def showPercentagesOverTime(field):
    cursor = collection.aggregate([
        {'$unwind': '$'+field},
        {'$group': {'_id': {'year': '$year', 'field': '$'+field}, 'total': {'$sum': 1}}},
    ])

    # If a game has multiple genres, each one is given equal
    # weight. This could (maybe should) be reconsidered.
    fieldsOverTime = sorted([[record['_id'], record['total']] for record in cursor])
    years = sorted(list(set([record[0]['year'] for record in fieldsOverTime])))
    fields = sorted(list(set([record[0]['field'] for record in fieldsOverTime])))

    dataDict = {}
    for record in fieldsOverTime:
        if record[0]['year'] not in dataDict.keys():
            dataDict[record[0]['year']] = {}
        dataDict[record[0]['year']][record[0]['field']] = record[1]

    dataArray = [[0 for j in range(len(years))] for i in range(len(fields))]
    for i in range(len(fields)):
        for j in range(len(years)):
            if years[j] in dataDict.keys():
                if fields[i] in dataDict[years[j]].keys():
                    dataArray[i][j] = dataDict[years[j]][fields[i]]

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
    ax.set_prop_cycle(cycler('color', ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd', '#ffe8c7', '#ccebc5','#ffed6f']))
    y = np.row_stack(dataArray)

    # sort by total for each field
    sums = np.sum(y, axis=1)
    indices = sums.argsort()[::-1]
    y = np.take(y, indices, axis=0)

    # make sure to sort labels how their fields were sorted
    max_fields = 12
    label_list = list(np.take(fields, indices))[0:max_fields]

    # beyond n most significant fields, categorize as other
    y, other = y[:max_fields], np.sum(y[max_fields:], axis=0)
    if sum(other) != 0:
        y = np.vstack([y, other])
        label_list.append('other')

    percent = y / y.sum(axis=0).astype(float)*100
    ax.stackplot(years, percent, labels=label_list)
    ax.margins(0,0)
    # move the upper left edge of the legend relative to axes
    # coordinates and reverse the label order
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper left', bbox_to_anchor=[1,1])
    ax.set_title(field + ' shares over time')
    ax.set_ylabel('Percent of total games (%)')
    ax.set_xlabel('Year')

    fig.autofmt_xdate()

    plt.show()

# These might work but there are too many publishers and developers so
# matplotlib crashes with current implementation.
# showPercentagesOverTime('publishedBy')
# showPercentagesOverTime('developedBy')

showGamesPerYear()
showTitleLengths()
showPercentagesOverTime('genre')
showPercentagesOverTime('theme')
showPercentagesOverTime('perspective')
showPercentagesOverTime('platforms')
