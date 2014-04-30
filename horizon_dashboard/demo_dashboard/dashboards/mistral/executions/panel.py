from django.utils.translation import ugettext_lazy as _

import horizon
from demo_dashboard.dashboards.mistral import dashboard


class Executions(horizon.Panel):
    name = _("Executions")
    slug = 'executions'


dashboard.MistralDashboard.register(Executions)
