# Copyright 2016 Udey Rishi
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import os
import logging

TEXT_FLAVOUR = 'text'
USELESS_FIELDS = {'url', 'usage', 'status', 'statusInfo', 'totalTransactions'}

class AlchemyAPIError(Exception):
    def __init__(self, message, response):
        super(AlchemyAPIError, self).__init__(message)
        self.response = response

    def get_cause(self):
        return self.response['statusInfo']

    def __str__(self):
        return super(AlchemyAPIError, self).__str__() + ' Cause: ' + self.get_cause()

    def __repr__(self):
        return super(AlchemyAPIError, self).__repr__() + ' Cause: ' + self.get_cause()

class AlchemyFileAnalyzer(object):
    def __init__(self, api, transaction_limit_callback):
        self.api = api
        self.transaction_limit_callback = transaction_limit_callback

    def analyze(self, file_name):
        # temp place holder
        result = dict()
        with open(file_name, 'r') as f:
            text = f.read()

        result['entities'] = self.__api_executor(file_name,
            lambda: self.api.entities(TEXT_FLAVOUR, text, {'sentiment': 1}))
        result['keywords'] = self.__api_executor(file_name,
            lambda: self.api.keywords(TEXT_FLAVOUR, text, {'sentiment': 1}))
        result['concepts'] = self.__api_executor(file_name,
            lambda: self.api.concepts(TEXT_FLAVOUR, text))
        result['category'] = self.__api_executor(file_name,
            lambda: self.api.category(TEXT_FLAVOUR, text))
        result['doc_sentiment'] = self.__api_executor(file_name,
            lambda: self.api.sentiment(TEXT_FLAVOUR, text))
        return result

    def __api_executor(self, file_name, api_func):
        while True:
            try:
                return self.__error_checking_api_executor(file_name, api_func)
            except AlchemyAPIError as e:
                if e.response['statusInfo'] == 'daily-transaction-limit-exceeded':
                    repeat = self.transaction_limit_callback(self)
                    if not repeat:
                        raise

    def __error_checking_api_executor(self, file_name, api_func):
        result = api_func()
        if 'status' in result and result['status'].lower() == 'error':
            raise AlchemyAPIError('Erroneous response when processing file ' + file_name + '.', result)

        self.__remove_keys(result, USELESS_FIELDS)
        return result

    @staticmethod
    def __remove_keys(dictionary, keys):
        for k in keys:
            if k in dictionary:
                dictionary.pop(k)


class AlchemyDirectoryAnalyzer(object):
    def __init__(self, file_analyzer, source, destination, recursive, logger):
        self.__file_analyzer = file_analyzer
        self.__source = source
        self.__destination = destination
        self.__recursive = recursive
        self.__logger = logger

    def run(self):
        for root, _, file_names in os.walk(self.__source):
            for file_name in file_names:
                if self.__should_skip_file(file_name):
                    continue

                file_name = os.path.join(root, file_name)
                output_file = self.__get_output_file_path(file_name)

                if self.__logger is not None:
                    self.__logger.debug('Processing file: {0} >> Output file: {1}'.format(file_name, output_file))

                nlp_result = self.__file_analyzer.analyze(file_name)
                self.__make_dirs(output_file)

                with open(output_file, 'w') as f:
                    json.dump(nlp_result, f, sort_keys=True, indent=4)

            if not self.__recursive:
                break

    @staticmethod
    def __should_skip_file(file_name):
        # System file
        return file_name.startswith('.')

    def __get_output_file_path(self, file_name):
        if self.__source.endswith(os.path.sep):
            destination = self.__destination if self.__destination.endswith(os.path.sep) \
                            else self.__destination + os.path.sep
        else:
            destination = self.__destination if not self.__destination.endswith(os.path.sep) \
                            else self.__destination[:self.__destination.rfind(os.path.sep)]

        return file_name.replace(self.__source, destination) + '.json'

    @staticmethod
    def __make_dirs(file):
        if not os.path.exists(os.path.dirname(file)):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
