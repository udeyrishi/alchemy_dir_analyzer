#!/usr/bin/env python

from alchemyapi_python.alchemyapi import AlchemyAPI
from alchemyapi_python.alchemyapi import BadApiKeyError
from argparse import ArgumentParser
from alchemy_analyzer import AlchemyDirectoryAnalyzer
from alchemy_analyzer import AlchemyFileAnalyzer


def read_api_key(path_to_key):
    with open(path_to_key, 'r') as f:
        return f.readline().strip()

def get_args():
    parser = ArgumentParser()
    parser.add_argument('key', help='The path to the file containing the AlchemyAPI key')
    parser.add_argument('source', help='The path to the source directory')
    parser.add_argument('destination', help='The path to the destination directory. '
        + "Directories will be created if they don't exist")
    parser.add_argument('-r', '--recursive', help='Recursively process subdirectories',
        action='store_true')

    return parser.parse_args()

def main():
    args = get_args()
    try:
        api = AlchemyAPI(api_key=read_api_key(args.key))
        file_analyzer = AlchemyFileAnalyzer(api)
    except BadApiKeyError as e:
        print(("The keys file '{0}' should contain proper Alchemy API key in the "
            + "first line. Cause: {1}").format(args.key, str(e)))
        exit(-1)

    AlchemyDirectoryAnalyzer(file_analyzer=file_analyzer,
                            source=args.source,
                            destination=args.destination,
                            recursive=args.recursive).run()

if __name__ == '__main__':
    main()