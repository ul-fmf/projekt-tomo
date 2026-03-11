"""
Export to Putka
"""

import json

from django.core.management import BaseCommand
from expurtkapp.export import courses, problems, users


class Command(BaseCommand):
    help = """JSON dumps the tomo models for putka import"""

    def handle(self, *args, **options):
        self.stdout.write("Creating dict to dump...")

        obj = {}
        obj["users"] = users.export_all()

        obj["institutions"], obj["courses"], obj["problem_sets"] = courses.export_all()

        (
            obj["tasks"],
            obj["contents"],
            obj["files"],
            obj["uploads"],
        ) = problems.export_all()

        self.stdout.write("Dumping JSON...")

        with open(options["outfile"], "w") as f:
            json.dump(obj, f, indent=4)

        self.stdout.write("Done!")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("outfile", help="The path to which to export the JSON to")
