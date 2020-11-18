# Copyright 2020 Nokia Software.
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


class DynamicActionFormatter(base.MistralFormatter):
    COLUMNS = [
        ('id', 'ID'),
        ('name', 'Name'),
        ('class_name', 'Class'),
        ('code_source_id', 'Code source ID'),
        ('code_source_name', 'Code source name'),
        ('project_id', 'Project ID'),
        ('scope', 'Scope'),
        ('created_at', 'Created at'),
        ('updated_at', 'Updated at'),
    ]

    @staticmethod
    def format(action=None, lister=False):
        if action:
            data = (
                action.id,
                action.name,
                action.class_name,
                action.code_source_id,
                action.code_source_name,
                action.project_id,
                action.scope,
                action.created_at
            )

            if hasattr(action, 'updated_at'):
                data += (action.updated_at,)
            else:
                data += (None,)

        else:
            data = (('',)*len(DynamicActionFormatter.COLUMNS),)

        return DynamicActionFormatter.headings(), data


class List(base.MistralLister):
    """List all dynamic actions."""

    def _get_format_function(self):
        return DynamicActionFormatter.format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace of dynamic actions.",
        )

        return parser

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.dynamic_actions.list(
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            sort_keys=parsed_args.sort_keys,
            sort_dirs=parsed_args.sort_dirs,
            fields=DynamicActionFormatter.fields(),
            namespace=parsed_args.namespace,
            **base.get_filters(parsed_args)
        )


class Get(command.ShowOne):
    """Show specific dynamic action."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'identifier',
            help='Dynamic action identifier (name or ID)'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to create the dynamic action within.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        action = mistral_client.dynamic_actions.get(
            parsed_args.identifier,
            parsed_args.namespace
        )

        return DynamicActionFormatter.format(action)


class Create(command.ShowOne):
    """Create new action."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument('name', help='Dynamic action name')
        parser.add_argument('class_name', help='Dynamic action class name')
        parser.add_argument('code_source', help='Code source ID or name')
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag an action will be marked as "public".'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to create the action within.",
        )

        return parser

    def take_action(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        dyn_action = mistral_client.dynamic_actions.create(
            parsed_args.name,
            parsed_args.class_name,
            parsed_args.code_source,
            namespace=parsed_args.namespace,
            scope=scope
        )

        return DynamicActionFormatter.format(dyn_action)


class Delete(command.Command):
    """Delete action."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'identifier',
            nargs='+',
            help="Dynamic action name or ID (can be repeated multiple times)."
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace of the dynamic action(s).",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s: mistral_client.dynamic_actions.delete(
                s,
                namespace=parsed_args.namespace
            ),
            parsed_args.identifier,
            "Request to delete dynamic action(s) %s has been accepted.",
            "Unable to delete the specified dynamic action(s)."
        )


class Update(command.ShowOne):
    """Update dynamic action."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'identifier',
            help='Dynamic action identifier (ID or name)'
        )
        parser.add_argument(
            '--class-name',
            dest='class_name',
            nargs='?',
            help='Dynamic action class name.'
        )
        parser.add_argument(
            '--code-source',
            dest='code_source',
            nargs='?',
            help='Code source identifier (ID or name).'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag action will be marked as "public".'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace of the action.",
        )

        return parser

    def take_action(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        dyn_action = mistral_client.dynamic_actions.update(
            parsed_args.identifier,
            class_name=parsed_args.class_name,
            code_source=parsed_args.code_source,
            scope=scope,
            namespace=parsed_args.namespace
        )

        return DynamicActionFormatter.format(dyn_action)
