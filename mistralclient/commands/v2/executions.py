# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
# Copyright 2016 - Brocade Communications Systems, Inc.
#
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

from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient import utils

LOG = logging.getLogger(__name__)


class ExecutionFormatter(base.MistralFormatter):
    COLUMNS = [
        ('id', 'ID'),
        ('workflow_id', 'Workflow ID'),
        ('workflow_name', 'Workflow name'),
        ('workflow_namespace', 'Workflow namespace'),
        ('description', 'Description'),
        ('task_execution_id', 'Task Execution ID'),
        ('root_execution_id', 'Root Execution ID'),
        ('state', 'State'),
        ('state_info', 'State info'),
        ('created_at', 'Created at'),
        ('updated_at', 'Updated at'),
    ]

    @staticmethod
    def format(execution=None, lister=False):
        # TODO(nmakhotkin) Add parent task id when it's implemented in API.

        if execution:
            state_info = (execution.state_info if not lister
                          else base.cut(execution.state_info))

            data = (
                execution.id,
                execution.workflow_id,
                execution.workflow_name,
                execution.workflow_namespace,
                execution.description,
                execution.task_execution_id or '<none>',
                execution.root_execution_id or '<none>',
                execution.state,
                state_info,
                execution.created_at,
                execution.updated_at or '<none>'
            )
        else:
            data = (tuple('' for _ in
                          range(len(ExecutionFormatter.COLUMNS))),)

        return ExecutionFormatter.headings(), data


class List(base.MistralExecutionLister):
    """List all executions."""

    def _get_format_function(self):
        return ExecutionFormatter.format_list

    def get_parser(self, parsed_args):
        parser = super(List, self).get_parser(parsed_args)
        parser.add_argument(
            '--task',
            nargs='?',
            help="Parent task execution ID associated with workflow "
                 "execution list.",
        )

        return parser

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.executions.list(
            task=parsed_args.task,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            sort_keys=parsed_args.sort_keys,
            sort_dirs=parsed_args.sort_dirs,
            fields=ExecutionFormatter.fields(),
            **base.get_filters(parsed_args)
        )


class Get(command.ShowOne):
    """Show specific execution."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('execution', help='Execution identifier')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        execution = mistral_client.executions.get(parsed_args.execution)

        return ExecutionFormatter.format(execution)


class Create(command.ShowOne):
    """Create new execution."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'workflow_identifier',
            nargs='?',
            help='Workflow ID or name. Workflow name will be deprecated since '
                 'Mitaka.'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Workflow namespace."
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
        parser.add_argument(
            '-s',
            dest='source_execution_id',
            nargs='?',
            help="Workflow Execution id which will allow operators to create "
                 "a new workflow execution based on the previously successful "
                 "executed workflow. Example: mistral execution-create -s "
                 "123e4567-e89b-12d3-a456-426655440000")

        return parser

    def take_action(self, parsed_args):
        if parsed_args.workflow_input:
            wf_input = utils.load_json(parsed_args.workflow_input)
        else:
            wf_input = {}

        if parsed_args.params:
            params = utils.load_json(parsed_args.params)
        else:
            params = {}

        mistral_client = self.app.client_manager.workflow_engine

        execution = mistral_client.executions.create(
            parsed_args.workflow_identifier,
            parsed_args.namespace,
            wf_input,
            parsed_args.description,
            parsed_args.source_execution_id,
            **params
        )

        return ExecutionFormatter.format(execution)


