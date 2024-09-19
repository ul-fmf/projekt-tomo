"""
Export to Putka
"""

import expurtka.export
import expurtka.export.courses
import expurtka.export.problems
import expurtka.export.users
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """Recrerates the database with Putka models"""

    def handle(self, *args, **options):
        self.stdout.write("Recreating the current database in Putka format...")

        users_map = expurtka.export.users.please()
        institution_map, course_map, problemset_map = expurtka.export.courses.please(
            users_map
        )
        expurtka.export.problems.please(problemset_map)

        self.stdout.write("Done!")
