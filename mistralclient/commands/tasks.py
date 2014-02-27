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

from cliff.lister import Lister as ListCommand
from cliff.show import ShowOne as ShowCommand

from mistralclient.openstack.common import log as logging
from mistralclient.api.tasks import TaskManager

LOG = logging.getLogger(__name__)


def format(task=None):
    columns = (
        'ID',
        'Workbook',
        'Execution',
        'Name',
        'Description',
        'State',
        'Tags'
    )

    if task:
        data = (
            task.id,
            task.workbook_name,
            task.execution_id,
            task.name,
            task.description or '<none>',
            task.state,
            task.tags and ', '.join(task.tags) or '<none>'
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return (columns, data)


class List(ListCommand):
    "List all tasks"

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Task workbook')
        parser.add_argument(
            'execution',
            help='Task execution')

        return parser

    def take_action(self, parsed_args):
        data = [format(task)[1] for task
                in TaskManager(self.app.client)
                .list(parsed_args.workbook,
                      parsed_args.execution)]

        if data:
            return (format()[0], data)
        else:
            return format()


class Get(ShowCommand):
    "Show specific task"

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Task workbook')
        parser.add_argument(
            'execution',
            help='Task execution')
        parser.add_argument(
            'id',
            help='Task identifier')
        return parser

    def take_action(self, parsed_args):
        execution = TaskManager(self.app.client)\
            .get(parsed_args.workbook,
                 parsed_args.execution,
                 parsed_args.id)

        return format(execution)


class Update(ShowCommand):
    "Update task"

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)
        parser.add_argument(
            'workbook',
            help='Task workbook')
        parser.add_argument(
            'execution',
            help='Task execution')
        parser.add_argument(
            'id',
            help='Task identifier')
        parser.add_argument(
            'state',
            choices=['IDLE', 'RUNNING', 'SUCCESS', 'ERROR'],
            help='Task state')

        return parser

    def take_action(self, parsed_args):
        execution = TaskManager(self.app.client).update(parsed_args.workbook,
                                                        parsed_args.execution,
                                                        parsed_args.id,
                                                        parsed_args.state)

        return format(execution)
