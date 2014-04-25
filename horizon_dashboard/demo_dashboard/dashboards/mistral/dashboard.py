from django.utils.translation import ugettext_lazy as _

import horizon


class Default(horizon.Panel):
    name = _("Default")
    slug = 'default'
    urls = 'demo_dashboard.dashboards.mistral.workbooks.urls'
    nav = False


class MistralDashboard(horizon.Dashboard):
    name = _("Mistral")
    slug = "mistral"
    panels = ('default', 'workbooks', 'executions',)
    default_panel = 'default'
    roles = ('admin',)


horizon.register(MistralDashboard)
MistralDashboard.register(Default)
