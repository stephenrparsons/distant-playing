# Modified from https://github.com/vladsandulescu/topics

from pymongo import MongoClient
import nltk, time, logging, gensim, json, StringIO, csv
import zipfile as zf

client = MongoClient()
desc_collection = client['items']['moby_items']

def tag_descriptions():
    desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
    desc_count = desc_cursor.count()

    # could consider another stopwords list
    stopwords = nltk.corpus.stopwords.words('english')

    tagger = nltk.tag.perceptron.PerceptronTagger()

    done = 0
    start = time.time()

    for record in desc_cursor:
        words = []
        sentences = nltk.sent_tokenize(record['description'].lower())

        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            text = [word for word in tokens if word not in stopwords]
            tagged_text = nltk.tag._pos_tag(tokens, None, tagger)

            for word, tag in tagged_text:
                words.append({'word': word, 'pos': tag})

        desc_collection.update_one({'_id': record['_id']}, {'$set': {'words': words}})

        done += 1
        if done % 1000 == 0:
            end = time.time()
            print 'Done ' + str(done) + ' out of ' + str(desc_count) + ' in ' + str((end - start))

def create_corpus():
    desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
    desc_count = desc_cursor.count()

    lem = nltk.stem.wordnet.WordNetLemmatizer()

    done = 0
    start = time.time()

    for record in desc_cursor:
        words_to_use = []
        # select only nouns
        words = [word for word in record['words'] if word['pos'] in ['NN', 'NNS']]

        for word in words:
            words_to_use.append(lem.lemmatize(word['word']))

        desc_collection.update_one({'_id': record['_id']}, {'$set': {'words_to_use': words_to_use}})

        done += 1
        if done % 1000 == 0:
            end = time.time()
            print 'Done ' + str(done) + ' out of ' + str(desc_count) + ' in ' + str((end - start))

class Corpus(object):
    def __init__(self, cursor, desc_dictionary, corpus_path):
        self.cursor = cursor
        self.desc_dictionary = desc_dictionary
        self.corpus_path = corpus_path

    def __iter__(self):
        self.cursor.rewind()
        for desc in self.cursor:
            yield self.desc_dictionary.doc2bow(desc['words_to_use'])

    def serialize(self):
        gensim.corpora.BleiCorpus.serialize(self.corpus_path, self, id2word=self.desc_dictionary)
        return self

class Dictionary(object):
    def __init__(self, cursor, dictionary_path):
        self.cursor = cursor
        self.dictionary_path = dictionary_path

    def build(self):
        self.cursor.rewind()
        dictionary = gensim.corpora.Dictionary(desc['words_to_use'] for desc in self.cursor)
        dictionary.filter_extremes(keep_n=10000)
        dictionary.compactify()
        gensim.corpora.Dictionary.save(dictionary, self.dictionary_path)
        return dictionary

class Train:
    def __init__(self):
        pass

    @staticmethod
    def run(lda_model_path, corpus_path, num_topics, id2word):
        corpus = gensim.corpora.BleiCorpus(corpus_path)
        lda = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=id2word)
        lda.save(lda_model_path)
        return lda

def train_corpus():
    desc_cursor = desc_collection.find(modifiers={'$snapshot': True})

    dictionary = Dictionary(desc_cursor, dictionary_path).build()
    Corpus(desc_cursor, dictionary, corpus_path).serialize()
    Train.run(lda_model_path, corpus_path, lda_num_topics, dictionary)

def display_topics():
    dictionary = gensim.corpora.Dictionary.load(dictionary_path)
    corpus = gensim.corpora.BleiCorpus(corpus_path)
    lda = gensim.models.LdaModel.load(lda_model_path)

    i = 0
    for topic in lda.show_topics(num_topics=lda_num_topics):
        print '#' + str(i) + ': ' + str(topic)
        i += 1

class Predict():
    def __init__(self, dictionary_path, lda_model_path):
        self.dictionary = gensim.corpora.Dictionary.load(dictionary_path)
        self.lda = gensim.models.LdaModel.load(lda_model_path)

    def run(self, record):
        words_to_use = record['words_to_use']
        new_desc_bow = self.dictionary.doc2bow(words_to_use)
        new_desc_lda = self.lda[new_desc_bow]

        return new_desc_lda

def predict_topics():
    desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
    desc_count = desc_cursor.count()
    predict = Predict(dictionary_path, lda_model_path)
    lda = gensim.models.LdaModel.load(lda_model_path)
    dictionary = gensim.corpora.Dictionary.load(dictionary_path)

    done = 0
    start = time.time()

    for record in desc_cursor:
        topics = predict.run(record)

        # topic_list = []
        # for (topic_id, topic_weight) in topics:
        #     terms = lda.get_topic_terms(topic_id)
        #     topic_list.append((topic_weight, [dictionary.get(term[0]) for term in terms]))
        # topic_list = sorted(topic_list, reverse=True)
        # for topic in topic_list:
        #     print topic

        desc_collection.update_one({'_id': record['_id']}, {'$set': {'topic_weights': topics}})

        done += 1
        if done % 1000 == 0:
            end = time.time()
            print 'Done ' + str(done) + ' out of ' + str(desc_count) + ' in ' + str((end - start))

def output_vis_files():
    desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
    desc_count = desc_cursor.count()
    num_topics = 50.0
    lda = gensim.models.LdaModel.load(lda_model_path)
    dictionary = gensim.corpora.Dictionary.load(dictionary_path)

    # tw.json
    alpha = [1/num_topics for i in range(int(num_topics))]
    tw = []
    for topic_id in range(int(num_topics)):
        terms = lda.get_topic_terms(topic_id)
        words = [dictionary.get(term[0]) for term in terms]
        weights = [term[1] for term in terms]
        tw.append({'words': words, 'weights': weights})
    
    data = {'alpha': alpha, 'tw': tw}

    with open('tw.json', 'w') as outfile:
        json.dump(data, outfile)

    # meta.csv
    def clean(item):
        if isinstance(item, unicode) or isinstance(item, str):
            return item.encode('ascii', 'ignore').replace('"', '""').replace('\n', '').replace('\r', '').replace("'", '')
        elif isinstance(item, list):
            return str([clean(elem) for elem in item])
        else:
            return str(item)
    
    meta = []
    for record in desc_cursor:
        entry = [record['_id'], record['title'], record['publishedBy'], record['developedBy'], '', '', record['year'], '']
        
        meta.append([clean(item) for item in entry])

    meta_out = ''
    for entry in meta:
        meta_out += '"' + '","'.join(entry) + '"\n'

    with zf.ZipFile('meta.csv.zip', 'w') as z:
        z.writestr('meta.csv', meta_out)

    # dt.json.zip begins as dt.csv
    desc_cursor = desc_collection.find(modifiers={'$snapshot': True})
    dt = [[str(0) for i in range(int(num_topics))] for j in range(desc_count)]
    i = 0
    for record in desc_cursor:
        topic_weights = record['topic_weights']
        for topic_pair in topic_weights:
            dt[i][topic_pair[0]] = str(int(topic_pair[1]*10000))
        i += 1
        
    dt_out = ''
    for doc_id in range(len(dt)):
        dt_out += ','.join(dt[doc_id]) + '\n'
    with open('dt.csv', 'w') as outfile:
        outfile.write(dt_out)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    dictionary_path = 'models/dictionary.dict'
    corpus_path = "models/corpus.lda-c"
    lda_num_topics = 50
    lda_model_path = "models/lda_model_50_topics.lda"

    tag_descriptions()
    create_corpus()
    train_corpus()
    display_topics()
    predict_topics()
    output_vis_files()
