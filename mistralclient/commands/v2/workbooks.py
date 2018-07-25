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

from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient import utils


def format(workbook=None):
    columns = (
        'Name',
        'Namespace',
        'Tags',
        'Scope',
        'Created at',
        'Updated at'
    )

    if workbook:
        data = (
            workbook.name,
            workbook.namespace,
            base.wrap(', '.join(workbook.tags or '')) or '<none>',
            workbook.scope,
            workbook.created_at,
        )

        if hasattr(workbook, 'updated_at'):
            data += (workbook.updated_at,)
        else:
            data += (None,)

    else:
        data = (tuple('' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all workbooks."""

    def _get_format_function(self):
        return format

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.workbooks.list()


class Get(command.ShowOne):
    """Show specific workbook."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('workbook', help='Workbook name')

        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to get the workbook from."
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        workbook = mistral_client.workbooks.get(
            parsed_args.workbook,
            parsed_args.namespace
        )

        return format(workbook)


class Create(command.ShowOne):
    """Create new workbook."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workbook definition file'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag workbook will be marked as "public".'
        )

        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to create the workbook within."
        )

        return parser

    def take_action(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine
        workbook = mistral_client.workbooks.create(
            parsed_args.definition.read(),
            namespace=parsed_args.namespace,
            scope=scope
        )

        return format(workbook)


class Delete(command.Command):
    """Delete workbook."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('workbook', nargs='+', help='Name of workbook(s).')
        parser.add_argument(
            '--namespace',
            nargs='?',
            default=None,
            help="Namespace to delete the workbook(s) from."
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        utils.do_action_on_many(
            lambda s: mistral_client.workbooks.delete(s,
                                                      parsed_args.namespace),
            parsed_args.workbook,
            "Request to delete workbook %s has been accepted.",
            "Unable to delete the specified workbook(s)."
        )


class Update(command.ShowOne):
    """Update workbook."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workbook definition file'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default=None,
            help="Namespace to update the workbook in."
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag workbook will be marked as "public".'
        )

        return parser

    def take_action(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine
        workbook = mistral_client.workbooks.update(
            parsed_args.definition.read(),
            namespace=parsed_args.namespace,
            scope=scope
        )

        return format(workbook)


class GetDefinition(command.Command):
    """Show workbook definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='Workbook name')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        definition = mistral_client.workbooks.get(parsed_args.name).definition

        self.app.stdout.write(definition or "\n")


class Validate(command.ShowOne):
    """Validate workbook."""

    def _format(self, result=None):
        columns = ('Valid', 'Error')

        if result:
            data = (result.get('valid'), result.get('error'),)
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
        mistral_client = self.app.client_manager.workflow_engine
        result = mistral_client.workbooks.validate(
            parsed_args.definition.read()
        )

        return self._format(result)
