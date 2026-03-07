import attempts.models as tomo


def export_attempts(users, parts):
    for attempt in tomo.Attempt.objects.all():
        for version in attempt.history:
            {
                "user": users[attempt.user.id],
                "task": parts[attempt.part.id],  # TODO: glue?
                "source": bytes(attempt.solution, encoding="utf-8"),
                "upload_time": attempt.submission_date,
            }
    # TODO this is incomplete
    # TODO missing fields: part, valid, feedback
    # TODO valid -> max points


def please():
    # TODO will we even export attempts?
    pass
