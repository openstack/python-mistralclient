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

LOG = logging.getLogger(__name__)


def format_list(trigger=None):
    return format(trigger, lister=True)


def format(trigger=None, lister=False):
    columns = (
        'Name',
        'Pattern',
        'Workflow',
        'Workflow input',
        'Next execution time',
        'Created at',
        'Updated at'
    )

    if trigger:
        wf_input = trigger.workflow_input if not lister \
            else base.cut(trigger.workflow_input)

        data = (
            trigger.name,
            trigger.pattern,
            trigger.workflow_name,
            wf_input,
            trigger.next_execution_time,
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
        parser.add_argument('pattern', help='Cron trigger pattern')
        parser.add_argument('workflow_name', help='Workflow name')

        parser.add_argument(
            'workflow_input',
            nargs='?',
            help='Workflow input'
        )

        return parser

    def take_action(self, parsed_args):
        mgr = cron_triggers.CronTriggerManager(self.app.client)

        if parsed_args.workflow_input:
            try:
                wf_input = json.loads(parsed_args.workflow_input)
            except:
                wf_input = json.load(open(parsed_args.workflow_input))
        else:
            wf_input = {}

        trigger = mgr.create(
            parsed_args.name,
            parsed_args.pattern,
            parsed_args.workflow_name,
            wf_input
        )

        return format(trigger)


class Delete(command.Command):
    """Delete trigger."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', help='Cron trigger name')

        return parser

    def take_action(self, parsed_args):
        mgr = cron_triggers.CronTriggerManager(self.app.client)

        mgr.delete(parsed_args.name)
