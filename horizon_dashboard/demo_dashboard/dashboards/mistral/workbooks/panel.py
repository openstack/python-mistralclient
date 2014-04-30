from django.utils.translation import ugettext_lazy as _

import horizon

from demo_dashboard.dashboards.mistral import dashboard


class Workbooks(horizon.Panel):
    name = _("Workbooks")
    slug = 'workbooks'


dashboard.MistralDashboard.register(Workbooks)
