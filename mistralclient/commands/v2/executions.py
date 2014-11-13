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

import json
import logging

from cliff import command
from cliff import show

from mistralclient.api.v2 import executions
from mistralclient.commands.v2 import base

LOG = logging.getLogger(__name__)


def format(execution=None):
    columns = (
        'ID',
        'Workflow',
        'State',
        'Created at',
        'Updated at'
    )
    # TODO(nmakhotkin) Add parent task id when it's implemented in API.

    if execution:
        data = (
            execution.id,
            execution.workflow_name,
            execution.state,
            execution.created_at,
            execution.updated_at or '<none>'
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all executions."""

    def _get_format_function(self):
        return format

    def _get_resources(self, parsed_args):
        return executions.ExecutionManager(self.app.client).list()


class Get(show.ShowOne):
    """Show specific execution."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution identifier')

        return parser

    def take_action(self, parsed_args):
        execution = executions.ExecutionManager(self.app.client).get(
            parsed_args.id)

        return format(execution)


class Create(show.ShowOne):
    """Create new execution."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'workflow_name',
            help='Execution workflow'
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

        return parser

    def take_action(self, parsed_args):
        if parsed_args.workflow_input:
            try:
                wf_input = json.loads(parsed_args.workflow_input)
            except:
                wf_input = json.load(open(parsed_args.workflow_input))
        else:
            wf_input = {}

        if parsed_args.params:
            try:
                params = json.loads(parsed_args.params)
            except:
                params = json.load(open(parsed_args.params))
        else:
            params = {}

        execution = executions.ExecutionManager(self.app.client).create(
            parsed_args.workflow_name,
            wf_input,
            **params)

        return format(execution)


class Delete(command.Command):
    """Delete execution."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution identifier')

        return parser

    def take_action(self, parsed_args):
        executions.ExecutionManager(self.app.client).delete(parsed_args.id)


class Update(show.ShowOne):
    """Update execution."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Execution identifier'
        )
        parser.add_argument(
            'state',
            choices=['RUNNING', 'PAUSED', 'SUCCESS', 'ERROR'],
            help='Execution state'
        )

        return parser

    def take_action(self, parsed_args):
        execution = executions.ExecutionManager(self.app.client).update(
            parsed_args.id,
            parsed_args.state)

        return format(execution)


class GetInput(command.Command):
    """Show execution input data."""

    def get_parser(self, prog_name):
        parser = super(GetInput, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution ID')

        return parser

    def take_action(self, parsed_args):
        ex_input = executions.ExecutionManager(self.app.client).get(
            parsed_args.id).input

        try:
            ex_input = json.loads(ex_input)
            ex_input = json.dumps(ex_input, indent=4) + "\n"
        except:
            LOG.debug("Execution input is not JSON.")

        self.app.stdout.write(ex_input or "\n")


class GetOutput(command.Command):
    """Show execution output data."""

    def get_parser(self, prog_name):
        parser = super(GetOutput, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution ID')

        return parser

    def take_action(self, parsed_args):
        output = executions.ExecutionManager(self.app.client).get(
            parsed_args.id).output

        try:
            output = json.loads(output)
            output = json.dumps(output, indent=4) + "\n"
        except:
            LOG.debug("Execution output is not JSON.")

        self.app.stdout.write(output or "\n")
