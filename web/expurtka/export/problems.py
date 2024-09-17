from django.db.utils import IntegrityError
import expurtka.putka as putka
import problems.models as tomo


def export_problems(
    problemset_map: dict[str, putka.Set]
) -> dict[str, dict[str, putka.Task | putka.Content | putka.Upload]]:
    putka.Task.objects.all().delete()
    putka.TaskLink.objects.all().delete()
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
    for problem in tomo.Problem.objects.all():
        # Turn Problem into Task
        new_task = putka.Task.objects.create(
            id=problem.id,  # TODO this no good
            url=(problem.title + "_" + str(problem.id))
            .lower()
            .replace(" ", "_"),  # TODO ouch
            evaluation_type=putka.TASK_EVALUATION_TYPES.local_evaluation,
            testscript="",
            solution="",
            secret="",
        )

        # Add parent to Task
        putka.TaskLink.objects.create(
            parent=problemset_map[problem.problem_set.id],
            task=new_task,
            sort=1,
        )

        # Turn description and title into separate Content object
        new_content = putka.Content(
            base_object=new_task,
            lang="sl",
            title=problem.title,
            content=problem.description,
        )
        new_content.save(editor=placeholder_user)
        # Link it to task
        new_task.content_queryset.add(new_content)

        # Create official upload
        new_upload = putka.Upload(
            task=new_task,
            max_points=0,
            is_official_solution=True,
        )

        # Update dictionary
        problems_map[problem.id] = {
            "task": new_task,
            "content": new_content,
            "solution": new_upload,
        }
    return problems_map


def export_parts(
    problems_map: dict[str, dict[str, putka.Task | putka.Content | putka.Upload]]
):
    placeholder_user = putka.User.objects.get(id=0)
    PARTS_SEPARATOR_TOKEN = "\n\n\{\{\{ PART BREAK \}\}\}\n\n"
    SCRIPT_SEPARATOR_TOKEN = "\n\n# \{\{\{ PART BREAK \}\}\}\n\n"
    SOLUTION_SEPARATOR_TOKEN = "\n\n# \{\{\{ PART BREAK \}\}\}\n\n"
    SECRET_SEPARATOR_TOKEN = "\n"
    for part in tomo.Part.objects.all():
        # TODO: improve this apend
        content = problems_map[part.problem.id]["content"]
        content.content = content.content + PARTS_SEPARATOR_TOKEN + part.description
        content.save(editor=placeholder_user)

        task = problems_map[part.problem.id]["task"]
        if task.testscript:
            task.testscript += SCRIPT_SEPARATOR_TOKEN
        task.testscript +=  part.validation
        if task.solution:
            task.solution += SOLUTION_SEPARATOR_TOKEN  
        task.solution += part.solution
        if task.secret:
            task.secret += SECRET_SEPARATOR_TOKEN
        task.secret += part.secret
        task.save()
        # TODO: template, solution, secret fields


def please(problemset_map: dict[str, putka.Set]):
    problems_map = export_problems(problemset_map)
    export_parts(problems_map)
