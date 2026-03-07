import argparse
import os

from . import run

DEFAULT_CONFIG_FILE = os.path.join(os.path.split(__file__)[0], 'config.json')

class PathAction(argparse.Action):

    def __call__(self, parser, namespace, path, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(path))
            
parser = argparse.ArgumentParser(description='ICU')

parser.add_argument('--config', '-c', metavar='C', action=PathAction, type=str, 
        default= DEFAULT_CONFIG_FILE,
        help='path of the config file to use.')

args = parser.parse_args()
run(**args.__dict__)