# Modified from https://github.com/vladsandulescu/topics

from pymongo import MongoClient
import nltk, time, logging, gensim

client = MongoClient()
desc_collection = client['items']['moby_items']
tags_collection = client['tags']['moby_description_tags']
corpus_collection = client['tags']['moby_description_corpus']

def tag_descriptions():
    desc_cursor = desc_collection.find({}, {'title': 1, 'description': 1, 'year': 1})
    desc_count = desc_cursor.count()
    # not sure if I need the below, will enable if I do
    # descCursor.batch_size(1000)

    # could consider another stopwords list
    stopwords = nltk.corpus.stopwords.words('english')

    tagger = nltk.tag.perceptron.PerceptronTagger()

    done = 0
    start = time.time()

    for record in desc_cursor:
        words = []
        sentences = nltk.sent_tokenize(record["description"].lower())

        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            text = [word for word in tokens if word not in stopwords]
            tagged_text = nltk.tag._pos_tag(tokens, None, tagger)

            for word, tag in tagged_text:
                words.append({'word': word, 'pos': tag})

        tag_document = {
            'year': record['year'],
            'text': record['description'],
            'words': words,
        }
    
        tags_collection.insert(tag_document)
    
        done += 1
        if done % 1000 == 0:
            end = time.time()
            print 'Done ' + str(done) + ' out of ' + str(desc_count) + ' in ' + str((end - start))

def create_corpus():
    desc_cursor = tags_collection.find()
    desc_count = desc_cursor.count()
    
    lem = nltk.stem.wordnet.WordNetLemmatizer()

    done = 0
    start = time.time()

    for record in desc_cursor:
        nouns = []
        words = [word for word in record['words'] if word['pos'] in ['NN', 'NNS']]

        for word in words:
            nouns.append(lem.lemmatize(word['word']))

        corpus_document = {
            'year': record['year'],
            'text': record['text'],
            'words': nouns,
        }

        corpus_collection.insert(corpus_document)

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
            yield self.desc_dictionary.doc2bow(desc['words'])

    def serialize(self):
        gensim.corpora.BleiCorpus.serialize(self.corpus_path, self, id2word=self.desc_dictionary)
        return self

class Dictionary(object):
    def __init__(self, cursor, dictionary_path):
        self.cursor = cursor
        self.dictionary_path = dictionary_path

    def build(self):
        self.cursor.rewind()
        dictionary = gensim.corpora.Dictionary(desc["words"] for desc in self.cursor)
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

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
dictionary_path = 'models/dictionary.dict'
corpus_path = "models/corpus.lda-c"
lda_num_topics = 50
lda_model_path = "models/lda_model_50_topics.lda"

def train_corpus():
    desc_cursor = corpus_collection.find()

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

display_topics()
