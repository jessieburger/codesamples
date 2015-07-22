#!/usr/bin/env python

import argparse
import numpy
import pandas
from matplotlib import pyplot
from scipy import interpolate
from sklearn import cross_validation
from sklearn import linear_model

class FBN:
    def __init__(self):
        self.planting_dataframe = None
        self.harvest_dataframe = None
        self.interpolated_dataframe = None
        self.train_ylabel = None
        self.train_Xdata = None
        self.test_ylabel = None
        self.test_Xdata = None

    def match_planting_harvest(self, planting_filename, harvest_filename):
        # Load both planting and harvest files
        self.planting_dataframe = pandas.read_csv(planting_filename, delimiter=',')
        self.harvest_dataframe = pandas.read_csv(harvest_filename, delimiter=',')

        # Interpolate planting data for the harvest lat/longs
        # Since we have a 2D grid and continuous values, perform bilinear interpolation,
        # which will look smoother than nearest neighbor interpolation
        # However, the "variety" is categorical and thus can't be bilinearly interpolated,
        # so instead we can use nearest neighbor
        # Interpolation turns out to be a common enough function that scipy provides it
        gd_linear = interpolate.griddata(self.planting_dataframe.values[:,:2],
                                         self.planting_dataframe.values[:,3:],
                                         self.harvest_dataframe.values[:,:2])
        gd_nearest = interpolate.griddata(self.planting_dataframe.values[:,:2],
                                          self.planting_dataframe.values[:,2:3],
                                          self.harvest_dataframe.values[:,:2],
                                          method='nearest')
        interpolated_columns = self.harvest_dataframe.columns.append(self.planting_dataframe.columns[2:])
        interpolated_array = numpy.hstack((self.harvest_dataframe.values, gd_nearest, gd_linear))
        self.interpolated_dataframe = pandas.DataFrame(interpolated_array, columns=interpolated_columns).dropna(how='any')
        # If we just want to interpolate all columns as nearest neighbor, uncomment:
        # gd = interpolate.griddata(self.planting_dataframe.values[:,:2], self.planting_dataframe.values[:,2:], self.harvest_dataframe.values[:,:2], method='nearest')
        # interpolated_array = numpy.hstack((self.harvest_dataframe.values, gd))
        # self.interpolated_dataframe = pandas.DataFrame(interpolated_array, columns=interpolated_columns)

        # Create test and validation sets
        self.train_ylabel, self.test_ylabel, self.train_Xdata, self.test_Xdata = cross_validation.train_test_split(self.interpolated_dataframe.values[:,2:3], self.interpolated_dataframe.values[:,4:-1])
        return self.interpolated_dataframe

    def explore_data(self):
        linear = linear_model.LinearRegression()
        linear.fit(self.train_Xdata, self.train_ylabel)
        print "Linear Coefficients:"
        print linear.coef_
        print "Linear Train Score (R^2):"
        print linear.score(self.train_Xdata, self.train_ylabel)
        print "Linear Test Score (R^2):"
        print linear.score(self.test_Xdata, self.test_ylabel)

        # sgd = linear_model.SGDRegressor()
        # sgd.fit(self.train_Xdata, self.train_ylabel)
        # print "SGD Coefficients:"
        # print sgd.coef_
        # print "SGD Train Score:"
        # print sgd.score(self.train_Xdata, self.train_ylabel)
        # print "SGD Test Score:"
        # print sgd.score(self.test_Xdata, self.test_ylabel)

        self.interpolated_dataframe.plot(kind='scatter', x=u'seeding_rate', y=u'seed_spacing', c=u'yield')
        # sr = self.interpolated_dataframe.plot(kind='scatter', x=u'seeding_rate', y=u'yield', c='r')
        # ss = self.interpolated_dataframe.plot(kind='scatter', x=u'seed_spacing', y=u'yield', c='g', ax=sr)
        # s = self.interpolated_dataframe.plot(kind='scatter', x=u'speed', y=u'yield', c='b', ax=ss)
        # pyplot.show()

    # Making this a separate function to preserve the requested signature
    # of the match_planting_harvest function (take 2 arguments, return data frame)
    def save(self, interpolate_filename, figure_filename):
        self.interpolated_dataframe.to_csv(interpolate_filename, delimiter=',', index=False)
        pyplot.savefig(figure_filename)

def main():
    arg_parser = argparse.ArgumentParser('Load and Analyze Planting and Harvest Data')
    arg_parser.add_argument('--planting', type=str, default='planting_sample_data.csv', help='planting data file name, default \'planting_sample_data.csv\'')
    arg_parser.add_argument('--harvest', type=str, default='harvest_sample_data.csv', help='harvest data file name, default \'harvest_sample_data.csv\'')
    arg_parser.add_argument('--interpolate', type=str, default='interpolate_sample_data.csv', help='interpolated data file name, default \'interpolate_sample_data.csv\'')
    arg_parser.add_argument('--figure', type=str, default='figure.png', help='figure file name, default \'figure.png\'')
    args = arg_parser.parse_args()
    fbn = FBN()
    fbn.match_planting_harvest(args.planting, args.harvest)
    fbn.explore_data()
    fbn.save(args.interpolate, args.figure)

if __name__ == "__main__":
    main()
