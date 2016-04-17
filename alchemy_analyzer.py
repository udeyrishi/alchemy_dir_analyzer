import json
import os

TEXT_FLAVOUR = 'text'
USELESS_FIELDS = {'url', 'usage', 'status', 'statusInfo', 'totalTransactions'}

class AlchemyAPIError(Exception):
    pass

class AlchemyFileAnalyzer(object):
    def __init__(self, api):
        self.__api = api

    def analyze(self, file_name):
        # temp place holder
        result = dict()
        with open(file_name, 'r') as f:
            text = f.read()

        result['entities'] = self.__api_executor(lambda: self.__api.entities(TEXT_FLAVOUR, text, {'sentiment': 1}))
        result['keywords'] = self.__api_executor(lambda: self.__api.keywords(TEXT_FLAVOUR, text, {'sentiment': 1}))
        result['concepts'] = self.__api_executor(lambda: self.__api.concepts(TEXT_FLAVOUR, text))
        result['category'] = self.__api_executor(lambda: self.__api.category(TEXT_FLAVOUR, text))
        result['doc_sentiment'] = self.__api_executor(lambda: self.__api.sentiment(TEXT_FLAVOUR, text))
        return result

    def __api_executor(self, api_func):
        result = api_func()
        if 'status' in result and result['status'].lower() == 'error':
            raise AlchemyAPIError('Erroneous response from Alchemy API with status info: ' + result['statusInfo'])

        self.__remove_keys(result, USELESS_FIELDS)

        return result

    @staticmethod
    def __remove_keys(dictionary, keys):
        for k in keys:
            if k in dictionary:
                dictionary.pop(k)


class AlchemyDirectoryAnalyzer(object):
    def __init__(self, file_analyzer, source, destination, recursive):
        self.__file_analyzer = file_analyzer
        self.__source = source
        self.__destination = destination
        self.__recursive = recursive

    def run(self):
        for root, _, file_names in os.walk(self.__source):
            for file_name in file_names:
                if self.__should_skip_file(file_name):
                    continue

                file_name = os.path.join(root, file_name)
                nlp_result = self.__file_analyzer.analyze(file_name)
                output_file = self.__get_output_file_path(file_name)
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
