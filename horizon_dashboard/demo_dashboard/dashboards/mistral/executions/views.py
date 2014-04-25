from horizon import tables

from demo_dashboard.dashboards.mistral import api
from demo_dashboard.dashboards.mistral.executions.tables import ExecutionsTable


class IndexView(tables.DataTableView):
    table_class = ExecutionsTable
    template_name = 'mistral/executions/index.html'

    def get_data(self):
        client = api.mistralclient(self.request)
        return [item for wb in client.workbooks.list()
                for item in client.executions.list(wb.name)]
