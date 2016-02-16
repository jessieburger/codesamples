#!/usr/bin/env python
import argparse
import csv
import json
from operator import itemgetter
import numpy
import pandas
from matplotlib import pyplot
from sklearn import cross_validation, linear_model, tree

class ExploreGenericData:
    def __init__(self):
        self.dataframe = None
        self.train_ylabel = None
        self.train_Xdata = None
        self.test_ylabel = None
        self.test_Xdata = None

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
                datum = json.loads(line)
                print datum # this is a dict of values

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

    def load_data(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if (ext == 'csv'):
            self.dataframe = pandas.read_csv(filename, delimiter=',')
        elif (ext == 'tsv'):
            self.dataframe = pandas.read_csv(filename, delimiter='\t')
        elif (ext == 'json'):
            self.dataframe = pandas.read_json(filename)
        # Handle any missing values by dropping the whole row
        self.dataframe = self.dataframe.dropna(how='any')
        # Create test and validation sets
        print self.dataframe.shape, self.dataframe.size
        self.train_ylabel, self.test_ylabel, self.train_Xdata, self.test_Xdata = cross_validation.train_test_split(self.dataframe.values[:,2:3], self.dataframe.values[:,4:])
        print self.test_Xdata

    def save_data(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if (ext == 'csv'):
            self.dataframe.to_csv(filename, delimiter=',')
        elif (ext == 'tsv'):
            self.dataframe.to_csv(filename, delimiter='\t')
        elif (ext == 'json'):
            self.dataframe.to_json(filename)

    def explore_data(self):
        linear = linear_model.LinearRegression()
        linear.fit(self.train_Xdata, self.train_ylabel)
        featwts = linear.coef_
        print "Linear Coefficients:"
        print featwts
        print sorted(zip(featwts, range(len(featwts))), key=lambda fw: abs(fw[0]), reverse=True)
        print "Linear Train Score (R^2):"
        print linear.score(self.train_Xdata, self.train_ylabel)
        print "Linear Test Score (R^2):"
        print linear.score(self.test_Xdata, self.test_ylabel)

        sgd = linear_model.SGDRegressor()
        sgd.fit(self.train_Xdata, self.train_ylabel)
        featwts = sgd.coef_
        print "SGD Coefficients:"
        print featwts
        print sorted(zip(featwts, range(len(featwts))), key=lambda fw: abs(fw[0]), reverse=True)
        print "SGD Train Score (R^2):"
        print sgd.score(self.train_Xdata, self.train_ylabel)
        print "SGD Test Score (R^2):"
        print sgd.score(self.test_Xdata, self.test_ylabel)

        dt = tree.DecisionTreeRegressor()
        dt.fit(self.train_Xdata, self.train_ylabel)
        featwts = dt.feature_importances_
        print "Tree Feature Importances:"
        print featwts
        print sorted(zip(featwts, range(len(featwts))), key=lambda fw: abs(fw[0]), reverse=True)
        print "Tree Train Score (R^2):"
        print dt.score(self.train_Xdata, self.train_ylabel)
        print "Tree Test Score (R^2):"
        print dt.score(self.test_Xdata, self.test_ylabel)

        # self.dataframe.plot(kind='scatter', x=u'seeding_rate', y=u'seed_spacing', c=u'yield')
        # self.dataframe.plot(kind='scatter', x=u'seeding_rate', y=u'speed', c=u'yield')
        # self.dataframe.plot(kind='scatter', x=u'seed_spacing', y=u'speed', c=u'yield')
        # v = self.dataframe.plot(kind='scatter', x=u'variety', y=u'yield', c='b')
        # sr = self.dataframe.plot(kind='scatter', x=u'seeding_rate', y=u'yield', c='r')
        # ss = self.dataframe.plot(kind='scatter', x=u'seed_spacing', y=u'yield', c='g')
        # s = self.dataframe.plot(kind='scatter', x=u'speed', y=u'yield', c='b')
        # ss = self.dataframe.plot(kind='scatter', x=u'seed_spacing', y=u'yield', c='g', ax=sr)
        # s = self.dataframe.plot(kind='scatter', x=u'speed', y=u'yield', c='b', ax=ss)
        pyplot.show()

def main():
    arg_parser = argparse.ArgumentParser('Load and Analyze Generic Data')
    arg_parser.add_argument('--data', '-d', type=str, default='data.csv', help='input data file name, default \'data.csv\'')
    arg_parser.add_argument('--type', '-t', type=str, default='r', help='problem type, \'r\' for regression or \'c\' for classication, default \'r\'')
    # arg_parser.add_argument('--graph', '-g', type=str, default='graph.png', help='output figure file name, default \'graph.png\'')
    args = arg_parser.parse_args()
    gendata = ExploreGenericData()
    gendata.load_data(args.data)
    gendata.explore_data()
    # gendata.save_graph(args.data, args.graph)

if __name__ == "__main__":
    main()
