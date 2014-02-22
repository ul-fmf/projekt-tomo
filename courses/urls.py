from django.conf.urls import patterns, url, include


urlpatterns = patterns('courses.views',
    (r'^problemset/(?P<problemset_id>\d+)/', include(patterns('courses.views',
        url(r'^toggle_solution_visibility/$', 'problemset_toggle_solution_visibility'),
        url(r'^toggle_visible/$', 'problemset_toggle_visible'),
        url(r'^move/(?P<shift>-?\d+)/$', 'problemset_move'),
    ))),
)
