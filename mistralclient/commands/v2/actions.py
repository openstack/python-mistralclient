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
from cliff import lister
from cliff import show

from mistralclient.api.v2 import actions

LOG = logging.getLogger(__name__)


def format(action=None):
    columns = (
        'Name',
        'Description',
        'Created at',
        'Updated at'
    )

    if action:
        data = (
            action.name,
            getattr(action, 'description', '<none>'),
            action.created_at,
        )

        if hasattr(action, 'updated_at'):
            data += (action.updated_at,)
        else:
            data += (None,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(lister.Lister):
    """List all actions."""

    def take_action(self, parsed_args):
        data = [
            format(action)[1] for action
            in actions.ActionManager(self.app.client).list()
        ]

        if data:
            return format()[0], data
        else:
            return format()


class Get(show.ShowOne):
    """Show specific action."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')

        return parser

    def take_action(self, parsed_args):
        action = actions.ActionManager(self.app.client).get(
            parsed_args.name)

        return format(action)


class Create(show.ShowOne):
    """Create new action."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')
        parser.add_argument(
            'definition',
            nargs='?',
            type=argparse.FileType('r'),
            help='Action definition file'
        )

        return parser

    def take_action(self, parsed_args):
        if not parsed_args.definition:
            raise RuntimeError("You must provide path to action "
                               "definition file.")

        action = actions.ActionManager(self.app.client)\
            .create(parsed_args.name,
                    parsed_args.definition.read())

        return format(action)


class Delete(command.Command):
    """Delete action."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')

        return parser

    def take_action(self, parsed_args):
        actions.ActionManager(self.app.client).delete(parsed_args.name)


class Update(show.ShowOne):
    """Update action."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')
        parser.add_argument(
            'definition',
            nargs='?',
            type=argparse.FileType('r'),
            help='Action definition file'
        )

        return parser

    def take_action(self, parsed_args):
        action = actions.ActionManager(self.app.client)\
            .update(parsed_args.name,
                    parsed_args.definition.read())

        return format(action)


class UploadDefinition(command.Command):
    """Upload action definition."""

    def get_parser(self, prog_name):
        parser = super(UploadDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')
        parser.add_argument(
            'path',
            type=argparse.FileType('r'),
            help='Action definition file'
        )

        return parser

    def take_action(self, parsed_args):
        action = actions.ActionManager(self.app.client)\
            .update(parsed_args.name,
                    definition=parsed_args.path.read())

        self.app.stdout.write(action.definition or "\n")


class GetDefinition(command.Command):
    """Show action definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='Action name')

        return parser

    def take_action(self, parsed_args):
        definition = actions.ActionManager(self.app.client)\
            .get(parsed_args.name).definition

        self.app.stdout.write(definition or "\n")
