from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from demo_dashboard.dashboards.mistral.executions.views import IndexView

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='index'),
)
