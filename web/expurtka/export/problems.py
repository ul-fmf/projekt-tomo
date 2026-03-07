import json

import problems.models as tomo


def export_problems(problem_sets):
    placeholder_user = {
        "id": 0,
        "username": "expurtka_bot",
        "first_name": "Export",
        "last_name": "to Putka",
        "email": "",
        "is_staff": True,
        "is_active": True,
    }
    problems = []
    for i, problem in enumerate(tomo.Problem.objects.all()):
        url = (problem.title + "_" + str(problem.id)).lower().replace(" ", "_")

        # Turn Problem into Task
        new_task = {
            "id": problem.id,  # TODO this no good
            "url": url,  # TODO ouch
            "evaluation_type": "local_evaluation",
            "testscript": "",
        }

        # Add parent to Task
        task_link = {
            "parent": problem_sets[problem.problem_set.id],
            "task": new_task,
            "sort": i,
        }

        # Turn description and title into separate Content object
        new_content = {
            "base_object": new_task,
            "lang": "sl",
            "title": problem.title,
            "content": problem.description,
        }

        # Create official upload
        new_upload = {
            "user": placeholder_user,
            "lang": "py3",
            "filename": url + ".py",
            "source": "".encode(),
            "status": "done",
            "agg_status": "OK",
            "preparation_status": "OK",
            "task": new_task,
            "points": 0,
            "max_points": 0,
            "is_official_solution": True,
        }

        # Create template file
        template_file = {
            "task": new_task,
            "filename": url + "_template.py",
            "type": "generic_public",
            "data": "".encode(),
        }

        # Update dictionary
        problems.append(
            {
                "task": new_task,
                "task_link": task_link,
                "content": new_content,
                "solution": new_upload,
                "template_file": template_file,
                "files": [],
                "num_parts": -1,
            }
        )
    return problems


def export_parts(problems):
    PARTS_SEPARATOR_TOKEN = "\n\n{{{ PART BREAK }}}\n\n"
    SCRIPT_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"
    SOLUTION_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"
    TEMPLATE_SEPARATOR_TOKEN = "\n\n\n\n\n"
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
                        "data": str(example).encode(),
                        "type": "inout_secret",
                    }
                )

        # Update template
        template_file = problems[part.problem.id]["template_file"]
        task_template = template_file["data"].decode()
        if task_template:
            task_template += TEMPLATE_SEPARATOR_TOKEN
        task_template += part.template
        template_file["data"] = task_template.encode()

        problems[part.problem.id]["files"].append(
            {
                "task": task,
                "filename": task["url"] + f"_template_{i}.py",
                "type": "generic_public",
                "data": part.template.encode(),
            }
        )

        # Update official solution
        official_solution = problems[part.problem.id]["solution"]
        task_solution = official_solution["source"].decode()
        if task_solution:
            task_solution += SOLUTION_SEPARATOR_TOKEN
        task_solution += part.solution
        official_solution["source"] = task_solution.encode()
        official_solution["max_points"] = i
        official_solution["points"] = i
        # TODO: template, solution, secret fields


def please(problem_sets):
    problems = export_problems(problem_sets)
    export_parts(problems)
