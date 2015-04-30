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

from mistralclient.api.v2 import cron_triggers
from mistralclient.commands.v2 import base
from mistralclient import utils

LOG = logging.getLogger(__name__)


def format_list(trigger=None):
    return format(trigger, lister=True)


def format(trigger=None, lister=False):
    columns = (
        'Name',
        'Workflow',
        'Params',
        'Pattern',
        # TODO(rakhmerov): Uncomment when passwords are handled properly.
        # TODO(rakhmerov): Add 'Workflow input' column.
        'Next execution time',
        'Remaining executions',
        'Created at',
        'Updated at'
    )

    if trigger:
        # TODO(rakhmerov): Add following here:
        # TODO(rakhmerov): wf_input = trigger.workflow_input if not lister
        # TODO(rakhmerov:):    else base.cut(trigger.workflow_input)

        data = (
            trigger.name,
            trigger.workflow_name,
            trigger.workflow_params,
            trigger.pattern,
            # TODO(rakhmerov): Uncomment when passwords are handled properly.
            # TODo(rakhmerov): Add 'wf_input' here.
            trigger.next_execution_time,
            trigger.remaining_executions,
            trigger.created_at,
        )

        if hasattr(trigger, 'updated_at'):
            data += (trigger.updated_at,)
        else:
            data += (None,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all cron triggers."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        return cron_triggers.CronTriggerManager(self.app.client).list()


class Get(show.ShowOne):
    """Show specific cron trigger."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('name', help='Cron trigger name')

        return parser

    def take_action(self, parsed_args):
        mgr = cron_triggers.CronTriggerManager(self.app.client)

        return format(mgr.get(parsed_args.name))


class Create(show.ShowOne):
    """Create new trigger."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument('name', help='Cron trigger name')
        parser.add_argument('workflow_name', help='Workflow name')

        parser.add_argument(
            'workflow_input',
            nargs='?',
            help='Workflow input'
        )

        parser.add_argument(
            '--params',
            help='Workflow params',
        )

        parser.add_argument(
            '--pattern',
            type=str,
            help='Cron trigger pattern',
            metavar='<* * * * *>'
        )
        parser.add_argument(
            '--first-time',
            type=str,
            help="Date and time of the first execution",
            metavar='<YYYY-MM-DD HH:MM>'
        )
        parser.add_argument(
            '--count',
            type=int,
            help="Number of wanted executions",
            metavar='<integer>'
        )

        return parser

    @staticmethod
    def _get_file_content_or_dict(string):
        if string:
            try:
                return json.loads(string)
            except:
                return json.load(open(string))
        else:
            return {}

    def take_action(self, parsed_args):
        mgr = cron_triggers.CronTriggerManager(self.app.client)

        wf_input = self._get_file_content_or_dict(parsed_args.workflow_input)
        wf_params = self._get_file_content_or_dict(parsed_args.params)

        trigger = mgr.create(
            parsed_args.name,
            parsed_args.workflow_name,
            wf_input,
            wf_params,
            parsed_args.pattern,
            parsed_args.first_time,
            parsed_args.count
        )

        return format(trigger)


class Delete(command.Command):
    """Delete trigger."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', nargs='+', help='Name of cron trigger(s).')

        return parser

    def take_action(self, parsed_args):
        mgr = cron_triggers.CronTriggerManager(self.app.client)
        utils.do_action_on_many(
            lambda s: mgr.delete(s),
            parsed_args.name,
            "Request to delete cron trigger %s has been accepted.",
            "Unable to delete the specified cron trigger(s)."
        )
