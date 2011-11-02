import json

class Check:
    @staticmethod
    def initialize(parts):
        Check.parts = parts
        Check.current = None
        Check.part_counter = None

    @staticmethod
    def part():
        if Check.part_counter is None:
            Check.part_counter = 0
        else:
            Check.part_counter += 1
        Check.current = Check.parts[Check.part_counter]
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
    def run(example, state, message=None, env={}, clean=lambda x: x):
        s = {}
        s.update(env)
        exec (example, globals(), s)
        for (x,v) in state.items():
            if x not in s:
                Check.error('Ukazi\n{0}\nne nestavijo spremenljivke {1}, a bi jo morali.'.format(example, x))
            elif clean(s[x]) != clean(v):
                Check.error('Ukazi\n{0}\nbi morali nastaviti spremenljivko {1} na {2},\na jo nastavijo na {3}'.format(example, x, v, s[x]))

    @staticmethod
    def equal(example, expected, message=None, clean=lambda x: x, env={}):
        if not message:
            message = 'Ukaz {0} vrne {1!r} namesto {2!r}.'
        local = locals()
        local.update(env)
        answer = eval(example, globals(), local)
        if clean(answer) != clean(expected):
            Check.error(message.format(example, answer, expected))

    @staticmethod
    def num_equal(example, expected, digits=6):
        Check.equal(example, expected, clean=lambda x: round(x, digits))

    @staticmethod
    def summarize():
        for i, part in enumerate(Check.parts):
            if not part['solution']:
                print('Naloga {0} je brez rešitve.'.format(i + 1))
            elif 'errors' in part:
                print('Naloga {0} je napačno rešena.'.format(i + 1))
                print('- {0}'.format("\n- ".join(part['errors'])))
            else:
                print('Naloga {0} je pravilno rešena.'.format(i + 1))

    @staticmethod
    def dump():
        return json.dumps(Check.parts)

