import attempts.models as tomo


def export_attempts(users, parts):
    for attempt in tomo.Attempt.objects.all():
        for version in attempt.history:
            {
                "user": attempt.user.id,
                "task": attempt.part.id,  # TODO: glue?
                "source": bytes(attempt.solution, encoding="utf-8"),
                "upload_time": attempt.submission_date,
            }
    # TODO this is incomplete
    # TODO missing fields: part, valid, feedback
    # TODO valid -> max points


def export_all():
    # TODO will we even export attempts?
    pass
