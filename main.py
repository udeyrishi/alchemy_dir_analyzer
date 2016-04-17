#!/usr/bin/env python

from alchemyapi_python.alchemyapi import AlchemyAPI
from alchemyapi_python.alchemyapi import BadApiKeyError
from argparse import ArgumentParser
from alchemy_analyzer import *
from utils import query_yes_no
import sys

def get_args():
    parser = ArgumentParser()
    parser.add_argument('key', help='The AlchemyAPI key')
    parser.add_argument('source', help='The path to the source directory')
    parser.add_argument('destination', help='The path to the destination directory. '
        + "Directories will be created if they don't exist")
    parser.add_argument('-r', '--recursive', help='Recursively process subdirectories',
        action='store_true')

    return parser.parse_args()

def transaction_limit_callback(file_analyzer):
    retry = query_yes_no('Daily transaction limit reached. Retry with a different key?')
    if retry:
        key = raw_input('Please enter the new key: ')
        try:
            file_analyzer.api = AlchemyAPI(api_key=key)
            return True
        except BadApiKeyError as e:
            sys.stderr.write('The API key is not in proper format. Cause: ' + str(e))
            exit(-1)
    else:
        return False

def main():
    args = get_args()
    try:
        api = AlchemyAPI(api_key=args.key)
        file_analyzer = AlchemyFileAnalyzer(api, transaction_limit_callback)
    except BadApiKeyError as e:
        sys.stderr.write('The API key is not in proper format. Cause: ' + str(e))
        exit(-1)

    try:
        AlchemyDirectoryAnalyzer(file_analyzer=file_analyzer,
                                source=args.source,
                                destination=args.destination,
                                recursive=args.recursive).run()
    except AlchemyAPIError as e:
        sys.stderr.write(str(e) + '\n')
        exit(-1)

if __name__ == '__main__':
    main()