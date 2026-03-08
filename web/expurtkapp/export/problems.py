import json

import problems.models as tomo_problems
import attempts.models as tomo_attempts

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
    uploads = []
    solution_uploads = []

    for i, problem in enumerate(
        tomo_problems.Problem.objects.all()
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

        problem_uploads = {}
        # TODO: query all attempts with parts list and ordered by submission date
        attempts = tomo_attempts.Attempt.objects.filter(part__in=parts).order_by(
            "submission_date"
        )
        for attempt in attempts:
            upload = problem_uploads.get(
                attempt.user.id, {part.id: "" for part in parts}
            )
            current_part = upload[attempt.part.id]
            if current_part:
                uploads.append(
                    {
                        "user": attempt.user.id,
                        "lang": LANG_PY3,
                        "filename": url + ".py",
                        "source": PARTS_SEPARATOR_TOKEN.join(upload.values()),
                        "upload_time": None,
                        "status": UPLOAD_STATUS_DONE,
                        "agg_status": JAILRUN_STATUS_OK,
                        "preparation_status": JAILRUN_STATUS_OK,
                        "task": task["id"],
                        "points": 0,
                        "max_points": len(parts),
                        "is_official_solution": False,
                    }
                )

            upload[attempt.part.id] = attempt.solution
            problem_uploads[attempt.user.id] = upload
        uploads.extend(
            {
                "user": user_id,
                "lang": LANG_PY3,
                "filename": url + ".py",
                "source": PARTS_SEPARATOR_TOKEN.join(upload.values()),
                "upload_time": None,
                "status": UPLOAD_STATUS_DONE,
                "agg_status": JAILRUN_STATUS_OK,
                "preparation_status": JAILRUN_STATUS_OK,
                "task": task["id"],
                "points": 0,
                "max_points": len(parts),
                "is_official_solution": False,
            }
            for user_id, upload in problem_uploads.items()
        )

        # Create official upload
        solution_uploads.append(
            {
                "lang": LANG_PY3,
                "filename": url + ".py",
                "source": PARTS_SEPARATOR_TOKEN.join([part.solution for part in parts]),
                "upload_time": None,
                "status": UPLOAD_STATUS_DONE,
                "agg_status": JAILRUN_STATUS_OK,
                "preparation_status": JAILRUN_STATUS_OK,
                "task": task["id"],
                "points": len(parts),
                "max_points": len(parts),
                "is_official_solution": True,
            }
        )

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

    return tasks, contents, files, uploads, solution_uploads


def export_all():
    return export_problems()
