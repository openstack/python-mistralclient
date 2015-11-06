# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import logging

from cliff import command
from cliff import show

from mistralclient.api.v2 import workbooks
from mistralclient.commands.v2 import base
from mistralclient import utils


LOG = logging.getLogger(__name__)


def format(workbook=None):
    columns = (
        'Name',
        'Tags',
        'Created at',
        'Updated at'
    )

    if workbook:
        data = (
            workbook.name,
            base.wrap(', '.join(workbook.tags or '')) or '<none>',
            workbook.created_at,
        )

        if hasattr(workbook, 'updated_at'):
            data += (workbook.updated_at,)
        else:
            data += (None,)

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all workbooks."""

    def _get_format_function(self):
        return format

    def _get_resources(self, parsed_args):
        return workbooks.WorkbookManager(self.app.client).list()


class Get(show.ShowOne):
    """Show specific workbook."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            help='Workbook name'
        )

        return parser

    def take_action(self, parsed_args):
        workbook = workbooks.WorkbookManager(self.app.client).get(
            parsed_args.name)

        return format(workbook)


class Create(show.ShowOne):
    """Create new workbook."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workbook definition file'
        )

        return parser

    def take_action(self, parsed_args):
        workbook = workbooks.WorkbookManager(self.app.client).create(
            parsed_args.definition.read())

        return format(workbook)


class Delete(command.Command):
    """Delete workbook."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', nargs='+', help='Name of workbook(s).')

        return parser

    def take_action(self, parsed_args):
        wb_mgr = workbooks.WorkbookManager(self.app.client)
        utils.do_action_on_many(
            lambda s: wb_mgr.delete(s),
            parsed_args.name,
            "Request to delete workbook %s has been accepted.",
            "Unable to delete the specified workbook(s)."
        )


class Update(show.ShowOne):
    """Update workbook."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workbook definition file'
        )

        return parser

    def take_action(self, parsed_args):
        workbook = workbooks.WorkbookManager(self.app.client).update(
            parsed_args.definition.read())

        return format(workbook)


class GetDefinition(command.Command):
    """Show workbook definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='Workbook name')

        return parser

    def take_action(self, parsed_args):
        definition = workbooks.WorkbookManager(self.app.client).get(
            parsed_args.name).definition

        self.app.stdout.write(definition or "\n")


class Validate(show.ShowOne):
    """Validate workbook."""

    def _format(self, result=None):
        columns = ('Valid', 'Error')

        if result:
            data = (result.get('valid'),)
            if not result.get('error'):
                data += (None,)
            else:
                data += (result.get('error'),)
        else:
            data = (tuple('<none>' for _ in range(len(columns))),)

        return columns, data

    def get_parser(self, prog_name):
        parser = super(Validate, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workbook definition file'
        )

        return parser

    def take_action(self, parsed_args):
        result = workbooks.WorkbookManager(self.app.client).validate(
            parsed_args.definition.read())

        return self._format(result)
