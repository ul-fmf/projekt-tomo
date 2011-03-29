from hashlib import md5
import os, re, random, sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

def _split_file(filename):
    with open(filename) as f:
        source = f.read()

    part_regex = re.compile(
        r'(#{50,}@(\d+)#' # beginning of header
        r'.*?Naloga (.+?)\)' # part label
        r'.*?#{50,}\2@#)' # end of header
        r'(.*?)(?=#{50,}@)', # body
        flags=re.DOTALL|re.MULTILINE
    )
    def part(part_match):
        start = part_match.start() + len(part_match.group(1))
        end = part_match.end()
        return {
            'id': int(part_match.group(2)),
            'label': part_match.group(3),
            'start': start,
            'end': end,
            'solution': part_match.group(0),
            'attempted': bool(source[start:end].strip())
        }

    parts = [part(part_match) for part_match in part_regex.finditer(source)]
    
    return source, parts

def _equal(example, expected):
    global _warn
    answer = eval(example)
    if answer != expected:
        _warn('Ukaz {0} vrne {1!r} namesto {2!r}.'.format(example, answer, expected))

def check_function(name, argsnum):
    """ Preveri, če je metoda name definirana in sprejme argsnum argumentov."""  
    if name not in globals():
        _warn("Funkcija {0} ni definirana.".format(name))
        return False
    func = eval(name)
    if argsnum != -1 and len(inspect.getargspec(func)[0]) != argsnum:
        _warn("Funkcija {2} mora namesto {0} sprejeti {1} argumentov.".format(len(inspect.getargspec(func)[0]), argsnum, name))
        return False
  return True

def _run_trial(trial, solution):
    global _warn
    errors = []
    h = md5()
    _warn = lambda msg: errors.append(msg)
    for x in trial(solution):
        h.update(str(x).encode('utf-8'))
    return h.hexdigest(), errors
    

def _submit_solutions(parts, source, username, signature, download_ip):
    data = {
        'username': username,
        'signature': signature,
        'download_ip': download_ip,
        'source': source
    }
    for part in parts:
        label = part['label']
        if not part['attempted']:
            print('Naloga {0}) je brez rešitve.'.format(label))
        else:
            part_id = part['id'] if part['id'] else -i
            data['{0}_label'.format(part_id)] = part['label']
            data['{0}_start'.format(part_id)] = part['start']
            data['{0}_end'.format(part_id)] = part['end']
            random.seed(username)
            secret, errors = _run_trial(part['trial'], part['solution'])
            if errors:
                print('Naloga {0}) je napačno rešena:'.format(label))
                print('- ' + '\n- '.join(errors))
            else:
                print('Naloga {0}) je pravilno rešena.'.format(label))
                data['{0}_secret'.format(part_id)] = secret
    print('Shranjujem rešitve...')
    post = urlencode(data)
    try:
        r = urlopen('http://{{ request.META.HTTP_HOST }}{% url upload_solution problem.id %}', post)
        contents = r.read()
    except HTTPError as error:
        contents = error.read()
    print(contents.decode())
