__author__ = 'Adam'

import argparse
import random
import time
import os
import sys
#import pandas as pd
import re
from functools import wraps


class SetPerformanceTester:
    """A simple for testing performance of comparing sets, called parts, of objects,
        called nodes. It can be used with a file containing the node/part data or can
        generate it's own random data from provided node and part numbers or defaults.

        File should be in the format:

        [node_id as integer][delimiter][part_id as integer]

        The delimiter can be either ",", "\t"(tab), " "(space), or "|" and after the part_id
        there can be anything else on the same line.

        Keyword arguments:
        filename -- path to the file with the input information
        parts -- the number of nodes to use (default 50)
        nodes -- the imaginary part (default 1000)
        verbose -- write out debug information to system (default False)

        NOTE: the pandas stuff is commented out so you can run on base python and because
        it is not well implemented.

    """

    intersection_report_data = []
    test_report = []

    def __init__(self, **kwargs):

        self.verbose = kwargs.get('verbose', False)
        filename = kwargs.get('filename', '')
        self.data_dict = {}

        if filename:
            self.data_filename = os.path.basename(filename)
            self.load_data_from_filename(filename)
        else:
            self.data_filename = ''
            self.parts = kwargs.get('parts', 200)
            self.nodes = kwargs.get('nodes', 3000)
            self.max_nodes = kwargs.get('max_nodes')

            if not self.max_nodes:
                self.max_nodes = self.nodes

            self.load_random_data(self.parts, self.nodes, self.max_nodes)

    def timetest(func):
        """Main timing function wrapper that is used to test performance of the tests. The
            wrapper should be put around the main tests and expects each function that it
            wraps to return a dictionary with information about the test. This is not
            necessary but it would be nice. The format is:

            {'container_type': data structure holding the parts,
            'part_type': data structure describing the parts (sets of nodes),
            'data_size': size of complete container}

            The wrapper runs a set of timed runs of the function and returns a dictionary
            that is an entry for the report on the tests.  The entry is in the format:

            {'test': the test name (the function name),
            'data_information': described above,
            'timed_result': the amount of time the test took}

            This can and should be changed to use time.perf_counter() instead on time.time() for better timing.

            There is also an issue of load on machine you are testing on so you should try to do this in an
            isolated environment.

            More on this to come, most likely.

        """
        @wraps(func)
        def wrapper(*args, **kwargs):

            trials = 10
            total = 0

            for i in range(0, trials):

                print func.__name__ + " Trial:" + str(i + 1)

                start = time.time()
                r = func(*args, **kwargs)
                end = time.time()

                total += end - start

            return {'test': func.__name__, 'data_information': r, 'average_time': total / trials, 'trials': trials}
        return wrapper

    def load_data_from_filename(self, filename):
        """Load data from given file."""
        try:
            if self.verbose:
                print 'Getting data from ' + filename

            self.data_dict = {}

            with open(filename, 'rt') as f:
                for line in f:
                    data_match = re.match(r'^(\d+)[\,|\t|\s|\|](\d+)$', line)
                    if data_match:
                        node = int(data_match.group(1))
                        part = int(data_match.group(2))

                        if part in self.data_dict:
                            self.data_dict[part].append(node)
                        else:
                            self.data_dict[part] = [node]

        except Exception, e:
            print 'Unexpected error:', str(e)
            print 'Problems loading data from file.'
            exit()

    def load_random_data(self, parts, nodes, max_nodes):
        """Generate and load random data based on the given nodes and parts."""

        self.parts = parts
        self.nodes = nodes
        self.max_nodes = max_nodes

        if self.verbose:
            print 'Generating random data using nodes:' + str(nodes) + \
                ' parts:' + str(parts) + ' max nodes:' + str(max_nodes)

        node_list = []
        node_list.extend(range(1, nodes))

        # for each part we want to add a random number of nodes from the node list
        for i in range(1, parts):
            self.data_dict[i] = random.sample(node_list, random.randint(2, max_nodes))

    def run_tests(self):
        """Run tests and populate the test report."""

        self.test_report = []

        #dict of unsorted lists
        dict_of_un_lists = self.dict_un_lists_intersection_test(self.data_dict)
        self.test_report.append(dict_of_un_lists)

        #dict of sets
        dict_of_sets = self.build_dict_of_sets(self.data_dict)
        self.test_report.append(self.dict_sets_intersection_test(dict_of_sets))

        #pandas - experimental and probably not the way to use pandas
        # dict_of_pandas = self.build_dict_of_panda_series(self.data_dict)
        # self.test_report.append(self.dicts_any_intersection_node_test(dict_of_pandas))

        # print results

        if self.verbose:
            self.print_tests_results()

    def print_tests_results(self):
        """Print the test results, broken out for future enhancements."""

        for test in self.test_report:
            for detail in test:
                print detail + ': ', test[detail]


    def get_data_info(self,data):
        """This functions extracts the information we want to know about the data structures tested"""
        if data:
            container_type = type(data)
            #this would have to change if you were to use change data structures around
            part_type = type(data[min(data)])

            return {'container_type': container_type, 'part_type': part_type, 'data_size': sys.getsizeof(data)}

        return {'container_type': None, 'part_type': None, 'data_size': 0}


    @timetest
    def dict_un_lists_intersection_test(self, data):
        """A simple way to find if parts share a common node using a dictionary of unsorted lists.
            An improvement would be to change the type of the finished variable."""

        data_info = self.get_data_info(data)
        finished = []

        for part in data:
            for union_part in data:
                union = []
                if part != union_part and union_part not in finished:
                    for node in data[part]:
                        if node in data[union_part]:
                            union.append(node)
            finished.append(part)

        return data_info


    @timetest
    def dict_sets_intersection_test(self, data):
        """A simple way to find if parts share a common node using a dictionary of sets.
            An improvement would be to change the type of the finished variable."""

        data_info = self.get_data_info(data)
        finished = []

        for part in data:
            for union_part in data:
                if part != union_part and union_part not in finished:
                    data[part].intersection(data[union_part])
            finished.append(part)

        return data_info


    @staticmethod
    def build_dict_of_sets(data):
        """Build dicts of sets for tests. Broken out for now for possible testing."""

        data_sets = {}

        for part in data:
            data_sets[part] = set(data[part])

        return data_sets

    # @staticmethod
    # def build_dict_of_panda_series(data):
    #     """Build set of sets for tests but a dictionary of sets is a Dataframe in pandas
    #         so we need to research this."""
    #
    #     data_pandas = {}
    #
    #     for part in data:
    #         data_pandas[part] = pd.Series(data[part])
    #
    #     return data_pandas

    def create_intersection_report(self, data=None):
        """Determine if two parts have intersecting nodes and save to intersection report and save it to the report.
        The format of the report is [part, union_part, union_set]  """

        if not data:
            data = self.build_dict_of_sets(self.data_dict)

        self.intersection_report_data = []
        finished = []

        for part in data:
            for union_part in data:
                if part != union_part and union_part not in finished:
                    union_set = data[part].intersection(data[union_part])
                    self.intersection_report_data.append([part, union_part, union_set])
            finished.append(part)


    def print_intersection_report(self):
        """Print out report to the output directory based on nodes and parts"""
        try:
            filename = ''

            if self.data_filename:
                filename = '../output/' + self.data_filename + '.results.txt'
            else:
                filename = '../output/random.results.p' + str(self.parts) + '.n' + str(self.nodes) + '.txt'

            if self.verbose:
                print 'Printing Report data to ' + filename

            with open(filename, 'wt') as f:
                for report_row in self.intersection_report_data:
                    f.write(str(report_row[0]) + '|' + str(report_row[1]))
                    f.write(report_row[2])
                    f.write('\n')
        except Exception, e:
            print 'Unexpected error:', str(e)
            print 'Problems writing the data output file.'
            exit()


