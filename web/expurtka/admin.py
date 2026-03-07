from django.contrib import admin

from expurtka.putka.models.alerts import Alert
from expurtka.putka.models.common import UntabledItem
from expurtka.putka.models.contests import (
    Contest,
    ContestGroup,
    ContestGroupMembership,
    Contestant,
    ContestUpload,
    StaticScoreboard,
)
from expurtka.putka.models.forums import (
    ContestThread,
    Forum,
    GeneralThread,
    Post,
    TaskThread,
    Thread,
)
from expurtka.putka.models.groups import Group
from expurtka.putka.models.pauth import GroupObjectPermission, UserObjectPermission
from expurtka.putka.models.results import TestCase, Upload, UserTest
from expurtka.putka.models.tasks import File, Set, Tag, Task, TaskLink
from expurtka.putka.models.users import Profile, User
from expurtka.putka.models.wiki import Content

admin.site.register(Alert)
admin.site.register(UntabledItem)
admin.site.register(Contest)
admin.site.register(ContestGroup)
admin.site.register(ContestGroupMembership)
admin.site.register(Contestant)
admin.site.register(ContestUpload)
admin.site.register(StaticScoreboard)
admin.site.register(ContestThread)
admin.site.register(Forum)
admin.site.register(GeneralThread)
admin.site.register(Post)
admin.site.register(TaskThread)
admin.site.register(Thread)
admin.site.register(Group)
admin.site.register(GroupObjectPermission)
admin.site.register(UserObjectPermission)
admin.site.register(TestCase)
admin.site.register(Upload)
admin.site.register(UserTest)
admin.site.register(File)
admin.site.register(Set)
admin.site.register(Tag)
admin.site.register(Task)
admin.site.register(TaskLink)
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(Content)
