"""
Export to Putka
"""

import json

from django.core.management import BaseCommand
from expurtkapp.export import problems


class Command(BaseCommand):
    help = """JSON dumps the tomo models for putka import"""

    def handle(self, *args, **options):
        self.stdout.write("creating dict to dump...")

        obj = {}
        obj['tasks'] = problems.get_problems()

        self.stdout.write("dumping JSON...")

        with open(options['outfile'], 'w') as f:
            json.dump(obj, f)

        self.stdout.write("Done!")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('outfile', help="The path to which to export the JSON to")
