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

from mistralclient.commands.v2 import base
from mistralclient import utils


LOG = logging.getLogger(__name__)


def format_list(workflow=None):
    return format(workflow, lister=True)


def format(workflow=None, lister=False):
    columns = (
        'ID',
        'Name',
        'Project ID',
        'Tags',
        'Input',
        'Created at',
        'Updated at'
    )

    if workflow:
        tags = getattr(workflow, 'tags', None) or []

        data = (
            workflow.id,
            workflow.name,
            workflow.project_id,
            base.wrap(', '.join(tags)) or '<none>',
            workflow.input if not lister else base.cut(workflow.input),
            workflow.created_at
        )

        if hasattr(workflow, 'updated_at'):
            data += (workflow.updated_at,)
        else:
            data += (None,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all workflows."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.workflows.list()


class Get(show.ShowOne):
    """Show specific workflow."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('name', help='Workflow name')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        wf = mistral_client.workflows.get(parsed_args.name)

        return format(wf)


class Create(base.MistralLister):
    """Create new workflow."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Workflow definition file'
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
            scope=scope
        )


class Delete(command.Command):
    """Delete workflow."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', nargs='+', help='Name of workflow(s).')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        utils.do_action_on_many(
            lambda s: mistral_client.workflows.delete(s),
            parsed_args.name,
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
            scope=scope
        )


class GetDefinition(command.Command):
    """Show workflow definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='Workflow name')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        definition = mistral_client.workflows.get(parsed_args.name).definition

        self.app.stdout.write(definition or "\n")


class Validate(show.ShowOne):
    """Validate workflow."""

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
            help='Workflow definition file'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        result = mistral_client.workflows.validate(
            parsed_args.definition.read()
        )

        return self._format(result)
