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

import logging
import os.path

from oslo_serialization import jsonutils

from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient.commands.v2 import executions
from mistralclient import utils

LOG = logging.getLogger(__name__)


class TaskFormatter(base.MistralFormatter):
    COLUMNS = [
        ('id',                      'ID'),
        ('name',                    'Name'),
        ('workflow_name',           'Workflow name'),
        ('workflow_namespace',      'Workflow namespace'),
        ('workflow_execution_id',   'Workflow Execution ID'),
        ('state',                   'State'),
        ('state_info',              'State info'),
        ('created_at',              'Created at'),
        ('updated_at',              'Updated at'),
    ]

    @staticmethod
    def format(task=None, lister=False):
        if task:
            state_info = (task.state_info if not lister
                          else base.cut(task.state_info))

            data = (
                task.id,
                task.name,
                task.workflow_name,
                task.workflow_namespace,
                task.workflow_execution_id,
                task.state,
                state_info,
                task.created_at,
                task.updated_at or '<none>'
            )
        else:
            data = (tuple('' for _ in range(len(TaskFormatter.COLUMNS))),)

        return TaskFormatter.headings(), data


class List(base.MistralExecutionLister):
    """List all tasks."""

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        parser.add_argument(
            'workflow_execution',
            nargs='?',
            help='Workflow execution ID associated with list of Tasks.'
        )
        return parser

    def _get_format_function(self):
        return TaskFormatter.format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.tasks.list(
            parsed_args.workflow_execution,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            sort_keys=parsed_args.sort_keys,
            sort_dirs=parsed_args.sort_dirs,
            fields=TaskFormatter.fields(),
            **base.get_filters(parsed_args)
        )


class Get(command.ShowOne):
    """Show specific task."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('task', help='Task identifier')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        execution = mistral_client.tasks.get(parsed_args.task)

        return TaskFormatter.format(execution)


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
            result = jsonutils.loads(result)
            result = jsonutils.dumps(result, indent=4) + "\n"
        except Exception:
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
        res = mistral_client.tasks.get(parsed_args.id)
        published = res.published
        published_glob = res.published_global \
            if hasattr(res, 'published_global') else None

        try:
            published = jsonutils.loads(published)
            published = jsonutils.dumps(published, indent=4) + "\n"

            if published_glob:
                published_glob = jsonutils.loads(published_glob)
                published += jsonutils.dumps(published_glob, indent=4) + "\n"
        except Exception:
            LOG.debug("Task result is not JSON.")

        self.app.stdout.write(published or "\n")


class Rerun(command.ShowOne):
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

        parser.add_argument(
            '-e',
            '--env',
            dest='env',
            help='Environment variables'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        env = (
            utils.load_file(parsed_args.env)
            if parsed_args.env and os.path.isfile(parsed_args.env)
            else utils.load_content(parsed_args.env)
        )

        execution = mistral_client.tasks.rerun(
            parsed_args.id,
            reset=(not parsed_args.resume),
            env=env
        )

        return TaskFormatter.format(execution)


class SubExecutionsLister(executions.SubExecutionsBaseLister):

    def _get_format_function(self):
        return executions.ExecutionFormatter.format_list

    def _get_resources_function(self):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.tasks.get_task_sub_executions
