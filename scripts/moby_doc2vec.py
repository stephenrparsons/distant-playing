from pymongo import MongoClient
import gensim

client = MongoClient()
desc_collection = client['items']['moby_items']
doc2vec_model_path = 'models/doc2vec.model'

desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
desc_count = desc_cursor.count()

documents = (gensim.models.doc2vec.TaggedDocument(record['words_to_use'], [record['_id']]) for record in desc_cursor)

model = gensim.models.doc2vec.Doc2Vec(documents)
model.save(doc2vec_model_path)

