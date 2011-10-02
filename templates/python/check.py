from hashlib import md5
import inspect, json, os, re, random, sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

class Check:
    @staticmethod
    def initialize(parts):
        Check.parts = parts
        Check.current = None
        Check.part_id = None

    @staticmethod
    def part():
        if Check.part_id is None:
            Check.part_id = 0
        else:
            Check.part_id += 1
        Check.current = Check.parts[Check.part_id]
        return Check.current.get('solution', '') != ''

    @staticmethod
    def error(msg):
        if 'errors' not in Check.current:
            Check.current['errors'] = []
        Check.current['errors'].append(msg)

    @staticmethod
    def challenge(x):
        if 'challenge' not in Check.current:
            Check.current['challenge'] = ''
        Check.current['challenge'] += str(x)

    @staticmethod
    def equal(example, expected, message=None, clean=lambda x: x):
        if not message:
            message = 'Ukaz {0} vrne {1!r} namesto {2!r}.'
        answer = eval(example)
        if clean(answer) != clean(expected):
            Check.error(message.format(example, answer, expected))

    @staticmethod
    def num_equal(example, expected, digits=6):
        Check.equal(example, expected, clean=lambda x: round(x, digits))


    @staticmethod
    def summarize():
        for i, part in enumerate(Check.parts):
            print('Naloga {0}) je'.format(i + 1), end=' ')
            if not part['solution']:
                print('brez rešitve.'.format(i + 1))
            elif 'errors' in part:
                print('napačno rešena.'.format(i + 1))
                print('- {0}'.format("\n- ".join(part['errors'])))
            else:
                print('pravilno rešena.')

    @staticmethod
    def dump():
        return json.dumps(Check.parts)

