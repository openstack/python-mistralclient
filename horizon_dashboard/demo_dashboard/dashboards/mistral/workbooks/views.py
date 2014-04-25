from django.core.urlresolvers import reverse_lazy

from horizon import tables, forms

from demo_dashboard.dashboards.mistral import api
from demo_dashboard.dashboards.mistral.workbooks.tables import WorkbooksTable
from demo_dashboard.dashboards.mistral.workbooks.forms import ExecuteForm


class IndexView(tables.DataTableView):
    table_class = WorkbooksTable
    template_name = 'mistral/workbooks/index.html'

    def get_data(self):
        return api.mistralclient(self.request).workbooks.list()


class ExecuteView(forms.ModalFormView):
    form_class = ExecuteForm
    template_name = 'mistral/workbooks/execute.html'
    success_url = reverse_lazy("horizon:mistral:executions:index")

    def get_context_data(self, **kwargs):
        context = super(ExecuteView, self).get_context_data(**kwargs)
        context["workbook_name"] = self.kwargs['workbook_name']
        return context

    def get_initial(self, **kwargs):
        return {
            'workbook_name': self.kwargs['workbook_name']
        }
