import users.models as tomo


def export_users():
    return [
        {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "date_joined": user.date_joined.strftime("%Y-%m-%d"),
        }
        for user in tomo.User.objects.all()
    ]


def export_all():
    return export_users()
