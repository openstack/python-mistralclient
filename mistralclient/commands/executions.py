# Copyright 2014 StackStorm, Inc.
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

from cliff.command import Command as BaseCommand
from cliff.lister import Lister as ListCommand
from cliff.show import ShowOne as ShowCommand

from mistralclient.api.v1.executions import ExecutionManager

LOG = logging.getLogger(__name__)


def format(execution=None):
    columns = (
        'ID',
        'Workbook',
        'Task',
        'State'
    )

    if execution:
        data = (
            execution.id,
            execution.workbook_name,
            execution.task,
            execution.state
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return (columns, data)


class List(ListCommand):
    "List all executions"

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Execution workbook')

        return parser

    def take_action(self, parsed_args):
        data = [format(execution)[1] for execution
                in ExecutionManager(self.app.client)
                .list(parsed_args.workbook)]

        if data:
            return (format()[0], data)
        else:
            return format()


class Get(ShowCommand):
    "Show specific execution"

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Execution workbook')
        parser.add_argument(
            'id',
            help='Execution identifier')

        return parser

    def take_action(self, parsed_args):
        execution = ExecutionManager(self.app.client)\
            .get(parsed_args.workbook, parsed_args.id)

        return format(execution)


class Create(ShowCommand):
    "Create new execution"

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Execution workbook')
        parser.add_argument(
            'task',
            help='Execution task')
        parser.add_argument(
            'context',
            help='Execution context')

        return parser

    def take_action(self, parsed_args):
        try:
            ctx = json.loads(parsed_args.context)
        except:
            ctx = open(parsed_args.context).read()

        execution = ExecutionManager(self.app.client)\
            .create(parsed_args.workbook,
                    parsed_args.task,
                    ctx)

        return format(execution)


class Delete(BaseCommand):
    "Delete execution"

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Execution workbook')
        parser.add_argument(
            'id',
            help='Execution identifier')

        return parser

    def take_action(self, parsed_args):
        ExecutionManager(self.app.client)\
            .delete(parsed_args.workbook, parsed_args.id)


class Update(ShowCommand):
    "Update execution"

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Execution workbook')
        parser.add_argument(
            'id',
            help='Execution identifier')
        parser.add_argument(
            'state',
            choices=['RUNNING', 'SUSPENDED', 'STOPPED', 'SUCCESS', 'ERROR'],
            help='Execution state')

        return parser

    def take_action(self, parsed_args):
        execution = ExecutionManager(self.app.client)\
            .update(parsed_args.workbook,
                    parsed_args.id,
                    parsed_args.state)

        return format(execution)
