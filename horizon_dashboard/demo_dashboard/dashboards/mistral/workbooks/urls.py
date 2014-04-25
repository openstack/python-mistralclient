from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from demo_dashboard.dashboards.mistral.workbooks.views \
    import IndexView, ExecuteView

WORKBOOKS = r'^(?P<workbook_name>[^/]+)/%s$'

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='index'),
    url(WORKBOOKS % 'execute', ExecuteView.as_view(), name='execute'),
)
