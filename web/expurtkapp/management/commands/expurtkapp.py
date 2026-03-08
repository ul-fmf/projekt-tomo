"""
Export to Putka
"""

import json

from django.core.management import BaseCommand
from expurtkapp.export import attempts, courses, problems, users


class Command(BaseCommand):
    help = """JSON dumps the tomo models for putka import"""

    def handle(self, *args, **options):
        self.stdout.write("creating dict to dump...")

        obj = {}
        obj["users"] = users.export_all()

        obj["institutions"], obj["courses"], obj["problem_sets"] = courses.export_all()

        tasks, contents, files = problems.export_all()
        obj["tasks"] = tasks
        obj["contents"] = contents
        obj["files"] = files
        # obj["official_uploads"] = official_uploads

        obj["attempts"] = attempts.export_all(tasks)

        self.stdout.write("dumping JSON...")

        with open(options["outfile"], "w") as f:
            json.dump(obj, f, indent=4)

        self.stdout.write("Done!")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("outfile", help="The path to which to export the JSON to")
