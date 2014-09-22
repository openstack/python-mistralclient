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
from cliff import lister
from cliff import show

from mistralclient.api.v2 import tasks

LOG = logging.getLogger(__name__)


def format(task=None):
    columns = (
        'ID',
        'Name',
        'Workflow name',
        'Execution ID',
        'State',
    )

    if task:
        data = (
            task.id,
            task.name,
            task.wf_name,
            task.execution_id,
            task.state,
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(lister.Lister):
    """List all tasks."""

    def take_action(self, parsed_args):
        data = [format(task)[1] for task
                in tasks.TaskManager(self.app.client).list()]

        if data:
            return format()[0], data
        else:
            return format()


class Get(show.ShowOne):
    """Show specific task."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Task identifier')
        return parser

    def take_action(self, parsed_args):
        execution = tasks.TaskManager(self.app.client)\
            .get(parsed_args.id)

        return format(execution)


class Update(show.ShowOne):
    """Update task."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Task identifier')
        parser.add_argument(
            'state',
            choices=['IDLE', 'RUNNING', 'SUCCESS', 'ERROR'],
            help='Task state')

        return parser

    def take_action(self, parsed_args):
        execution = tasks.TaskManager(self.app.client).update(
            parsed_args.id,
            parsed_args.state)

        return format(execution)


class GetOutput(command.Command):
    """Show task output data."""

    def get_parser(self, prog_name):
        parser = super(GetOutput, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            help='Task ID')

        return parser

    def take_action(self, parsed_args):
        output = tasks.TaskManager(self.app.client)\
            .get(parsed_args.id).output

        try:
            output = json.loads(output)
            output = json.dumps(output, indent=4) + "\n"
        except:
            LOG.debug("Task output is not JSON.")

        self.app.stdout.write(output or "\n")


class GetResult(command.Command):
    """Show task output data."""

    def get_parser(self, prog_name):
        parser = super(GetResult, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            help='Task ID')

        return parser

    def take_action(self, parsed_args):
        result = tasks.TaskManager(self.app.client)\
            .get(parsed_args.id).result

        try:
            result = json.loads(result)
            result = json.dumps(result, indent=4) + "\n"
        except:
            LOG.debug("Task result is not JSON.")

        self.app.stdout.write(result or "\n")


class GetInput(command.Command):
    """Show task input."""

    def get_parser(self, prog_name):
        parser = super(GetInput, self).get_parser(prog_name)
        parser.add_argument(
            'id',
            help='Task ID'
        )

        return parser

    def take_action(self, parsed_args):
        result = tasks.TaskManager(self.app.client)\
            .get(parsed_args.id).input

        try:
            result = json.loads(result)
            result = json.dumps(result, indent=4) + "\n"
        except:
            LOG.debug("Task result is not JSON.")

        self.app.stdout.write(result or "\n")
