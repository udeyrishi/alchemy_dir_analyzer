#!/usr/bin/env python

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


from alchemyapi_python.alchemyapi import AlchemyAPI
from alchemyapi_python.alchemyapi import BadApiKeyError
from argparse import ArgumentParser
from alchemy_analyzer import *
from utils import query_yes_no
import sys
import logging

def get_args():
    parser = ArgumentParser()
    parser.add_argument('key', help='The AlchemyAPI key')
    parser.add_argument('source', help='The path to the source directory')
    parser.add_argument('destination', help='The path to the destination directory. '
        + "Directories will be created if they don't exist")
    parser.add_argument('-r', '--recursive', help='Recursively process subdirectories',
        action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable verbose log output',
        action='store_true')

    return parser.parse_args()

def transaction_limit_callback(file_analyzer, logger):
    retry = query_yes_no('Daily transaction limit reached. Retry with a different key?')
    if retry:
        key = raw_input('Please enter the new key: ')
        try:
            file_analyzer.api = AlchemyAPI(api_key=key)
            return True
        except BadApiKeyError as e:
            logger.critical('The API key is not in proper format. Cause: ' + str(e))
            exit(-1)
    else:
        return False

def get_logger(verbose_enabled):
    logger = logging.getLogger('alchemy_dir_analyzer')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if verbose_enabled:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger

def main():
    args = get_args()
    logger = get_logger(args.verbose)
    try:
        api = AlchemyAPI(api_key=args.key)
        file_analyzer = AlchemyFileAnalyzer(api,
            lambda file_analyzer: transaction_limit_callback(file_analyzer, logger))
    except BadApiKeyError as e:
        logger.critical('The API key is not in proper format. Cause: ' + str(e))
        exit(-1)

    try:
        logger.info('Starting analysis')
        AlchemyDirectoryAnalyzer(file_analyzer=file_analyzer,
                                source=args.source,
                                destination=args.destination,
                                recursive=args.recursive,
                                logger=logger).run()
        logger.info('Analysis finished. Results in ' + args.destination)
    except AlchemyAPIError as e:
        logger.critical(str(e))
        exit(-1)

if __name__ == '__main__':
    main()