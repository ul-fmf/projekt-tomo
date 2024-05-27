"""
Export to Putka
"""

import expurtka.export
import expurtka.export.courses
import expurtka.export.problems
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """Recrerates the database with Putka models"""

    def handle(self, *args, **options):
        self.stdout.write("Recreating the current database in Putka format...")

        institution_map, course_map, problemset_map = expurtka.export.courses.please()
        expurtka.export.problems.please(problemset_map)

        self.stdout.write("Done!")
