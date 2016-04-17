import json
import os

SKIP_FILES = {'.DS_Store'}

class AlchemyFileAnalyzer(object):
    def __init__(self, api):
        self.__api = api

    def analyze(self, file_name):
        # temp place holder
        return {'file': file_name}


class AlchemyDirectoryAnalyzer(object):
    def __init__(self, file_analyzer, source, destination, recursive):
        self.__file_analyzer = file_analyzer
        self.__source = source
        self.__destination = destination
        self.__recursive = recursive

    def run(self):
        for root, _, file_names in os.walk(self.__source):
            for file_name in file_names:
                if file_name in SKIP_FILES:
                    continue

                file_name = os.path.join(root, file_name)
                nlp_result = self.__file_analyzer.analyze(file_name)
                output_file = self.__get_output_file_path(file_name)
                self.__make_dirs(output_file)

                with open(output_file, 'w') as f:
                    json.dump(nlp_result, f)

            if not self.__recursive:
                break

    def __get_output_file_path(self, file_name):
        if self.__source.endswith(os.path.sep):
            destination = self.__destination if self.__destination.endswith(os.path.sep) \
                            else self.__destination + os.path.sep
        else:
            destination = self.__destination if not self.__destination.endswith(os.path.sep) \
                            else self.__destination[:self.__destination.rfind(os.path.sep)]

        return file_name.replace(self.__source, destination) + '.json'

    def __make_dirs(self, file):
        if not os.path.exists(os.path.dirname(file)):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
