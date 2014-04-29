from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from demo_dashboard.dashboards.mistral.executions.views \
    import IndexView, TaskView

EXECUTIONS = r'^(?P<execution_id>[^/]+)/%s$'

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='index'),
    url(EXECUTIONS % 'tasks', TaskView.as_view(), name='tasks'),
)
