import json

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
    for i, problem in enumerate(tomo.Problem.objects.all()):
        # Turn Problem into Task
        new_task = putka.Task.objects.create(
            id=problem.id,  # TODO this no good
            url=(problem.title + "_" + str(problem.id))
            .lower()
            .replace(" ", "_"),  # TODO ouch
            evaluation_type=putka.TASK_EVALUATION_TYPES.local_evaluation,
            testscript="",
        )

        # Add parent to Task
        putka.TaskLink.objects.create(
            parent=problemset_map[problem.problem_set.id],
            task=new_task,
            sort=i,
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
        new_upload = putka.Upload.objects.create(
            user=placeholder_user,
            lang=putka.PROG_LANGS_.py3,
            filename=new_task.url + ".py",
            source="".encode(),
            status=putka.UPLOAD_STATUS.done,
            agg_status=putka.JAILRUN_STATUS.OK,
            preparation_status=putka.JAILRUN_STATUS.OK,
            task=new_task,
            points=0,
            max_points=0,
            is_official_solution=True,
        )

        # Create template file
        template_file = putka.File.objects.create(
            task=new_task,
            filename=new_task.url + "_template.py",
            type=putka.ATT_TYPE.generic_public,
            data="".encode(),
        )

        # Update dictionary
        problems_map[problem.id] = {
            "task": new_task,
            "content": new_content,
            "solution": new_upload,
            "template_file": template_file,
            "num_parts": -1,
        }
    return problems_map


def export_parts(
    problems_map: dict[str, dict[str, putka.Task | putka.Content | putka.Upload]]
):
    placeholder_user = putka.User.objects.get(id=0)
    PARTS_SEPARATOR_TOKEN = "\n\n{{{ PART BREAK }}}\n\n"
    SCRIPT_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"
    SOLUTION_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"
    TEMPLATE_SEPARATOR_TOKEN = "\n\n\n\n\n"
    for part in tomo.Part.objects.all():
        # TODO: improve this apend
        content = problems_map[part.problem.id]["content"]
        content.content = content.content + PARTS_SEPARATOR_TOKEN + part.description
        content.save(editor=placeholder_user)

        task = problems_map[part.problem.id]["task"]
        if task.testscript:
            task.testscript += SCRIPT_SEPARATOR_TOKEN
        task.testscript += part.validation

        i = problems_map[part.problem.id]["num_parts"] + 1
        problems_map[part.problem.id]["num_parts"] = i

        secret = json.loads(part.secret)
        if secret:
            for j, example in enumerate(secret):
                putka.File.objects.create(
                    task=task,
                    filename=f"secret.{i:02d}.{j:02d}.out",
                    data=str(example).encode(),
                    type=putka.ATT_TYPE.inout_secret,
                )

        # Update template
        template_file = problems_map[part.problem.id]["template_file"]
        task_template = template_file.data.decode()
        if task_template:
            task_template += TEMPLATE_SEPARATOR_TOKEN
        task_template += part.template
        template_file.data = task_template.encode()
        template_file.save()

        putka.File.objects.create(
            task=task,
            filename=task.url + f"_template_{i}.py",
            type=putka.ATT_TYPE.generic_public,
            data=part.template.encode(),
        )

        # Update official solution
        official_solution = problems_map[part.problem.id]["solution"]
        # if part.problem.id == 363:
        #     print(official_solution)
        task_solution = official_solution.source.decode()
        if task_solution:
            task_solution += SOLUTION_SEPARATOR_TOKEN
        task_solution += part.solution
        official_solution.source = task_solution.encode()
        official_solution.max_points = i
        official_solution.points = i
        official_solution.save()
        task.save()
        # TODO: template, solution, secret fields


def please(problemset_map: dict[str, putka.Set]):
    problems_map = export_problems(problemset_map)
    export_parts(problems_map)
