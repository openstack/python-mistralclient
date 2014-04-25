from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ExecuteWorkflow(tables.LinkAction):
    name = "execute"
    verbose_name = _("Execute")
    url = "horizon:mistral:workbooks:execute"
    classes = ("ajax-modal", "btn-edit")


def tags_to_string(workbook):
    return ', '.join(workbook.tags)


class WorkbooksTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    tags = tables.Column(tags_to_string, verbose_name=_("Tags"))

    def get_object_id(self, datum):
        return datum.name

    class Meta:
        name = "workbooks"
        verbose_name = _("Workbooks")
        row_actions = (ExecuteWorkflow,)
