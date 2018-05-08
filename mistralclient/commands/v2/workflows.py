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

from cliff import command
from cliff import show

from mistralclient.commands.v2 import base
from mistralclient import utils


def format_list(workflow=None):
    return format(workflow, lister=True)


def format(workflow=None, lister=False):
    columns = (
        'ID',
        'Name',
        'Namespace',
        'Project ID',
        'Tags',
        'Input',
        'Scope',
        'Created at',
        'Updated at'
    )

    if workflow:
        tags = getattr(workflow, 'tags', None) or []

        data = (
            workflow.id,
            workflow.name,
            workflow.namespace,
            workflow.project_id,
            base.wrap(', '.join(tags)) or '<none>',
            workflow.input if not lister else base.cut(workflow.input),
            workflow.scope,
            workflow.created_at
        )

        if hasattr(workflow, 'updated_at'):
            data += (workflow.updated_at,)
        else:
            data += (None,)
    else:
        data = (tuple('' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all workflows."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        parser.add_argument(
            '--filter',
            dest='filters',
            action='append',
            help='Filters. Can be repeated.'
        )

        return parser

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.workflows.list(
            **base.get_filters(parsed_args)
        )


class Get(show.ShowOne):
    """Show specific workflow."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('workflow', help='Workflow ID or name.')
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to get the workflow from.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        wf = mistral_client.workflows.get(
            parsed_args.workflow,
            parsed_args.namespace
        )

        return format(wf)


class Create(base.MistralLister):
    """Create new workflow."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workflow definition file.'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to create the workflow within.",
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag workflow will be marked as "public".'
        )

        return parser

    def _get_format_function(self):
        return format_list

    def _validate_parsed_args(self, parsed_args):
        if not parsed_args.definition:
            raise RuntimeError("You must provide path to workflow "
                               "definition file.")

    def _get_resources(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.workflows.create(
            parsed_args.definition.read(),
            namespace=parsed_args.namespace,
            scope=scope
        )


class Delete(command.Command):
    """Delete workflow."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'workflow',
            nargs='+',
            help='Name or ID of workflow(s).'
        )

        parser.add_argument(
            '--namespace',
            nargs='?',
            default=None,
            help="Namespace to delete the workflow from.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        utils.do_action_on_many(
            lambda s: mistral_client.workflows.delete(s,
                                                      parsed_args.namespace),
            parsed_args.workflow,
            "Request to delete workflow %s has been accepted.",
            "Unable to delete the specified workflow(s)."
        )


class Update(base.MistralLister):
    """Update workflow."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workflow definition'
        )

        parser.add_argument('--id', help='Workflow ID.')

        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace of the workflow.",
        )

        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag workflow will be marked as "public".'
        )

        return parser

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.workflows.update(
            parsed_args.definition.read(),
            scope=scope,
            id=parsed_args.id,
            namespace=parsed_args.namespace
        )


class GetDefinition(command.Command):
    """Show workflow definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('identifier', help='Workflow ID or name.')
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to get the workflow from.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        wf = mistral_client.workflows.get(
            parsed_args.identifier,
            parsed_args.namespace
        )

        self.app.stdout.write(wf.definition or "\n")


class Validate(show.ShowOne):
    """Validate workflow."""

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
            help='Workflow definition file'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        result = mistral_client.workflows.validate(
            parsed_args.definition.read()
        )

        return self._format(result)
