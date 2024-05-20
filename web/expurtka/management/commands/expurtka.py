"""
Export to Putka
"""

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """Recrerates the database with Putka models"""

    def handle(self, *args, **options):
        self.stdout.write("Recreating the current database in Putka format...")

        # expurtka.core.migrate_institutions()

        self.stdout.write("Done!")
