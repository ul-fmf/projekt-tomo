"""
Export to Putka
"""

import expurtka.export.courses as courses
import expurtka.export.problems as problems
import expurtka.export.users as users
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """Recrerates the database with Putka models"""

    def handle(self, *args, **options):
        self.stdout.write("Recreating the current database in Putka format...")

        _users = users.please()
        _institutions, _courses, _problem_sets = courses.please(_users)
        _problems = problems.please(_problem_sets)

        self.stdout.write("Done!")
