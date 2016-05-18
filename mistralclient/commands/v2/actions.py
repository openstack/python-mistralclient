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

import argparse
import logging

from cliff import command
from cliff import show

from mistralclient.commands.v2 import base
from mistralclient import utils

LOG = logging.getLogger(__name__)


def format_list(action=None):
    return format(action, lister=True)


def format(action=None, lister=False):
    columns = (
        'Name',
        'Is system',
        'Input',
        'Description',
        'Tags',
        'Created at',
        'Updated at'
    )

    if action:
        tags = getattr(action, 'tags', None) or []
        input = action.input if not lister else base.cut(action.input)
        desc = (action.description if not lister
                else base.cut(action.description))

        data = (
            action.name,
            action.is_system,
            input,
            desc,
            base.wrap(', '.join(tags)) or '<none>',
            action.created_at,
        )

        if hasattr(action, 'updated_at'):
            data += (action.updated_at,)
        else:
            data += (None,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all actions."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.actions.list()


class Get(show.ShowOne):
    """Show specific action."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        action = mistral_client.actions.get(parsed_args.name)

        return format(action)


class Create(base.MistralLister):
    """Create new action."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Action definition file'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag action will be marked as "public".'
        )

        return parser

    def _validate_parsed_args(self, parsed_args):
        if not parsed_args.definition:
            raise RuntimeError("Provide action definition file.")

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.actions.create(
            parsed_args.definition.read(),
            scope=scope
        )


class Delete(command.Command):
    """Delete action."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', nargs='+', help='Name of action(s).')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s: mistral_client.actions.delete(s),
            parsed_args.name,
            "Request to delete action %s has been accepted.",
            "Unable to delete the specified action(s)."
        )


class Update(base.MistralLister):
    """Update action."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Action definition file'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag action will be marked as "public".'
        )

        return parser

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.actions.update(
            parsed_args.definition.read(),
            scope=scope
        )


class GetDefinition(command.Command):
    """Show action definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        definition = mistral_client.actions.get(parsed_args.name).definition

        self.app.stdout.write(definition or "\n")


class Validate(show.ShowOne):
    """Validate action."""

    def _format(self, result=None):
        columns = ('Valid', 'Error')

        if result:
            data = (result.get('valid'), result.get('error'))
        else:
            data = (tuple('<none>' for _ in range(len(columns))),)

        return columns, data

    def get_parser(self, prog_name):
        parser = super(Validate, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='action definition file'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        result = mistral_client.actions.validate(
            parsed_args.definition.read()
        )

        return self._format(result)
