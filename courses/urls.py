from django.conf.urls import patterns, url, include
from tomo.views.problem_set import ProblemSetDelete


urlpatterns = patterns('courses.views',
    (r'^problemset/(?P<pk>\d+)/', include(patterns('courses.views',
        url(r'^toggle_solution_visibility/$', 'problemset_toggle_solution_visibility'),
        url(r'^toggle_visible/$', 'problemset_toggle_visible'),
        url(r'^move/(?P<shift>-?\d+)/$', 'problemset_move'),
        url(r'^delete/$', ProblemSetDelete.as_view(), name='problemset_delete')
    ))),
)
