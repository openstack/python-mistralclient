from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import forms
from horizon import messages

from demo_dashboard.dashboards.mistral import api


class ExecuteForm(forms.SelfHandlingForm):
    workbook_name = forms.CharField(label=_("Workbook"),
                                    required=True,
                                    widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}))
    task = forms.CharField(label=_("Task"),
                           required=True,
                           help_text=_("Name of the task to stop"))
    context = forms.CharField(label=_("Context"),
                              required=False,
                              initial="{}",
                              widget=forms.widgets.Textarea())

    def __init__(self, request, *args, **kwargs):
        super(ExecuteForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        try:
            ex = api.mistralclient(request).executions.create(**data)

            msg = _('Execution has been created with id "%s".') % ex.id
            messages.success(request, msg)
            return True
        except Exception:
            msg = _('Failed to execute workbook "%s".') % data['workbook_name']
            redirect = reverse('horizon:mistral:workbooks:index')
            exceptions.handle(request, msg, redirect=redirect)
