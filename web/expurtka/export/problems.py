from django.db.utils import IntegrityError
import expurtka.putka as putka
import problems.models as tomo


def export_problems(problemset_map: dict[str, putka.Set]):
    putka.Task.objects.all().delete()
    putka.Content.objects.all().delete()
    placeholder_user = putka.User(
        id=0,
        username="expurtka_bot",
        first_name="Export",
        last_name="to Putka",
        email="",
        is_staff=True,
        is_active=True,
    )
    placeholder_user.save()
    problems_map = {}
    parents_map = {}
    for problem in tomo.Problem.objects.all():
        new_task = putka.Task(
            id=problem.id,  # TODO this no good
            url=(problem.title + str(problem.id))
            .lower()
            .replace(" ", "_"),  # TODO ouch
            evaluation_type=putka.TASK_EVALUATION_TYPES.server_evaluation,
        )
        parents_map[new_task.id] = problemset_map[problem.problem_set.id]
        # new_task.parents.add(problemset_map[problem.problem_set.id])
        new_task.save()

        # try:
        #     new_task.save()
        # except IntegrityError:
        #     new_task = putka.Task.objects.get(id=problem.id)
        new_content = putka.Content(
            base_object=new_task,
            lang="sl",
            title=problem.title,
            content=problem.description,
        )
        new_content.save(editor=placeholder_user)
        new_task.content_queryset.add(new_content)
        problems_map[problem.id] = (new_task, new_content)
    return problems_map
    # TODO title -> Content.title
    # TODO description -> Content.content


def export_parts(problems_map: dict[str, tuple[putka.Task, putka.Content]]):
    placeholder_user = putka.User.objects.get(id=0)
    PARTS_SEPARATOR_TOKEN = "\n\n\{\{\{ PART BREAK \}\}\}\n\n"
    for part in tomo.Part.objects.all():
        # TODO: improve this apend
        content = problems_map[part.problem.id][1]
        content.content = content.content + PARTS_SEPARATOR_TOKEN + part.description
        content.save(editor = placeholder_user)

        # TODO: template, solution, validation, secret fields


def please(problemset_map: dict[str, putka.Set]):
    problems_map = export_problems(problemset_map)
    export_parts(problems_map)
