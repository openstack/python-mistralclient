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
import datetime
import time

from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient import utils


class CronTriggerFormatter(base.MistralFormatter):
    COLUMNS = [
        ('name', 'Name'),
        ('workflow_name', 'Workflow'),
        ('workflow_params', 'Params'),
        ('pattern', 'Pattern'),
        # TODO(rakhmerov): Uncomment when passwords are handled properly.
        # TODO(rakhmerov): Add 'Workflow input' column.
        ('next_execution_time', 'Next execution time'),
        ('remaining_executions', 'Remaining executions'),
        ('created_at', 'Created at'),
        ('updated_at', 'Updated at')
    ]

    @staticmethod
    def format(trigger=None, lister=False):
        if trigger:
            # TODO(rakhmerov): Add following here:
            # TODO(rakhmerov): wf_input = trigger.workflow_input if not lister
            # TODO(rakhmerov:):    else base.cut(trigger.workflow_input)

            data = (
                trigger.name,
                trigger.workflow_name,
                trigger.workflow_params,
                trigger.pattern,
                # TODO(rakhmerov): Uncomment when passwords are handled
                #  properly.
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
            data = (tuple('' for _ in
                          range(len(CronTriggerFormatter.COLUMNS))),)

        return CronTriggerFormatter.headings(), data


class List(base.MistralLister):
    """List all cron triggers."""

    def _get_format_function(self):
        return CronTriggerFormatter.format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.cron_triggers.list(
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            sort_keys=parsed_args.sort_keys,
            sort_dirs=parsed_args.sort_dirs,
            fields=CronTriggerFormatter.fields(),
            **base.get_filters(parsed_args)
        )


class Get(command.ShowOne):
    """Show specific cron trigger."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('cron_trigger', help='Cron trigger name')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return CronTriggerFormatter.format(mistral_client.cron_triggers.get(
            parsed_args.cron_trigger
        ))


class Create(command.ShowOne):
    """Create new trigger."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument('name', help='Cron trigger name')
        parser.add_argument('workflow_identifier', help='Workflow name or ID')

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
            default=None,
            help=("Date and time of the first execution. Time is treated as "
                  "local time unless --utc is also specified"),
            metavar='<YYYY-MM-DD HH:MM>'
        )
        parser.add_argument(
            '--count',
            type=int,
            help="Number of wanted executions",
            metavar='<integer>'
        )
        parser.add_argument(
            '--utc',
            action='store_true',
            help="All times specified should be treated as UTC"
        )

        return parser

    @staticmethod
    def _get_file_content_or_dict(string):
        if string:
            return utils.load_json(string)
        else:
            return {}

    @staticmethod
    def _convert_time_string_to_utc(time_string):
        datetime_format = '%Y-%m-%d %H:%M'

        the_time = time_string
        if the_time:
            the_time = datetime.datetime.strptime(
                the_time, datetime_format)

            is_dst = time.daylight and time.localtime().tm_isdst > 0
            utc_offset = - (time.altzone if is_dst else time.timezone)

            the_time = (the_time - datetime.timedelta(
                0, utc_offset)).strftime(datetime_format)

        return the_time

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        wf_input = self._get_file_content_or_dict(parsed_args.workflow_input)
        wf_params = self._get_file_content_or_dict(parsed_args.params)

        first_time = parsed_args.first_time
        if not parsed_args.utc:
            first_time = self._convert_time_string_to_utc(
                parsed_args.first_time)

        trigger = mistral_client.cron_triggers.create(
            parsed_args.name,
            parsed_args.workflow_identifier,
            wf_input,
            wf_params,
            parsed_args.pattern,
            first_time,
            parsed_args.count
        )

        return CronTriggerFormatter.format(trigger)


class Delete(command.Command):
    """Delete trigger."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'cron_trigger',
            nargs='+', help='Name of cron trigger(s).'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s: mistral_client.cron_triggers.delete(s),
            parsed_args.cron_trigger,
            "Request to delete cron trigger %s has been accepted.",
            "Unable to delete the specified cron trigger(s)."
        )
