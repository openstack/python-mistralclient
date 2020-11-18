# Copyright 2020 Nokia Software.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse

from cliff import show
from osc_lib.command import command

from mistralclient.commands.v2 import base
from mistralclient import utils


class CodeSourceFormatter(base.MistralFormatter):
    COLUMNS = [
        ('id', 'ID'),
        ('name', 'Name'),
        ('namespace', 'Namespace'),
        ('project_id', 'Project ID'),
        ('scope', 'Scope'),
        ('created_at', 'Created at'),
        ('updated_at', 'Updated at')
    ]

    @staticmethod
    def format(code_src=None, lister=False):
        if code_src:
            data = (
                code_src.id,
                code_src.name,
                code_src.namespace,
                code_src.project_id,
                code_src.scope,
                code_src.created_at
            )

            if hasattr(code_src, 'updated_at'):
                data += (code_src.updated_at,)
            else:
                data += (None,)
        else:
            data = (('',) * len(CodeSourceFormatter.COLUMNS),)

        return CodeSourceFormatter.headings(), data


class List(base.MistralLister):
    """List all workflows."""

    def _get_format_function(self):
        return CodeSourceFormatter.format_list

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        return parser

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        return mistral_client.code_sources.list(
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            sort_keys=parsed_args.sort_keys,
            sort_dirs=parsed_args.sort_dirs,
            fields=CodeSourceFormatter.fields(),
            **base.get_filters(parsed_args)
        )


class Get(show.ShowOne):
    """Show specific code source."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument('identifier', help='Code source ID or name.')
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to get the code source from.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        wf = mistral_client.code_sources.get(
            parsed_args.identifier,
            parsed_args.namespace
        )

        return CodeSourceFormatter.format(wf)


class Create(command.ShowOne):
    """Create new code source."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument('name', help='Code source name.')
        parser.add_argument(
            'content',
            type=argparse.FileType('r'),
            help='Code source content file.'
        )
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to create the code source within.",
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag the code source will be marked as "public".'
        )

        return parser

    def take_action(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        code_source = mistral_client.code_sources.create(
            parsed_args.name,
            parsed_args.content.read(),
            namespace=parsed_args.namespace,
            scope=scope
        )

        return CodeSourceFormatter.format(code_source)


class Delete(command.Command):
    """Delete workflow."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'identifier',
            nargs='+',
            help='Code source name or ID (can be repeated multiple times).'
        )

        parser.add_argument(
            '--namespace',
            nargs='?',
            default=None,
            help="Namespace to delete the code source(s) from.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        utils.do_action_on_many(
            lambda s:
                mistral_client.code_sources.delete(s, parsed_args.namespace),
            parsed_args.identifier,
            "Request to delete code source '%s' has been accepted.",
            "Unable to delete the specified code source(s)."
        )


class Update(command.ShowOne):
    """Update workflow."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'identifier',
            help='Code source identifier (name or ID).'
        )
        parser.add_argument(
            'content',
            type=argparse.FileType('r'),
            help='Code source content'
        )
        parser.add_argument('--id', help='Workflow ID.')
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace of the workflow.",
        )
        parser.add_argument(
            '--public',
            action='store_true',
            help='With this flag workflow will be marked as "public".'
        )

        return parser

    def take_action(self, parsed_args):
        scope = 'public' if parsed_args.public else 'private'

        mistral_client = self.app.client_manager.workflow_engine

        code_src = mistral_client.code_sources.update(
            parsed_args.identifier,
            parsed_args.content.read(),
            namespace=parsed_args.namespace,
            scope=scope
        )

        return CodeSourceFormatter.format(code_src)


class GetContent(command.Command):
    """Show workflow definition."""

    def get_parser(self, prog_name):
        parser = super(GetContent, self).get_parser(prog_name)

        parser.add_argument('identifier', help='Code source ID or name.')
        parser.add_argument(
            '--namespace',
            nargs='?',
            default='',
            help="Namespace to get the code source from.",
        )

        return parser

    def take_action(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine

        code_src = mistral_client.code_sources.get(
            parsed_args.identifier,
            parsed_args.namespace
        )

        self.app.stdout.write(code_src.content or "\n")
