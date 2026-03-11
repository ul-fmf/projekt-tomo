import attempts.models as tomo
import problems.models as tomo_problems
from expurtkapp.export.problems import (
    JAILRUN_STATUS_OK,
    LANG_PY3,
    UPLOAD_STATUS_DONE,
)

SOLUTION_SEPARATOR_TOKEN = "\n\n# {{{ PART BREAK }}}\n\n"


def export_all(tasks):
    """Export attempts as uploads grouped by (user, problem).

    tasks: list of task dicts from problems.export_all()
    """
    # Build task lookup: task id -> task dict
    task_by_id = {t["id"]: t for t in tasks}

    uploads = []

    # Build mapping: part_id -> (problem_id, index within problem)
    # and count parts per problem
    part_index = {}
    num_parts = {}
    for problem in tomo_problems.Problem.objects.prefetch_related("parts"):
        parts = list(problem.parts.all())
        num_parts[problem.id] = len(parts)
        for idx, part in enumerate(parts):
            part_index[part.id] = (problem.id, idx)

    # Track current solution state per (user_id, problem_id)
    # state[key] = (parts_list, latest_submission_date)
    state = {}

    for attempt in tomo.Attempt.objects.all():
        if attempt.part_id not in part_index:
            continue
        problem_id, idx = part_index[attempt.part_id]
        if problem_id not in task_by_id:
            continue

        key = (attempt.user_id, problem_id)

        if key not in state:
            state[key] = ([""] * num_parts[problem_id], None)

        parts_list, latest_date = state[key]
        parts_list[idx] = attempt.solution

        if latest_date is None or (
            attempt.submission_date and attempt.submission_date > latest_date
        ):
            latest_date = attempt.submission_date

        state[key] = (parts_list, latest_date)

    # Emit uploads
    for (user_id, problem_id), (parts_list, latest_date) in state.items():
        if any(s != "" for s in parts_list):
            task = task_by_id[problem_id]
            uploads.append({
                "user": user_id,
                "lang": LANG_PY3,
                "filename": task["url"] + ".py",
                "source": SOLUTION_SEPARATOR_TOKEN.join(parts_list),
                "upload_time": latest_date.isoformat() if latest_date else None,
                "status": UPLOAD_STATUS_DONE,
                "agg_status": JAILRUN_STATUS_OK,
                "preparation_status": JAILRUN_STATUS_OK,
                "task": problem_id,
                "points": sum(1 for s in parts_list if s != ""),
                "max_points": len(parts_list),
                "is_official_solution": False,
            })

    return uploads
