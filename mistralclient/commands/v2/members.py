# Copyright 2016 - Catalyst IT Limited
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

from cliff import command
from cliff import show

from mistralclient.commands.v2 import base
from mistralclient import exceptions


def format_list(member=None):
    return format(member, lister=True)


def format(member=None, lister=False):
    columns = (
        'Resource ID',
        'Resource Type',
        'Resource Owner',
        'Member ID',
        'Status',
        'Created at',
        'Updated at'
    )

    if member:
        data = (
            member.resource_id,
            member.resource_type,
            member.project_id,
            member.member_id,
            member.status,
            member.created_at,
            member.updated_at or '<none>'
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all members."""

    def _get_format_function(self):
        return format_list

    def get_parser(self, parsed_args):
        parser = super(List, self).get_parser(parsed_args)

        parser.add_argument(
            'resource_id',
            help='Resource id to be shared.'
        )
        parser.add_argument(
            'resource_type',
            help='Resource type.'
        )

        return parser

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.members.list(
            parsed_args.resource_id,
            parsed_args.resource_type
        )


class Get(show.ShowOne):
    """Show specific member information."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'resource_id',
            help='Resource ID to be shared.'
        )
        parser.add_argument(
            'resource_type',
            help='Resource type.'
        )
        parser.add_argument(
            '-m',
            '--member-id',
            default='',
            help='Project ID to whom the resource is shared to. No need to '
                 'provide this param if you are the resource member.'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        member = mistral_client.members.get(
            parsed_args.resource_id,
            parsed_args.resource_type,
            parsed_args.member_id,
        )

        return format(member)


class Create(show.ShowOne):
    """Shares a resource to another tenant."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'resource_id',
            help='Resource ID to be shared.'
        )
        parser.add_argument(
            'resource_type',
            help='Resource type.'
        )
        parser.add_argument(
            'member_id',
            help='Project ID to whom the resource is shared to.'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        member = mistral_client.members.create(
            parsed_args.resource_id,
            parsed_args.resource_type,
            parsed_args.member_id,
        )

        return format(member)


class Delete(command.Command):
    """Delete a resource sharing relationship."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'resource_id',
            help='Resource ID to be shared.'
        )
        parser.add_argument(
            'resource_type',
            help='Resource type.'
        )
        parser.add_argument(
            'member_id',
            help='Project ID to whom the resource is shared to.'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        try:
            mistral_client.members.delete(
                parsed_args.resource_id,
                parsed_args.resource_type,
                parsed_args.member_id,
            )

            print(
                "Request to delete %s member %s has been accepted." %
                (parsed_args.resource_type, parsed_args.member_id)
            )
        except Exception as e:
            print(e)

            error_msg = "Unable to delete the specified member."
            raise exceptions.MistralClientException(error_msg)


class Update(show.ShowOne):
    """Update resource sharing status."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'resource_id',
            help='Resource ID to be shared.'
        )
        parser.add_argument(
            'resource_type',
            help='Resource type.'
        )
        parser.add_argument(
            '-m',
            '--member-id',
            default='',
            help='Project ID to whom the resource is shared to. No need to '
                 'provide this param if you are the resource member.'
        )
        parser.add_argument(
            '-s',
            '--status',
            default='accepted',
            choices=['pending', 'accepted', 'rejected'],
            help='status of the sharing.'
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        member = mistral_client.members.update(
            parsed_args.resource_id,
            parsed_args.resource_type,
            parsed_args.member_id,
            status=parsed_args.status
        )

        return format(member)
