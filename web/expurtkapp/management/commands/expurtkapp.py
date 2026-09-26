"""
Export to Putka
"""

import json

import courses.models as tomo_courses
import users.models as tomo_users
from django.core.management import BaseCommand, CommandError
from expurtkapp.export import courses, problems, users


class Command(BaseCommand):
    help = """JSON dumps the tomo models for putka import"""

    def handle(self, *args, **options):
        course_ids = options["course"]
        include_attempts = not options["no_attempts"]

        if course_ids:
            selected_courses = tomo_courses.Course.objects.filter(pk__in=course_ids)
            missing = set(course_ids) - set(
                selected_courses.values_list("pk", flat=True)
            )
            if missing:
                raise CommandError(
                    f"No course with id {', '.join(map(str, sorted(missing)))}"
                )
            selected_users = users.course_users(selected_courses, include_attempts)
        else:
            selected_courses = tomo_courses.Course.objects.all()
            selected_users = tomo_users.User.objects.all()

        self.stdout.write("Creating dict to dump...")

        obj = {}
        obj["users"] = users.export_all(selected_users)

        obj["institutions"], obj["courses"], obj["problem_sets"] = courses.export_all(
            selected_courses
        )

        (
            obj["tasks"],
            obj["contents"],
            obj["files"],
            obj["uploads"],
        ) = problems.export_all(selected_courses, include_attempts)

        self.stdout.write("Dumping JSON...")

        with open(options["outfile"], "w") as f:
            json.dump(obj, f, indent=4)

        self.stdout.write("Done!")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("outfile", help="The path to which to export the JSON to")
        parser.add_argument(
            "--course",
            type=int,
            action="append",
            help="Export only the course with this id (can be given several times)",
        )
        parser.add_argument(
            "--no-attempts",
            action="store_true",
            help="Do not export student attempts (official solutions are still exported)",
        )
