import expurtka.putka as putka
import attempts.models as tomo


def export_attempts(
    users_map: dict[str, putka.User],
    parts_map: dict[str, putka.Task],
):
    for attempt in tomo.Attempt.objects.all():
        for version in attempt.history:
            new = putka.Upload(
                user=users_map[attempt.user.id],
                task=parts_map[attempt.part.id],  # TODO: glue?
                source=bytes(attempt.solution, encoding="utf-8"),
                upload_time=attempt.submission_date,
            )
    # TODO this is incomplete
    # TODO missing fields: part, valid, feedback
    # TODO valid -> max points


def please():
    # TODO will we even export attempts?
    pass
