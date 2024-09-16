import expurtka.putka as putka
import users.models as tomo


def export_users():
    putka.User.objects.all().delete()
    users_map = {}
    for user in tomo.User.objects.all():
        new = putka.User(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_staff=user.is_staff,
            is_active=user.is_active,
            date_joined=user.date_joined,
        )
        users_map[user.id] = new
    return users_map


def please():
    return export_users()
