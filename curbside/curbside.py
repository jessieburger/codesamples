import argparse
import json

class Curbside:
    def __init__(self):
        self.store_zipcode_dict = {}
        self.zipcode_store_dict = {}

    def load_data(self, filename):
        with open(filename) as datafile:
            for line in datafile.readlines():
                datum = json.loads(line)
                store = str(datum['store_id'])
                # don't convert to int because zips have leading 0s
                zipcode = str(datum['zipcode'][:-2])
                if store in self.store_zipcode_dict:
                    self.store_zipcode_dict[store].add(zipcode)
                else:
                    # store as a set because there are duplicates in input file
                    self.store_zipcode_dict[store] = {zipcode}
                if zipcode in self.zipcode_store_dict:
                    self.zipcode_store_dict[zipcode].add(store)
                else:
                    self.zipcode_store_dict[zipcode] = {store}

    def greedy_find_zips(self):
        include_zipcodes = set() # ZIP codes to include
        include_zipcode_stores = set() # stores returned by the incuded ZIP codes
        # sort the stores but the number of ZIP codes which return them,
        # so that we can greedily add the most rare stores
        sorted_stores = sorted(self.store_zipcode_dict.items(), key=lambda sz: len(sz[1]))
        for (store, zipcodes) in sorted_stores:
            if store not in include_zipcode_stores:
                zipcode = zipcodes.pop()
                include_zipcodes.add(zipcode)
                include_zipcode_stores |= self.zipcode_store_dict[zipcode]
        print "Include ZIP codes:"
        print include_zipcodes
        print len(include_zipcodes), "included ZIP codes of", len(self.zipcode_store_dict)
        print len(include_zipcode_stores), "included stores of", len(self.store_zipcode_dict)

def main():
    arg_parser = argparse.ArgumentParser('Find minimal subset of ZIP codes')
    arg_parser.add_argument('-d', '--data', type=str, default='data.json', help='input data file name, default \'data.json\'')
    args = arg_parser.parse_args()
    curbside = Curbside()
    curbside.load_data(args.data)
    curbside.greedy_find_zips()

if __name__ == "__main__":
    main()
