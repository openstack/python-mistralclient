from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ExecutionsTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    wb_name = tables.Column("workbook_name", verbose_name=_("Workbook"))
    state = tables.Column("state", verbose_name=_("State"))

    class Meta:
        name = "executions"
        verbose_name = _("Executions")
        # row_actions = (ExecuteWorkflow,)
