import json
from datetime import datetime, timezone

from attempts.models import Attempt
from courses.models import Course


class Course(Course):
    class Meta:
        proxy = True

    def statistika(self):
        students = self.student_success()
        problem_sets = self.problem_sets.all().prefetch_related(
            "problems",
            "problems__parts",
            "problems__parts__attempts",
            "problems__parts__attempts__user",
        )

        my_students = {student: 0 for student in students}

        number_of_problems = 0
        number_of_problem_parts = 0
        for problem_set in problem_sets:
            problems = problem_set.problems.all()
            number_of_problems += len(problems)
            for problem in problems:
                parts = problem.parts.all()
                number_of_problem_parts += len(parts)
                for part in parts:
                    for attempt in part.attempts.all():
                        if attempt.user in my_students:
                            if attempt.valid:
                                my_students[attempt.user] += 1

        my_students = [
            (value, student.last_name, student.first_name)
            for student, value in my_students.items()
        ]
        my_students.sort()

        solved_atleast = [
            ["Stevilo resenih", "Število učencev, ki je rešilo toliko nalog"]
        ]
        solved = 0
        student_index = 0

        while solved <= number_of_problem_parts:
            while (
                student_index < len(my_students)
                and my_students[student_index][0] < solved
            ):
                student_index += 1
            solved_atleast.append((str(solved), len(my_students) - student_index))
            solved += 1

        return {
            "students": students,
            "problem_sets": problem_sets,
            "number_of_problems": number_of_problems,
            "number_of_problem_parts": number_of_problem_parts,
            "my_students": my_students,
            "solved_atleast": solved_atleast,
        }

    def problem_success(self):
        problem_sets = self.problem_sets.all().prefetch_related(
            "problems",
            "problems__parts",
            "problems__parts__attempts",
        )
        annotated_problem_sets = []
        for problem_set in problem_sets:
            problems = problem_set.problems.all()
            problem_set.annotated_problems = []
            for problem in problems:
                problem.annotated_parts = []
                for part in problem.parts.all():
                    part.correct = 0
                    part.wrong = 0
                    for attempt in part.attempts.all():
                        if attempt.valid:
                            part.correct += 1
                        else:
                            part.wrong += 1
                    problem.annotated_parts.append(part)
                problem_set.annotated_problems.append(problem)
                rezultati = [("Pravilnost", "Pravilne rešitve", "Napačne rešitve")]
                for problem in problem_set.annotated_problems:
                    rezultati.append((problem.title, 0, 0))
                    for part in problem.annotated_parts:
                        rezultati.append(("", part.correct, part.wrong))
                problem_set.json = json.dumps(rezultati)
            annotated_problem_sets.append(problem_set)
        return annotated_problem_sets

    def problem_success_2(self):
        """
        Funkcija, ki naredi isto kot problem_success, le da podatke zbere hitreje in
        preko AttemptQuerySeta. Komentar bo popravljen, ko bo funkcija problem_succes
        izbrisana.
        """
        students = self.observed_students()
        attempts = Attempt.objects.filter(user__id__in=students).filter(
            part__problem__problem_set__course__id=self.id
        )
        success = attempts.problem_set_statistics()
        annotated_problem_sets = []
        for problem_set in self.problem_sets.all():
            try:
                rezultati = [("Pravilnost", "Pravilne rešitve", "Napačne rešitve")]
                for problem in success[problem_set]:
                    rezultati.append((problem.title, 0, 0))
                    for part in success[problem_set][problem]:
                        rezultati.append(
                            (
                                "",
                                success[problem_set][problem][part]["valid"],
                                success[problem_set][problem][part]["invalid"],
                            )
                        )
                problem_set.json = json.dumps(rezultati)
                annotated_problem_sets.append(problem_set)
            except Exception:
                pass
        return annotated_problem_sets

    def active(self, days):
        """
        Pripravi nam podatke za risanje grafov. Deluje enako kot funkcija
        problem_success_2, le da nas tokrat zanimajo le učenci, ki so bili
        aktivni v zadnjih DAYS dneh.
        """
        students = self.observed_students()
        active_students = []
        for student in students:
            user_attempts = student.attempts.all().order_by("-submission_date")
            if len(user_attempts) > 0:
                latest = user_attempts[0]
                if (datetime.now(timezone.utc) - latest.submission_date).days <= int(
                    days
                ):
                    active_students.append(student.id)
        attempts = Attempt.objects.filter(user__id__in=active_students).filter(
            part__problem__problem_set__course__id=self.id
        )
        success = attempts.problem_set_statistics()

        # Ta del funkcije se ponavlja skoraj pri vsaki pripravi podatkov, smiselno
        # bi ga bilo spraviti v svojo funkcijo.
        annotated_problem_sets = []
        for problem_set in self.problem_sets.all():
            try:
                rezultati = [("Pravilnost", "Pravilne rešitve", "Napačne rešitve")]
                for problem in success[problem_set]:
                    rezultati.append((problem.title, 0, 0))
                    for part in success[problem_set][problem]:
                        rezultati.append(
                            (
                                "",
                                success[problem_set][problem][part]["valid"],
                                success[problem_set][problem][part]["invalid"],
                            )
                        )
                problem_set.json = json.dumps(rezultati)
                annotated_problem_sets.append(problem_set)
            except Exception:
                pass
        return annotated_problem_sets
