from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ExecutionsTable(tables.DataTable):
    id = tables.Column("id",
                       verbose_name=_("ID"),
                       link=("horizon:mistral:executions:tasks"))
    wb_name = tables.Column("workbook_name", verbose_name=_("Workbook"))
    state = tables.Column("state", verbose_name=_("State"))

    class Meta:
        name = "executions"
        verbose_name = _("Executions")


class TaskTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    name = tables.Column("name", verbose_name=_("Name"))
    action = tables.Column("action", verbose_name=_("Action"))
    state = tables.Column("state", verbose_name=_("State"))

    class Meta:
        name = "tasks"
        verbose_name = _("Tasks")
