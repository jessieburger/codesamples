#!/usr/bin/env python
import argparse
import bs4
import csv
import json
import nltk
import os
import pprint
import string
from gensim import corpora, models, similarities
from gensim.models import ldamodel, phrases, word2vec
from gensim.similarities import docsim
from nltk.corpus import stopwords

class ExploreGenericText:
    def __init__(self):
        self.documents = None
        self.texts = None
        self.dictionary = None
        self.bow_corpus = None
        self.tfidf_corpus = None
        self.lda_corpus = None

    def read_csv(self, filename):
        with open(filename, 'r') as datafile:
            datareader = csv.reader(datafile, delimiter=',')
            for datum in datareader:
                print datum # this is a list of values

    def read_tsv(self, filename):
        with open(filename, 'r') as datafile:
            datareader = csv.reader(datafile, delimiter='\t')
            for datum in datareader:
                print datum # this is a list of values

    def read_json(self, filename):
        with open(filename, 'r') as datafile:
            for line in datafile:
                datum = json.reads(line)
                print datum # this is a dict of values

    def read_sgml(self, filename):
        with open(filename, 'r') as datafile:
            # nltk expects ascii encoding, not utf8
            return bs4.BeautifulSoup(datafile, 'html.parser').get_text().encode('ascii', 'ignore')
            # return bs4.BeautifulSoup(datafile, 'html.parser').get_text().encode('utf8', 'ignore')

    def write_csv(self, filename):
        with open(filename, 'w') as datafile:
            datawriter = csv.writer(datafile, delimiter=',')
            for row in data: #TODO
                datawriter.write(data)

    def write_tsv(self, filename):
        with open(filename, 'w') as datafile:
            datawriter = csv.writer(datafile, delimiter='\t')
            for row in data: #TODO
                datawriter.write(data)

    def write_json(self, filename):
        with open(filename, 'w') as datafile:
            for row in data: #TODO
                datafile.write(json.dumps(row))

    def load_text(self, filename):
        filelist = os.listdir(filename) if os.path.isdir(filename) else [os.path.basename(filename)]
        filepath = os.path.dirname(filename)
        # Assume all files are same ext
        ext = filelist[0].rsplit('.', 1)[1]
        if (ext == 'csv'):
            self.documents = [self.read_csv(os.path.join(filepath, f)) for f in filelist]
        elif (ext == 'tsv'):
            self.documents = [self.read_tsv(os.path.join(filepath, f)) for f in filelist]
        elif (ext == 'json'):
            self.documents = [self.read_json(os.path.join(filepath, f)) for f in filelist]
        elif (ext.endswith('ml')):
            self.documents = [self.read_sgml(os.path.join(filepath, f)) for f in filelist]

        # Simply split tokens on whitespace and remove punctuation
        # self.texts = [[word for word in document.lower().split()] for document in self.documents]
        # self.texts = [[word for word in document.translate(None, string.punctuation).lower().split()] for document in self.documents]
        # self.texts = [[''.join(ch for ch in word if ch.isalnum()) for word in document.lower().split()] for document in self.documents]
        # self.texts = [[''.join(ch for ch in word if ch.isalnum()) for word in nltk.word_tokenize(document)] for document in self.documents]

        # Split tokens on whitespace, remove punctuation, and remove stop words
        stop_words = set(stopwords.words('english'))
        # self.texts = [[word for word in document.lower().split()
        #                         if word not in stop_words]
        #               for document in self.documents]
        # self.texts = [[word for word in document.translate(None, string.punctuation).lower().split()
        #                         if word not in stop_words]
        #               for document in self.documents]
        self.texts = [[''.join(ch for ch in word if ch.isalnum())
                        for word in document.lower().split()
                            if word not in stop_words]
                      for document in self.documents]

        # Split tokens using nltk, remove punctuation, and remove stop words
        # self.texts = [[''.join(ch for ch in word if ch.isalnum()).lower()
        #                 for word in nltk.word_tokenize(document)
        #                     if word not in stop_words]
        #               for document in self.documents]

        # Create bigrams
        # bigrams = phrases.Phrases(self.texts)
        # self.texts = bigrams[self.texts]
        # print self.texts

        # Map tokens to ids
        self.dictionary = corpora.Dictionary(self.texts)
        print self.dictionary
        # Create document bag of words vectors of (id, count) tuples
        self.bow_corpus = [self.dictionary.doc2bow(text) for text in self.texts]

    def explore_text(self, num_topics):
        # Create document vectors of (id, tfidf) tuples
        tfidf = models.TfidfModel(self.bow_corpus)
        self.tfidf_corpus = tfidf[self.bow_corpus]

        # LDA expects a bag of words corpus
        lda = ldamodel.LdaModel(self.bow_corpus, id2word=self.dictionary, passes=20, iterations=200, num_topics=num_topics, minimum_probability=1.0/num_topics)
        self.lda_corpus = lda[self.bow_corpus]

        print "Top Words per Topic:"
        pprint.pprint(lda.show_topics(num_topics=num_topics, num_words=5))
        # print "Topic Coherence:"
        # print lda.top_topics(self.bow_corpus, num_words=2)
        print "Document Topics:"
        pprint.pprint([(self.filelist[f], l) for f, l in enumerate(self.lda_corpus)])
        # for f, l in enumerate(self.lda_corpus):
        #     print self.filelist[f], l

        index = docsim.MatrixSimilarity(self.lda_corpus, num_best=2)
        print "Document Similarity:"
        pprint.pprint([[s for s in similarities] for similarities in index])
        # for doc, similarities in enumerate(index):
        #     pprint.pprint((doc, [s for s in similarities]))
        #     # print doc, similarities[1] if similarities else similarities

        # w2v = word2vec.Word2Vec(sentences=self.texts)
        # print "Most Similar Words:"
        # print w2v.most_similar(positive=['doctor'], negative=[], topn=5)
        # print w2v.most_similar(positive=[], negative=['doctor'], topn=5)
        # print w2v.most_similar(positive=['prescription'], negative=[], topn=5)
        # print w2v.most_similar(positive=[], negative=['prescription'], topn=5)

def main():
    arg_parser = argparse.ArgumentParser('Load and Analyze Generic Text')
    arg_parser.add_argument('--text', '-t', type=str, default='text.tsv', help='input text file name, default \'text.tsv\'')
    arg_parser.add_argument('--numtopics', '-n', type=int, default=20, help='number of topics, default \'20\'')
    # arg_parser.add_argument('--graph', '-g', type=str, default='graph.png', help='output figure file name, default \'graph.png\'')
    args = arg_parser.parse_args()
    gentext = ExploreGenericText()
    gentext.load_text(args.text)
    gentext.explore_text(args.numtopics)

if __name__ == "__main__":
    main()
