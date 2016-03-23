from pymongo import MongoClient
import networkx as nx
import dateutil.parser, datetime

# directed graph
G = nx.DiGraph()

client = MongoClient()
collection = client['items']['moby_items']

cursor = collection.find({'similarities': {'$exists': True}}, modifiers={'$snapshot': True})
count = cursor.count()

print count

for record in cursor:
    id_str = str(record['_id'])
    if id_str not in G:
        G.add_node(id_str)

    # add attributes
    G.node[id_str]['title'] = record['title']
    G.node[id_str]['year'] = record['year']
    G.node[id_str]['released'] = record['released']

    G.node[id_str]['perspective'] = ''
    if len(record['perspective']) > 0:
        G.node[id_str]['perspective'] = record['perspective'][0]

    G.node[id_str]['genre'] = ''
    if len(record['genre']) > 0:
        G.node[id_str]['genre'] = record['genre'][0]

    G.node[id_str]['theme'] = ''
    if len(record['theme']) > 0:
        G.node[id_str]['theme'] = record['theme'][0]

    G.node[id_str]['platforms'] = ''
    if len(record['platforms']) > 0:
        G.node[id_str]['platforms'] = record['platforms'][0]

    # add edges two ways for each connection
    sim = record['similarities']
    for s in sim:
        if str(s[0]) not in G:
            G.add_node(str(s[0]))
        if not (G.has_edge(str(s[0]), id_str) or G.has_edge(id_str, str(s[0]))):
            G.add_edge(str(s[0]), id_str, weight=s[1])
            G.add_edge(id_str, str(s[0]), weight=s[1])

print G.number_of_nodes(), G.number_of_edges()

# remove edges that go backwards in time so they only point forwards
for source in G.nodes():
    goes_to = G.neighbors(source)
    source_date = dateutil.parser.parse(G.node[source]['released'], default=datetime.datetime(1,1,1,0,0))
    for target in goes_to:
        target_date = dateutil.parser.parse(G.node[target]['released'], default=datetime.datetime(1,1,1,0,0))
        if source_date >= target_date:
            G.remove_edge(source, target)

print G.number_of_nodes(), G.number_of_edges()

nx.write_gexf(G, 'moby.gexf')
