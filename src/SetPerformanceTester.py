__author__ = 'Adam'

import argparse
import random
import time
import os
import sys
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
            self.parts = kwargs.get('parts', 600)
            self.nodes = kwargs.get('nodes', 5000)
            self.load_random_data(self.parts, self.nodes)

    def timefunc(func):
        """Main timing function wrapper that is used to test performance of the tests. The
            wrapper should be put around the main tests and expects each function that it
            wraps to return [FILL UN THIS BLANK]

            The wrapper makes the function it wraps return a dictionary that is an entry
            for the report on the tests.  The entry is in the format:

            {'test': the test name (the function name),
            'data_information': the data structure used for the parts adn the container and
                                the size of the data,
            'timed_result': the amount of time the test took}

            This can and should be changed to use time.perf_counter() for better timing.

            More on this to come, most likely.

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            r = func(*args, **kwargs)
            end = time.time()
            return {'test': func.__name__, 'data_information': r, 'timed_result': end - start}
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

    def load_random_data(self, parts, nodes):
        """Generate and load random data based on the given nodes and parts."""

        self.parts = parts
        self.nodes = nodes

        if self.verbose:
            print 'Generating random data using nodes:' + str(nodes) + \
                ' parts:' + str(parts)

        node_list = []
        node_list.extend(range(1, nodes))

        # for each part we want to add a random number of nodes from the node list
        for i in range(1, parts):
            self.data_dict[i] = random.sample(node_list, random.randint(2, len(node_list)))

    def run_tests(self):
        """Run tests and populate the test report."""

        self.test_report = []

        #build data sets
        dict_of_sets = self.build_dict_of_sets(self.data_dict)
        set_of_sets = self.build_set_of_sets(self.data_dict)

        #run tests
        self.test_report.append(self.dicts_any_intersection_node_test(self.data_dict))
        self.test_report.append(self.dicts_any_intersection_node_test(dict_of_sets))
        self.test_report.append(self.sets_any_intersection_node_test(set_of_sets))

        # print results
        self.print_tests_results()

    def print_tests_results(self):
        """Print the test results, broken out for future enhancements."""

        for test in self.test_report:
            print test

    @timefunc
    def dicts_any_intersection_node_test(self, data):
        """A simple way to find if parts share a common node using a dictionary of lists or sets.
            An improvement would be to not double check the parts against each other."""

        data_size = sys.getsizeof(data)
        container_type = type(data)
        part_type = None

        for part in data:
            if not part_type:
                part_type = type(data[part])
            for union_part in data:
                if part != union_part:
                    for node in data[part]:
                        if node in data[union_part]:
                            break
        return {'container_type': container_type, 'part_type': part_type, 'data_size': data_size}

    @timefunc
    def sets_any_intersection_node_test(self, data):
        """A simple way to find if parts share a common node using sets of sets. An improvement
            would be to not double check the parts against each other."""

        data_size = sys.getsizeof(data, 0)
        container_type = type(data)
        part_type = None

        for part in data:
            if not part_type:
                part_type = type(part)
            for union_part in data:
                if part != union_part:
                    for node in part:
                        if node in union_part:
                            break
        return {'container_type': container_type, 'part_type': part_type, 'data_size': data_size}

    @staticmethod
    def build_dict_of_sets(data):
        """Build set of sets for tests"""

        data_sets = {}

        for part in data:
            data_sets[part] = set(data[part])

        return data_sets

    @staticmethod
    def build_set_of_sets(data):
        """Build set of sets for tests"""

        data_sets = set()

        for part in data:
            data_sets.add(frozenset(data[part]))

        return data_sets

    def create_intersection_report(self, data=None):
        """Determine if two parts have intersecting nodes and save to intersection report"""

        if not data:
            data = self.data_dict

        self.intersection_report_data = []

        for part in data:
            report_row = []

            for union_part in data:
                if part == union_part:
                    report_row.append(True)
                else:
                    union_flag = False
                    for node in data[part]:
                        if node in data[union_part]:
                            union_flag = True
                            break
                    report_row.append(union_flag)
            self.intersection_report_data.append(report_row)

    def print_intersection_report(self):
        try:
            filename = ''

            if self.data_filename:
                filename = '../output/' + self.data_filename + '.results.txt'
            else:
                filename = '../output/random.results.p' + str(self.parts) + '.n' + str(self.nodes) + '.txt'

            if self.verbose:
                print 'Printing Report data to ' + filename

            with open(filename, 'wt') as f:
                for part_number, part in enumerate(self.intersection_report_data, start=1):
                    f.write('Part Number:' + str(part_number) + '\n')
                    f.write('-------------------------' + '\n')
                    for union_part_number, union_test_bool in enumerate(self.intersection_report_data[part_number-1],
                                                                        start=1):

                        f.write('Union Set:' + str(part_number) + '\t Set: ' + str(union_part_number) + '\t flag:' +
                                str(union_test_bool) + '\n')

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
                    help='output results of the intersection report to file instead of system')
parser.add_argument('-pandas',
                    dest='pandas',
                    action='store_true',
                    help='only run the pandas version')
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
    if args.parts and args.nodes:
        if args.verbose:
            print 'Starting with data using nodes:' + str(args.nodes) + \
                ' parts:' + str(args.parts)
        set_perm_tester = SetPerformanceTester(verbose=args.verbose, nodes=args.nodes, parts=args.parts)
    else:
        if args.nodes:
            if args.verbose:
                print 'Notice: You did not include a number for parts.'
            set_perm_tester = SetPerformanceTester(verbose=args.verbose, nodes=args.nodes)
        elif args.parts:
            if args.verbose:
                print 'Notice: you did not include a number for nodes.'
            set_perm_tester = SetPerformanceTester(verbose=args.verbose, parts=args.parts)
        else:
            if args.verbose:
                print 'Notice: No information given using defaults.'
            set_perm_tester = SetPerformanceTester(verbose=args.verbose)

if args.verbose:
    print 'Starting the test....'

set_perm_tester.run_tests()

if args.file_out:

    if args.verbose:
        print 'Writing out intersection results....'

    set_perm_tester.create_intersection_report()
    set_perm_tester.print_intersection_report()

if args.verbose:
    print 'Testing Completed....'
