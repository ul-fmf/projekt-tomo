import expurtka.putka as putka
import problems.models as tomo


def export_problems(problemset_map: dict[str, putka.Set]):
    for problem in tomo.Problem.objects.all():
        new = putka.Task(
            title=problem.title,
            description=problem.description,
            parents=problemset_map[problem.problem_set.id],
        )
    # TODO export ProblemSet first


def export_parts():
    pass


def please(problemset_map: dict[str, putka.Set]):
    export_problems(problemset_map)
    export_parts()
