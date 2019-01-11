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

from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient import exceptions


class MemberFormatter(base.MistralFormatter):
    COLUMNS = [
        ('resource_id', 'Resource ID'),
        ('resource_type', 'Resource Type'),
        ('project_id', 'Resource Owner'),
        ('member_id', 'Member ID'),
        ('status', 'Status'),
        ('created_at', 'Created at'),
        ('updated_at', 'Updated at')
    ]

    @staticmethod
    def format(member=None, lister=False):
        if member:
            data = (
                member.resource_id,
                member.resource_type,
                member.project_id,
                member.member_id,
                member.status,
                member.created_at,
            )

            if hasattr(member, 'updated_at'):
                data += (member.updated_at,)
            else:
                data += (None,)
        else:
            data = (tuple('' for _ in range(len(MemberFormatter.COLUMNS))),)

        return MemberFormatter.headings(), data


class List(base.MistralLister):
    """List all members."""

    def _get_format_function(self):
        return MemberFormatter.format_list

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


class Get(command.ShowOne):
    """Show specific member information."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'resource',
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
            parsed_args.resource,
            parsed_args.resource_type,
            parsed_args.member_id,
        )

        return MemberFormatter.format(member)


class Create(command.ShowOne):
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

        return MemberFormatter.format(member)


class Delete(command.Command):
    """Delete a resource sharing relationship."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'resource',
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
                parsed_args.resource,
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


class Update(command.ShowOne):
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

        return MemberFormatter.format(member)