parser = argparse.ArgumentParser(description='Set Performance Tester')

parser.add_argument('-nodes',
                    dest='nodes',
                    type=int,
                    action='store',
                    help='number of nodes in the data set')
parser.add_argument('-maxNodes',
                    dest='max_nodes',
                    type=int,
                    action='store',
                    help='max number of nodes in each part')
parser.add_argument('-parts',
                    dest='parts',
                    type=int,
                    action='store',
                    help='number of parts in the data set')
parser.add_argument('-file',
                    dest='file',
                    type=str,
                    action='store',
                    help='path to the file you want to import data from')
parser.add_argument('-fileOut',
                    dest='file_out',
                    action='store_true',
                    help='output results of the intersection report to file')
parser.add_argument('-skipTests',
                    dest='skip_tests',
                    action='store_true',
                    help='do not run the tests')
parser.add_argument('-v',
                    dest='verbose',
                    action='store_true',
                    help='show more text output')
args = parser.parse_args()

set_perm_tester = None

if args.verbose:
    print 'Starting Set Performance Tester...'

if args.file:
    if args.verbose:
        print 'Using data from file:' + str(args.file)
    set_perm_tester = SetPerformanceTester(verbose=args.verbose,
                                           filename=args.file)
else:
    if args.parts and args.nodes and args.max_nodes:
        if args.verbose:
            print 'Starting with data using nodes:' + str(args.nodes) + \
                ' parts:' + str(args.parts) + ' maxNodes:' + str(args.max_nodes)
        set_perm_tester = SetPerformanceTester(verbose=args.verbose,
                                               nodes=args.nodes,
                                               parts=args.parts,
                                               max_nodes=args.max_nodes)
    else:
        if args.nodes:
            if args.verbose:
                print 'Notice: You did not include a number for parts.'
            set_perm_tester = SetPerformanceTester(verbose=args.verbose, nodes=args.nodes, max_nodes=args.max_nodes)
        elif args.parts:
            if args.verbose:
                print 'Notice: you did not include a number for nodes.'
            set_perm_tester = SetPerformanceTester(verbose=args.verbose, parts=args.parts, max_nodes=args.max_nodes)
        else:
            if args.verbose:
                print 'Notice: No information given using defaults.'
            set_perm_tester = SetPerformanceTester(verbose=args.verbose)

if args.verbose:
    print 'Starting the test....'

if args.skip_tests:
    print 'Skipping the tests....'
else:
    set_perm_tester.run_tests()

    if args.verbose:
        print 'Testing Completed....'

if args.file_out:
    if args.verbose:
        print 'Writing out intersection results....'

    set_perm_tester.create_intersection_report()
    set_perm_tester.print_intersection_report()

    if args.verbose:
        print 'Report Complete....'

if args.verbose:
    print 'Program Finished....'




