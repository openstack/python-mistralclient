# Copyright 2014 - Mirantis, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import argparse
import logging

from cliff import command
from cliff import lister
from cliff import show

from mistralclient.api.v2 import workflows

LOG = logging.getLogger(__name__)


def format(workflow=None):
    columns = (
        'Name',
        'Tags',
        'Created at',
        'Updated at'
    )

    if workflow:
        data = (
            workflow.name,
            ', '.join(workflow.tags or '') or '<none>',
            workflow.created_at,
        )
        if hasattr(workflow, 'updated_at'):
            data += (workflow.updated_at,)
        else:
            data += (None,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(lister.Lister):
    """List all workflows."""

    def take_action(self, parsed_args):
        data = [format(workflow)[1] for workflow
                in workflows.WorkflowManager(self.app.client).list()]

        if data:
            return format()[0], data
        else:
            return format()


class Get(show.ShowOne):
    """Show specific workflow."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            help='Workflow name')

        return parser

    def take_action(self, parsed_args):
        workflow = workflows.WorkflowManager(self.app.client).get(
            parsed_args.name)

        return format(workflow)


class Create(show.ShowOne):
    """Create new workflow."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help='Workflow name')
        parser.add_argument(
            'tags',
            nargs='?',
            help='Workflow tags separated by ","')
        parser.add_argument(
            'definition',
            nargs='?',
            type=argparse.FileType('r'),
            help='Workflow definition file'
        )

        return parser

    def take_action(self, parsed_args):
        if not parsed_args.definition:
            raise RuntimeError("You must provide path to workflow "
                               "definition file.")

        workflow = workflows.WorkflowManager(self.app.client)\
            .create(parsed_args.name,
                    parsed_args.definition.read(),
                    str(parsed_args.tags).split(','))

        return format(workflow)


class Delete(command.Command):
    """Delete workflow."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help='Workflow name')

        return parser

    def take_action(self, parsed_args):
        workflows.WorkflowManager(self.app.client).delete(parsed_args.name)


class Update(show.ShowOne):
    """Update workflow."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help='Workflow name')
        parser.add_argument(
            'tags',
            nargs='?',
            help='Workflow tags separated by ","')
        parser.add_argument(
            'definition',
            nargs='?',
            help='Workflow definition')

        return parser

    def take_action(self, parsed_args):
        if parsed_args.definition:
            workflow = workflows.WorkflowManager(self.app.client)\
                .update(parsed_args.name,
                        parsed_args.definition.read(),
                        str(parsed_args.tags).split(','))
        else:
            workflow = workflows.WorkflowManager(self.app.client)\
                .update(parsed_args.name,
                        None,
                        str(parsed_args.tags).split(','))

        return format(workflow)


class UploadDefinition(command.Command):
    """Upload workflow definition."""

    def get_parser(self, prog_name):
        parser = super(UploadDefinition, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help='Workflow name')
        parser.add_argument(
            'path',
            type=argparse.FileType('r'),
            help='Workflow definition file')

        return parser

    def take_action(self, parsed_args):
        workflow = workflows.WorkflowManager(self.app.client)\
            .update(parsed_args.name,
                    definition=parsed_args.path.read())

        self.app.stdout.write(workflow.definition or "\n")


class GetDefinition(command.Command):
    """Show workflow definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help='Workflow name')

        return parser

    def take_action(self, parsed_args):
        definition = workflows.WorkflowManager(self.app.client)\
            .get(parsed_args.name).definition

        self.app.stdout.write(definition or "\n")
