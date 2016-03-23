from pymongo import MongoClient
import gensim, multiprocessing, time
import numpy as np

client = MongoClient()
desc_collection = client['items']['moby_items']
doc2vec_model_path = 'models/doc2vec.model'

desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
desc_count = desc_cursor.count()

documents =[gensim.models.doc2vec.TaggedDocument(record['words_to_use'], [str(record['_id'])]) for record in desc_cursor]
tags = [document.tags[0] for document in documents]

cores = multiprocessing.cpu_count()

# model=gensim.models.doc2vec.Doc2Vec(size=100, workers=cores, alpha=0.025, min_alpha=0.025)
# model.build_vocab(documents)

# for epoch in range(10):
#     model.train(documents)
#     model.alpha -= 0.002
#     model.min_alpha = model.alpha

# model.save(doc2vec_model_path)

model = gensim.models.doc2vec.Doc2Vec.load(doc2vec_model_path)

counter = 0
start = time.time()

desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
for record in desc_cursor:
    similarity_vector = [float(elem) for elem in model.docvecs.most_similar(str(record['_id']), topn=False)]

    # remove link to self
    similarities = [list(elem) for elem in filter(lambda x: x[0] != str(record['_id']), zip(tags, similarity_vector))]
    unpacked = zip(*similarities)
    new_tags = list(unpacked[0])
    similarity_vector = list(unpacked[1])

    std_dev = np.std(similarity_vector)
    maximum = np.amax(similarity_vector)

    # reduce it in size by taking only those within half a standard deviation of the most similar (average degree 5)
    similarities = filter(lambda x: x[1] >= maximum-(std_dev/2.0), similarities)

    desc_collection.update_one({'_id': record['_id']}, {'$set': {'similarities': similarities}})

    counter += 1
    if counter % 100 == 0:
        end = time.time()
        print 'Done ' + str(counter) + ' out of ' + str(desc_count) + ' in ' + str((end - start))

# Gives titles of games most similar to Wii Sports
# [desc_collection.find({'_id':ObjectId(idd)})[0]['title'] for idd in [item[0] for item in model.docvecs.most_similar(str(desc_collection.find({'title':'Wii Sports'})[0]['_id']))]]
