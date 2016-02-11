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
import os.path

from cliff import command
from cliff import show

from mistralclient.commands.v2 import base
from mistralclient import utils

LOG = logging.getLogger(__name__)


def format_list(execution=None):
    return format(execution, lister=True)


def format(execution=None, lister=False):
    columns = (
        'ID',
        'Workflow ID',
        'Workflow name',
        'Description',
        'Task Execution ID',
        'State',
        'State info',
        'Created at',
        'Updated at'
    )
    # TODO(nmakhotkin) Add parent task id when it's implemented in API.

    if execution:
        state_info = (execution.state_info if not lister
                      else base.cut(execution.state_info))

        data = (
            execution.id,
            execution.workflow_id,
            execution.workflow_name,
            execution.description,
            execution.task_execution_id or '<none>',
            execution.state,
            state_info,
            execution.created_at,
            execution.updated_at or '<none>'
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all executions."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, parsed_args):
        parser = super(List, self).get_parser(parsed_args)

        parser.add_argument(
            '--marker',
            type=str,
            help='The last execution uuid of the previous page, displays list '
                 'of executions after "marker".',
            default='',
            nargs='?'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of executions to return in a single result.',
            nargs='?'
        )
        parser.add_argument(
            '--sort_keys',
            help='Comma-separated list of sort keys to sort results by. '
                 'Default: created_at. '
                 'Example: mistral execution-list --sort_keys=id,description',
            default='created_at',
            nargs='?'
        )
        parser.add_argument(
            '--sort_dirs',
            help='Comma-separated list of sort directions. Default: asc. '
                 'Example: mistral execution-list --sort_keys=id,description '
                 '--sort_dirs=asc,desc',
            default='asc',
            nargs='?'
        )

        return parser

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.executions.list(
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            sort_keys=parsed_args.sort_keys,
            sort_dirs=parsed_args.sort_dirs
        )


class Get(show.ShowOne):
    """Show specific execution."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution identifier')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        execution = mistral_client.executions.get(parsed_args.id)

        return format(execution)


class Create(show.ShowOne):
    """Create new execution."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'workflow_identifier',
            help='Workflow ID or name. Workflow name will be deprecated since'
                 'Mitaka.'
        )
        parser.add_argument(
            'workflow_input',
            nargs='?',
            help='Workflow input'
        )
        parser.add_argument(
            'params',
            nargs='?',
            help='Workflow additional parameters'
        )
        parser.add_argument(
            '-d',
            '--description',
            dest='description',
            default='',
            help='Execution description'
        )

        return parser

    def take_action(self, parsed_args):
        if parsed_args.workflow_input:
            try:
                wf_input = json.loads(parsed_args.workflow_input)
            except Exception:
                wf_input = json.load(open(parsed_args.workflow_input))
        else:
            wf_input = {}

        if parsed_args.params:
            try:
                params = json.loads(parsed_args.params)
            except Exception:
                params = json.load(open(parsed_args.params))
        else:
            params = {}

        mistral_client = self.app.client_manager.workflow_engine

        execution = mistral_client.executions.create(
            parsed_args.workflow_identifier,
            wf_input,
            parsed_args.description,
            **params
        )

        return format(execution)


class Delete(command.Command):
    """Delete execution."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            nargs='+',
            help='Id of execution identifier(s).'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s: mistral_client.executions.delete(s),
            parsed_args.id,
            "Request to delete execution %s has been accepted.",
            "Unable to delete the specified execution(s)."
        )


class Update(show.ShowOne):
    """Update execution."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Execution identifier'
        )

        parser.add_argument(
            '-s',
            '--state',
            dest='state',
            choices=['RUNNING', 'PAUSED', 'SUCCESS', 'ERROR'],
            help='Execution state'
        )

        parser.add_argument(
            '-e',
            '--env',
            dest='env',
            help='Environment variables'
        )

        parser.add_argument(
            '-d',
            '--description',
            dest='description',
            help='Execution description'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        env = (
            utils.load_file(parsed_args.env)
            if parsed_args.env and os.path.isfile(parsed_args.env)
            else utils.load_content(parsed_args.env)
        )

        execution = mistral_client.executions.update(
            parsed_args.id,
            parsed_args.state,
            description=parsed_args.description,
            env=env
        )

        return format(execution)


class GetInput(command.Command):
    """Show execution input data."""

    def get_parser(self, prog_name):
        parser = super(GetInput, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution ID')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        ex_input = mistral_client.executions.get(parsed_args.id).input

        try:
            ex_input = json.loads(ex_input)
            ex_input = json.dumps(ex_input, indent=4) + "\n"
        except Exception:
            LOG.debug("Execution input is not JSON.")

        self.app.stdout.write(ex_input or "\n")


class GetOutput(command.Command):
    """Show execution output data."""

    def get_parser(self, prog_name):
        parser = super(GetOutput, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution ID')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        output = mistral_client.executions.get(parsed_args.id).output

        try:
            output = json.loads(output)
            output = json.dumps(output, indent=4) + "\n"
        except Exception:
            LOG.debug("Execution output is not JSON.")

        self.app.stdout.write(output or "\n")
