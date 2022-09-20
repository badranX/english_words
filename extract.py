import json
import sys
from dataclasses import dataclass
import pandas as pd

bad_tags = ["archaic",  "obsolete" ]
bad_pos = set(['name', 'symbol', 'prefix', 'suffix', 'character'])

verb_tense = ['past', 'present']
#verb_extra = ['simple', 'participle', 'perfect']
verb_extra = []
TAGS = set(verb_tense + verb_extra)

class Word():
    def __init__(self, word, pos, form_of, tags):
        self.word = word
        self.pos = pos
        self.tags = tags
        self.form_of = form_of

    def get_dict(self, tags):
        ret = {'word': [self.word], 
        'pos': [self.pos], 
        'form_of': [self.form_of]}
        for tag in tags:
            ret[tag] = [True] if tag in self.tags else [False]



@dataclass
class AllWords:
    """Class for keeping track of an item in inventory."""
    words = {}



def oneline(line, tmp):
    d = json.loads(line)

    word = d['word']
    if len(word.split()) > 1:
        return None
    pos = d['pos']
    tags = set()
    form_of = None

    count = 0
    obs_count = 0
    for sense in d.get('senses', []):
        count += 1
        form_of = sense.get('form_of', [{}])[0]
        form_of = form_of.get('word')
        if form_of:
            tags = sense.get('tags', [])
            tags = TAGS.intersection(tags)

        for bad_tag in bad_tags:
            if bad_tag in sense.get('tags', []):
                obs_count += 1
                break

    if count and count == obs_count:
        return None

    return Word(word, pos, form_of, tags)


def read(file_path, freq_path):
    data = AllWords()
    ALL_POSES = set()
    with open(file_path, 'r') as f:
        for line in f:
            w = oneline(line, data)
            if w:
                data.words[w.word] = data.words.get(w.word, [])
                data.words[w.word].append(w.pos)
                ALL_POSES.add(w.pos.lower())
                #if len(data.words) > 10000:
                #    break 

    df = pd.read_csv(freq_path)
    #TODO insure feqs are low letter
    freqs = dict(zip(df['word'], df['count']))
    head = None

    data.words = {k.lower(): v for k, v in data.words.items() if k.lower() in freqs}
    data.words = {k: data.words[k] for k in sorted(data.words.keys(), reverse=True, key=lambda k: freqs[k.lower()])}

    with open('out.csv', 'w') as f, open('human.txt', 'w') as hf:
        for word, poses in data.words.items():
            if set(poses) - bad_pos:
                pass
            else:
                continue

            if not head:
                x = ','.join(ALL_POSES)
                x = 'count,' + x
                x = 'word,' + x
                f.write(x + '\n')
                head = x
            if word.lower() not in freqs:
                continue
            x = ','.join(['1' if x in poses else '0' for x in ALL_POSES])
            x = str(freqs[word.lower()]) + ',' + x
            x = word + ',' + x
            f.write(x + '\n')
            hf.write(word + ': ' + str(poses) + '\n')

if __name__ == '__main__':
    read(sys.argv[1], sys.argv[2])