class Delete(command.Command):
    """Delete execution."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'execution',
            nargs='+',
            help='Id of execution identifier(s).'
        )

        parser.add_argument(
            '--force',
            default=False,
            action='store_true',
            help='Force the deletion of an execution. Might cause a cascade '
                 ' of errors if used for running executions.'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        force = parsed_args.force

        utils.do_action_on_many(
            lambda s: mistral_client.executions.delete(s, force=force),
            parsed_args.execution,
            "Request to delete execution %s has been accepted.",
            "Unable to delete the specified execution(s)."
        )


class Update(command.ShowOne):
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
            choices=['RUNNING', 'PAUSED', 'SUCCESS', 'ERROR', 'CANCELLED'],
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

        return ExecutionFormatter.format(execution)


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


REPORT_ENTRY_INDENT = 4


class GetReport(command.Command):
    """Print execution report."""

    def get_parser(self, prog_name):
        parser = super(GetReport, self).get_parser(prog_name)

        parser.add_argument('id', help='Execution ID')
        parser.add_argument(
            '--errors-only',
            dest='errors_only',
            action='store_true',
            help='Only error paths will be included.'
        )
        parser.add_argument(
            '--no-errors-only',
            dest='errors_only',
            action='store_false',
            help='Not only error paths will be included.'
        )
        parser.set_defaults(errors_only=True)

        parser.add_argument(
            '--max-depth',
            dest='max_depth',
            nargs='?',
            type=int,
            default=-1,
            help='Maximum depth of the workflow execution tree. '
                 'If 0, only the root workflow execution and its '
                 'tasks will be included'
        )

        return parser

    def print_line(self, line, level=0):
        self.app.stdout.write(
            "%s%s\n" % (' ' * (level * REPORT_ENTRY_INDENT), line)
        )

    def print_workflow_execution_entry(self, wf_ex, level):
        self.print_line(
            "workflow '%s' [%s] %s" %
            (wf_ex['name'], wf_ex['state'], wf_ex['id']),
            level
        )

        if 'task_executions' in wf_ex:
            for t_ex in wf_ex['task_executions']:
                self.print_task_execution_entry(t_ex, level + 1)

    def print_task_execution_entry(self, t_ex, level):
        self.print_line(
            "task '%s' [%s] %s" %
            (t_ex['name'], t_ex['state'], t_ex['id']),
            level
        )

        if t_ex['state'] == 'ERROR':
            state_info = t_ex['state_info']
            state_info = state_info[0:200] + '...'

            self.print_line('(error info: %s)' % state_info, level)

        if 'action_executions' in t_ex:
            for a_ex in t_ex['action_executions']:
                self.print_action_execution_entry(a_ex, level + 1)

        if 'workflow_executions' in t_ex:
            for wf_ex in t_ex['workflow_executions']:
                self.print_workflow_execution_entry(wf_ex, level + 1)

    def print_action_execution_entry(self, a_ex, level):
        self.print_line(
            "action '%s' [%s] %s" %
            (a_ex['name'], a_ex['state'], a_ex['id']),
            level
        )

    def print_statistics(self, stat):
        self.print_line(
            'Number of tasks in SUCCESS state: %s' %
            stat['success_tasks_count']
        )
        self.print_line(
            'Number of tasks in ERROR state: %s' % stat['error_tasks_count']
        )
        self.print_line(
            'Number of tasks in RUNNING state: %s' %
            stat['running_tasks_count']
        )
        self.print_line(
            'Number of tasks in IDLE state: %s' % stat['idle_tasks_count']
        )
        self.print_line(
            'Number of tasks in PAUSED state: %s\n' %
            stat['paused_tasks_count']
        )

    def print_report(self, report_json):
        self.print_line(
            "\nTo get more details on a task failure "
            "run: mistral task-get <id> -c 'State info'\n"
        )

        frame_line = '=' * 30

        self.print_line(
            '%s General Statistics %s\n' %
            (frame_line, frame_line)
        )
        self.print_statistics(report_json['statistics'])

        self.print_line(
            '%s Workflow Execution Tree %s\n' %
            (frame_line, frame_line)
        )
        self.print_workflow_execution_entry(
            report_json['root_workflow_execution'],
            0
        )

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        report_json = mistral_client.executions.get_report(
            parsed_args.id,
            errors_only=parsed_args.errors_only,
            max_depth=parsed_args.max_depth
        )

        self.print_report(report_json)
