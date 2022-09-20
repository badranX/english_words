import json
import sys
from dataclasses import dataclass
import pandas as pd


def oneline(line):
    d = json.loads(line)

    word = d['word']
    pos = d['pos']
    tags = set()
    form_of = None

    isskip = False
    counter = 0
    o = 0
    for sense in d.get('senses', []):
        counter += 1
        if 'obsolete' in sense.get('tags', []):
            o += 1
        form_of = sense.get('form_of', [{}])
    if counter and counter == o:
        return False
    return True


def read(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            skip = oneline(line)


if __name__ == '__main__':
    read(sys.argv[1])
