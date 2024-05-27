from django.apps import apps

try:
    apps.get_model("teams", "Team", require_ready=False)
    TEAMS_EXIST = True
except LookupError:
    TEAMS_EXIST = False
