import json

import problems.models as tomo

# Putka integer choices (from putka Task model)
EVALUATION_TYPE_LOCAL = 2

# Putka PROG_LANGS choices
LANG_PY3 = 8

# Putka UPLOAD_STATUS choices
UPLOAD_STATUS_DONE = 3

# Putka JAILRUN_STATUS choices
JAILRUN_STATUS_OK = 1

# Putka ATT_TYPE choices
ATT_TYPE_INOUT_SECRET = -2
ATT_TYPE_GENERIC_PUBLIC = 4

PARTS_SEPARATOR_TOKEN = "\n\n{{{ PART BREAK }}}\n\n"
SCRIPT_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"
SOLUTION_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"
TEMPLATE_SEPARATOR_TOKEN = "\n\n\n\n\n"


def export_problems():
    placeholder_user = {
        "id": 0,
        "username": "expurtka_bot",
        "first_name": "Export",
        "last_name": "to Putka",
        "email": "",
        "is_staff": True,
        "is_active": True,
    }

    tasks = []
    contents = []
    files = []

    for i, problem in enumerate(
        tomo.Problem.objects.all()
        .prefetch_related("parts")
        .prefetch_related("parts__attempts")
    ):
        parts = problem.parts.all()
        url = (problem.title + "_" + str(problem.id)).lower().replace(" ", "_")
        task = {
            "id": problem.id,
            "url": url,
            "parent": problem.problem_set.id,
            "testscript": PARTS_SEPARATOR_TOKEN.join(
                [part.validation for part in parts]
            ),
        }
        # Turn description and title into separate Content object
        content = {
            "task": task["id"],
            "lang": "sl",
            "title": problem.title,
            "content": problem.description,
            "version": 1,
        }

        # for part in parts:
        #     print(part)
        # print(list(part.attempts.all()))

        # # Create official upload
        # new_upload = {
        #     "user": placeholder_user,
        #     "lang": LANG_PY3,
        #     "filename": url + ".py",
        #     "source": "",
        #     "upload_time": None,
        #     "status": UPLOAD_STATUS_DONE,
        #     "agg_status": JAILRUN_STATUS_OK,
        #     "preparation_status": JAILRUN_STATUS_OK,
        #     "task": new_task,
        #     "points": 0,
        #     "max_points": 0,
        #     "is_official_solution": True,
        # }

        # Create template file
        file = {
            "task": task["id"],
            "filename": url + "_template.py",
            "type": ATT_TYPE_GENERIC_PUBLIC,
            "data": PARTS_SEPARATOR_TOKEN.join([part.description for part in parts]),
        }

        tasks.append(task)
        contents.append(content)
        files.append(file)

        # # Update dictionary
        # problems[problem.id] = {
        #     "task": new_task,
        #     "task_link": task_link,
        #     "content": new_content,
        #     "solution": new_upload,
        #     "template_file": template_file,
        #     "files": [],
        #     "num_parts": -1,
        # }
    return tasks, contents, files


def export_parts(problems):
    for part in tomo.Part.objects.all():
        # TODO: improve this apend
        content = problems[part.problem.id]["content"]
        content["content"] = (
            content["content"] + PARTS_SEPARATOR_TOKEN + part.description
        )

        task = problems[part.problem.id]["task"]
        if task["testscript"]:
            task["testscript"] += SCRIPT_SEPARATOR_TOKEN
        task["testscript"] += part.validation

        i = problems[part.problem.id]["num_parts"] + 1
        problems[part.problem.id]["num_parts"] = i

        secret = json.loads(part.secret)
        if secret:
            for j, example in enumerate(secret):
                problems[part.problem.id]["files"].append(
                    {
                        "task": task,
                        "filename": f"secret.{i:02d}.{j:02d}.out",
                        "data": str(example),
                        "type": ATT_TYPE_INOUT_SECRET,
                    }
                )

        # Update template
        template_file = problems[part.problem.id]["template_file"]
        task_template = template_file["data"]
        if task_template:
            task_template += TEMPLATE_SEPARATOR_TOKEN
        task_template += part.template
        template_file["data"] = task_template

        problems[part.problem.id]["files"].append(
            {
                "task": task,
                "filename": task["url"] + f"_template_{i}.py",
                "type": ATT_TYPE_GENERIC_PUBLIC,
                "data": part.template,
            }
        )

        # Update official solution
        official_solution = problems[part.problem.id]["solution"]
        task_solution = official_solution["source"]
        if task_solution:
            task_solution += SOLUTION_SEPARATOR_TOKEN
        task_solution += part.solution
        official_solution["source"] = task_solution
        official_solution["max_points"] = i
        official_solution["points"] = i

    return problems


def export_all():
    return export_problems()
    # return export_parts(problems)
