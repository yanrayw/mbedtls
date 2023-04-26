#!/usr/bin/env python3

"""
This program is used to automatically add test dependencies.
"""

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import glob
import os
import re
import sys
import textwrap

DEPEND_REGEX = r'depends_on:.*'
# example input arguments
LOCATE_REGEX = r'\s*.*AES-192.*'
DEPEDENCIES = ["!MBEDTLS_AES_ONLY_128_BIT_KEY_LENGTH"]

class ExampleAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        PrintHelper.print_info("Running an example program")
        gen_dep = GenTestData(LOCATE_REGEX, DEPEDENCIES, None)
        gen_dep.walk_all()
        parser.exit()

class PrintHelper():
    """Helper function to display additional message type in print."""
    @staticmethod
    def print_info(*arg):
        print("Info:", *arg, file=sys.stderr)

    @staticmethod
    def print_warning(*arg):
        print("Warning:", *arg, file=sys.stderr)

    @staticmethod
    def print_err(*arg):
        print("Error:", *arg, file=sys.stderr)

class TestDataExplorer:
    """
    An iterator over test cases to handle their dependencies.
    This is an abstract class.
    """
    @staticmethod
    def split_test_case(data_stream):
        """Split data stream to one set for each test case."""
        res = []
        test_case = []
        for line in data_stream:
            if line == '\n':
                res.append(test_case)
                test_case = []
            else:
                test_case.append(line)
        res.append(test_case)

        return res

    @staticmethod
    def collect_test_directories():
        """Get the relative path for the TLS and Crypto test directories."""
        if os.path.isdir("tests"):
            tests_dir = "tests"
        elif os.path.isdir("suites"):
            tests_dir = "."
        elif os.path.isdir("../suites"):
            tests_dir = ".."
        return [tests_dir]

class GenTestData(TestDataExplorer):
    """
    An iterator over test cases to handle their dependencies.
    """
    def __init__(self, locate, dependencies, test_directories):
        super().__init__()
        self.locate_regex = locate
        self.dependencies = dependencies
        self.snippets = {'file_content_pool': os.path.basename(__file__)}
        if test_directories is None:
            self.test_directories = self.collect_test_directories()
        else:
            self.test_directories = test_directories

    def __found_target(self, tc_str: str) -> bool:
        """Return if we found target string."""
        return bool(re.match(self.locate_regex, tc_str))

    # @staticmethod
    # def __check_arguments(tc_str: str) -> bool:
        # """TODO"""
        # check = "PSA_KEY_TYPE_AES"
        # arguments = tc_str.split(":")
        # print(arguments)
        # for idx in range(0, len(arguments)):
            # if arguments[idx] == check:
                # if len(arguments[idx + 1]) > 32:
                    # return True
        # return False

    def __append_dep(self, single_test):
        """Return a list of depedencies to be appended."""
        if not single_test:
            return single_test
        index = 0
        while single_test[index].startswith('#'):
            index += 1
            if index >= len(single_test):
                return single_test

        if self.__found_target(single_test[index].strip()) or\
           self.__found_target(single_test[-1].strip()):
            if re.match(DEPEND_REGEX, single_test[index + 1].strip()):
                extra_deps = ""
                for dep in self.dependencies:
                    if dep in single_test[index + 1]:
                        extra_deps = ""
                        break
                    extra_deps += ":" + dep
                extra_deps += '\n'
                single_test[index + 1] = single_test[index + 1].strip('\n') + extra_deps
            else:
                extra_deps = "depends_on:" + ":".join(self.dependencies) + "\n"
                single_test.append(single_test[index + 1])
                single_test[index + 1] = extra_deps
        return single_test

    # TODO
    def __remove_dep(self, single_test):
        """TODO"""
        if not single_test:
            return single_test
        if re.match(self.locate_regex, single_test[0].strip()):
            if re.match(DEPEND_REGEX, single_test[1].strip()):
                new_deps = "depends_on"
                orig_deps = single_test[1].split(':')
                for o_dep in orig_deps:
                    if any(o_dep in dep for dep in self.dependencies):
                        continue
                    new_deps += ":" + o_dep
                if new_deps == "depends_on":
                    single_test[1] = [single_test[0]] + [single_test[2]]
                else:
                    single_test[1] = [single_test[0]] + [new_deps + '\n'] +\
                                     [single_test[2]]
        return single_test

    def __parse_file(self, data_file_name):
        """Parse file and tweak its dependencies based on REGEX rule."""
        if data_file_name is None:
            return
        file_content = []
        with open(data_file_name, 'r') as data_file:
            splitted_test = self.split_test_case(data_file)
            for test_case in splitted_test:
                file_content += self.__append_dep(test_case) + ['\n']
                # file_content += self.__remove_dep(test_case) + ['\n']
        self.snippets[data_file_name] = file_content[:-1]

    def __write_file(self, data_file_name):
        """Write content to target file."""
        if data_file_name is None:
            return
        with open(data_file_name, "w", encoding='utf-8') as data_file:
            for line in self.snippets[data_file_name]:
                data_file.write(line)


    def __gene_dep(self, data_file_name):
        """Generate dependencies for data file."""
        self.__parse_file(data_file_name)
        self.__write_file(data_file_name)

    def __walk_test_suite(self, data_file_name):
        """An interface to parse file and handle its dependencies"""
        self.__gene_dep(data_file_name)

    def walk_all(self):
        """Iterate all test cases under target directories"""
        if self.test_directories is None:
            PrintHelper.print_err("No test directories")
            return

        for directory in self.test_directories:
            # walk through tests/suites/*.data
            for data_file_name in glob.glob(os.path.join(directory, 'suites',
                                                         '*.data')):
                self.__walk_test_suite(data_file_name)

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.register('action', 'run_example', ExampleAction)
    group_help = parser.add_argument_group('Example arguments',
                                           'running an example program')
    group_help.add_argument("--example", nargs=0, action="run_example",
                            help=textwrap.dedent('''\
                            Set this option to run with an example. (Default: off, undo --example)
                            Note: this will tweak tests/suites/*.data by default.
                            '''))

    parser.add_argument("-r", "--regex", dest="locate_regex", required=True,
                        help=textwrap.dedent('''\
                        Regular Expression to match. E.g: -r \\\\s*.*AES-192.*
                        This is identical to LOCATE_REGEX=r'\\s*.*AES-192.*'
                        '''))
    parser.add_argument("-d", "--dependencies", dest="dependencies",
                        required=True, action='append',
                        help=textwrap.dedent('''\
                        Dependencies to add on target directories.
                        E.g: -d \\!MBEDTLS_AES_ONLY_128_BIT_KEY_LENGTH
                        DEPEDENCIES = ["!MBEDTLS_AES_ONLY_128_BIT_KEY_LENGTH"]
                        '''))
    parser.add_argument("-t", "--directories", dest="test_directories",
                        default=None,
                        help=textwrap.dedent('''\
                        Dependencies to add on target directories.
                        E.g: -d \\!MBEDTLS_AES_ONLY_128_BIT_KEY_LENGTH
                        DEPEDENCIES = ["!MBEDTLS_AES_ONLY_128_BIT_KEY_LENGTH"]
                        '''))


    args = parser.parse_args()

    if args.locate_regex and args.dependencies:
        gen_dep = GenTestData(args.locate_regex, args.dependencies,
                              args.test_directories)
        gen_dep.walk_all()

if __name__ == '__main__':
    main()
