##Alchemy Directory Analyzer
A text analysis app that uses [Alchemy API](https://github.com/udeyrishi/alchemyapi_python/) to analyze all the plain text documents in a directory.


###Dependencies
This project has been built and tested using Python 2.7.11. Get all the required packages as follows:

```sh
# Install all pip requirements
$ pip install -r requirements.txt

# Install Python Alchemy API (submodule)
$ git submodule init && git submodule update
```

###Usage
```
$ chmod +x ./main.py

$ ./main.py -h
usage: main.py [-h] [-r] [-v] key source destination

positional arguments:
  key              The AlchemyAPI key
  source           The path to the source directory
  destination      The path to the destination directory. Directories will be
                   created if they don't exist

optional arguments:
  -h, --help       show this help message and exit
  -r, --recursive  Recursively process subdirectories
  -v, --verbose    Enable verbose log output
```

Example usage:

```
$ ./main.py -rv 1234567890098765432112345678900987654321 path/to/src path/to/dest
2016-04-16 22:49:14,009 alchemy_dir_analyzer INFO     Starting analysis
2016-04-16 22:49:14,009 alchemy_dir_analyzer DEBUG    Processing file: path/to/src/f1.txt >> Output file: path/to/dest/f1.txt.json
...
2016-04-16 22:49:18,528 alchemy_dir_analyzer INFO     Analysis finished. Results in path/to/dest
```

Note that all the files in the source directory (and subdirectories, if ```-r``` is used) starting with a ```'.'``` will be skipped (system files on Linux and OS X).

###Output
The destination directory has the same structure as the source directory, except that all the file names have '.json' appended, and they contain the corresponding Alchemy API analysis information as a JSON object. All the fields in this JSON have the same meaning as specified in the [Alchemy API documentation](http://www.alchemyapi.com/api). Some unimportant fields such as ```'url'```, ```'usage'```, ```'status'```, ```'statusInfo'```, ```'totalTransactions'```, etc., have been removed from the API results.

Sample result JSON:

```js
{
    "category": {
        "category": "arts_entertainment",
        "language": "english",
        "score": "0.85"
    },
    "concepts": {
        "concepts": [
            {
                "dbpedia": "http://dbpedia.org/resource/Film",
                "freebase": "http://rdf.freebase.com/ns/m.02vxn",
                "opencyc": "http://sw.opencyc.org/concept/Mx4rwP19XJwpEbGdrcN5Y29ycA",
                "relevance": "0.962047",
                "text": "Film"
            },
            ...
        ],
        "language": "english"
    },
    "doc_sentiment": {
        "docSentiment": {
            "mixed": "1",
            "score": "-0.314192",
            "type": "negative"
        },
        "language": "english"
    },
    "entities": {
        "entities": [
            {
                "count": "2",
                "disambiguated": {
                    "dbpedia": "http://dbpedia.org/resource/Melissa_Sagemiller",
                    "freebase": "http://rdf.freebase.com/ns/m.0b6z88",
                    "name": "Melissa Sagemiller",
                    "subType": [
                        "Actor",
                        "FilmActor",
                        "TVActor"
                    ],
                    "yago": "http://yago-knowledge.org/resource/Melissa_Sagemiller"
                },
                "relevance": "0.737991",
                "sentiment": {
                    "score": "-0.714528",
                    "type": "negative"
                },
                "text": "melissa sagemiller",
                "type": "Person"
            },
            {
                "count": "1",
                "relevance": "0.584015",
                "sentiment": {
                    "score": "0.357154",
                    "type": "positive"
                },
                "text": "the deal",
                "type": "FieldTerminology"
            },
            ...
        ],
        "language": "english"
    },
    "keywords": {
        "keywords": [
            {
                "relevance": "0.943157",
                "sentiment": {
                    "score": "0.310866",
                    "type": "positive"
                },
                "text": "pretty neat concept"
            },
            ...
        ],
        "language": "english"
    }
}
```