from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import yaml

from horizon import exceptions
from horizon import forms
from horizon import messages

from demo_dashboard.dashboards.mistral import api


class ExecuteForm(forms.SelfHandlingForm):
    workbook_name = forms.CharField(label=_("Workbook"),
                                    required=True,
                                    widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}))
    task = forms.ChoiceField(label=_("Task"),
                             required=True,
                             help_text=_("Task to start the execution"))
    context = forms.CharField(label=_("Context"),
                              required=False,
                              initial="{}",
                              widget=forms.widgets.Textarea())

    def __init__(self, request, *args, **kwargs):
        super(ExecuteForm, self).__init__(request, *args, **kwargs)
        client = api.mistralclient(request)
        workbook_definition = client.workbooks.get_definition(
            kwargs['initial']['workbook_name'])
        workbook = yaml.safe_load(workbook_definition)

        task_choices = [('', _("Select a task"))]
        for task in workbook['Workflow']['tasks']:
            task_choices.append((task, task))
        self.fields['task'].choices = task_choices

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
