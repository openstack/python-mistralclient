# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
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

import json
import logging

from cliff import command
from cliff import show

from mistralclient.commands.v2 import base

LOG = logging.getLogger(__name__)


def format_list(task=None):
    return format(task, lister=True)


def format(task=None, lister=False):
    columns = (
        'ID',
        'Name',
        'Workflow name',
        'Execution ID',
        'State',
        'State info'
    )

    if task:
        state_info = (task.state_info if not lister
                      else base.cut(task.state_info))

        data = (
            task.id,
            task.name,
            task.workflow_name,
            task.workflow_execution_id,
            task.state,
            state_info
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all tasks."""

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        parser.add_argument(
            'workflow_execution',
            nargs='?',
            help='Workflow execution ID associated with list of Tasks.')
        return parser

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.tasks.list(parsed_args.workflow_execution)


class Get(show.ShowOne):
    """Show specific task."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('id', help='Task identifier')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        execution = mistral_client.tasks.get(parsed_args.id)

        return format(execution)


class GetResult(command.Command):
    """Show task output data."""

    def get_parser(self, prog_name):
        parser = super(GetResult, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            help='Task ID')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        result = mistral_client.tasks.get(parsed_args.id).result

        try:
            result = json.loads(result)
            result = json.dumps(result, indent=4) + "\n"
        except:
            LOG.debug("Task result is not JSON.")

        self.app.stdout.write(result or "\n")


class GetPublished(command.Command):
    """Show task published variables."""

    def get_parser(self, prog_name):
        parser = super(GetPublished, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            help='Task ID')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        result = mistral_client.tasks.get(parsed_args.id).published

        try:
            result = json.loads(result)
            result = json.dumps(result, indent=4) + "\n"
        except:
            LOG.debug("Task result is not JSON.")

        self.app.stdout.write(result or "\n")


class Rerun(show.ShowOne):
    """Rerun an existing task."""

    def get_parser(self, prog_name):
        parser = super(Rerun, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Task identifier'
        )

        parser.add_argument(
            '--resume',
            action='store_true',
            dest='resume',
            default=False,
            help=('rerun only failed or unstarted action '
                  'executions for with-items task')
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        execution = mistral_client.tasks.rerun(
            parsed_args.id,
            reset=(not parsed_args.resume)
        )

        return format(execution)
