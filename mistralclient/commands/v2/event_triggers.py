# Copyright 2017, OpenStack Foundation
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

from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient import utils


def format_list(trigger=None):
    return format(trigger, lister=True)


def format(trigger=None, lister=False):
    columns = (
        'ID',
        'Name',
        'Workflow ID',
        'Params',
        'Exchange',
        'Topic',
        'Event',
        'Created at',
        'Updated at'
    )

    if trigger:
        data = (
            trigger.id,
            trigger.name,
            trigger.workflow_id,
            trigger.workflow_params,
            trigger.exchange,
            trigger.topic,
            trigger.event,
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
    """List all event triggers."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.event_triggers.list()


class Get(command.ShowOne):
    """Show specific event trigger."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('event_trigger', help='Event trigger ID')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return format(mistral_client.event_triggers.get(
            parsed_args.event_trigger
        ))


class Create(command.ShowOne):
    """Create new trigger."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument('name', help='Event trigger name')
        parser.add_argument('workflow_id', help='Workflow ID')

        parser.add_argument('exchange',
                            type=str,
                            help='Event trigger exchange')

        parser.add_argument('topic',
                            type=str,
                            help='Event trigger topic')

        parser.add_argument('event',
                            type=str,
                            help='Event trigger event name')

        parser.add_argument('workflow_input',
                            nargs='?',
                            help='Workflow input')

        parser.add_argument('--params',
                            help='Workflow params')

        return parser

    @staticmethod
    def _get_json_string_or_dict(string):
        if string:
            return utils.load_json(string)
        else:
            return {}

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        wf_input = self._get_json_string_or_dict(parsed_args.workflow_input)
        wf_params = self._get_json_string_or_dict(parsed_args.params)

        trigger = mistral_client.event_triggers.create(
            parsed_args.name,
            parsed_args.workflow_id,
            parsed_args.exchange,
            parsed_args.topic,
            parsed_args.event,
            wf_input,
            wf_params,
        )

        return format(trigger)


class Delete(command.Command):
    """Delete trigger."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'event_trigger_id',
            nargs='+', help='ID of event trigger(s).'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s: mistral_client.event_triggers.delete(s),
            parsed_args.event_trigger_id,
            "Request to delete event trigger %s has been accepted.",
            "Unable to delete the specified event trigger(s)."
        )
