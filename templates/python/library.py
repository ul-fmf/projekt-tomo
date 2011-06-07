from hashlib import md5
import inspect, os, re, random, sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

def _equal(example, expected, message=None):
    global _warn
    if not message:
        message = 'Ukaz {0} vrne {1!r} namesto {2!r}.'
    answer = eval(example)
    if answer != expected:
        _warn(message.format(example, answer, expected))


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
