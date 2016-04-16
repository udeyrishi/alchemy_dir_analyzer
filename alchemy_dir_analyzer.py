class AlchemyDirectoryAnalyzer(object):
    def __init__(self, api, source, destination, recursive):
        self.__api = api
        self.__source = source
        self.__destination = destination
        self.__recursive = recursive

    def run(self):
        print('Hello, World!')
