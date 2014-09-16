# Copyright 2014 StackStorm, Inc.
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

"""
Command-line interface to the Mistral APIs
"""

import logging
import sys

from mistralclient.openstack.common.cliutils import env

from mistralclient.api import client

import mistralclient.commands.v1.workbooks
import mistralclient.commands.v1.executions
import mistralclient.commands.v1.tasks
import mistralclient.commands.v2.workbooks
import mistralclient.commands.v2.workflows
import mistralclient.commands.v2.executions
import mistralclient.commands.v2.tasks

from cliff import app
from cliff import help
from cliff import commandmanager

import argparse

LOG = logging.getLogger(__name__)


class MistralShell(app.App):

    def __init__(self):
        super(MistralShell, self).__init__(
            description=__doc__.strip(),
            version='0.1',
            command_manager=commandmanager.CommandManager('mistral.cli'),
        )

        # Set v2 commands by default
        self._set_shell_commands(self._get_commands_v2())

    def configure_logging(self):
        super(MistralShell, self).configure_logging()
        logging.getLogger('iso8601').setLevel(logging.WARNING)
        if self.options.verbose_level <= 1:
            logging.getLogger('requests').setLevel(logging.WARNING)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            help='Show program\'s version number and exit.'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '-h', '--help',
            action=help.HelpAction,
            nargs=0,
            default=self,  # tricky
            help="Show this help message and exit.",
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )
        parser.add_argument(
            '--os-mistral-url',
            action='store',
            dest='mistral_url',
            default=env('OS_MISTRAL_URL', default='http://localhost:8989/v2'),
            help='Mistral API host (Env: OS_MISTRAL_URL)'
        )
        parser.add_argument(
            '--os-username',
            action='store',
            dest='username',
            default=env('OS_USERNAME', default='admin'),
            help='Authentication username (Env: OS_USERNAME)'
        )
        parser.add_argument(
            '--os-password',
            action='store',
            dest='password',
            default=env('OS_PASSWORD', default='openstack'),
            help='Authentication password (Env: OS_PASSWORD)'
        )
        parser.add_argument(
            '--os-tenant-id',
            action='store',
            dest='tenant_id',
            default=env('OS_TENANT_ID'),
            help='Authentication tenant identifier (Env: OS_TENANT_ID)'
        )
        parser.add_argument(
            '--os-tenant-name',
            action='store',
            dest='tenant_name',
            default=env('OS_TENANT_NAME', 'Default'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)'
        )
        parser.add_argument(
            '--os-auth-token',
            action='store',
            dest='token',
            default=env('OS_AUTH_TOKEN'),
            help='Authentication token (Env: OS_AUTH_TOKEN)'
        )
        parser.add_argument(
            '--os-auth-url',
            action='store',
            dest='auth_url',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)'
        )
        return parser

    def initialize_app(self, argv):
        self._clear_shell_commands()
        self._set_shell_commands(self._get_commands(
            client.determine_client_version(self.options.mistral_url)))

        self.client = client.client(mistral_url=self.options.mistral_url,
                                    username=self.options.username,
                                    api_key=self.options.password,
                                    project_name=self.options.tenant_name,
                                    auth_url=self.options.auth_url,
                                    project_id=self.options.tenant_id,
                                    endpoint_type='publicURL',
                                    service_type='workflow',
                                    auth_token=self.options.token)

    def _set_shell_commands(self, cmds_dict):
        for k, v in cmds_dict.items():
            self.command_manager.add_command(k, v)

    def _clear_shell_commands(self):
        exclude_cmds = ['help', 'complete']

        cmds = self.command_manager.commands.copy()
        for k, v in cmds.items():
            if k not in exclude_cmds:
                self.command_manager.commands.pop(k)

    def _get_commands(self, version):
        if version == 1:
            return self._get_commands_v1()
        else:
            return self._get_commands_v2()

    def _get_commands_v1(self):
        return {
            'workbook-list': mistralclient.commands.v1.workbooks.List,
            'workbook-get': mistralclient.commands.v1.workbooks.Get,
            'workbook-create': mistralclient.commands.v1.workbooks.Create,
            'workbook-delete': mistralclient.commands.v1.workbooks.Delete,
            'workbook-update': mistralclient.commands.v1.workbooks.Update,
            'workbook-upload-definition':
            mistralclient.commands.v1.workbooks.UploadDefinition,
            'workbook-get-definition':
            mistralclient.commands.v1.workbooks.GetDefinition,
            'execution-list': mistralclient.commands.v1.executions.List,
            'execution-get': mistralclient.commands.v1.executions.Get,
            'execution-create': mistralclient.commands.v1.executions.Create,
            'execution-delete': mistralclient.commands.v1.executions.Delete,
            'execution-update': mistralclient.commands.v1.executions.Update,
            'task-list': mistralclient.commands.v1.tasks.List,
            'task-get': mistralclient.commands.v1.tasks.Get,
            'task-update': mistralclient.commands.v1.tasks.Update,
        }

    def _get_commands_v2(self):
        return {
            'workbook-list': mistralclient.commands.v2.workbooks.List,
            'workbook-get': mistralclient.commands.v2.workbooks.Get,
            'workbook-create': mistralclient.commands.v2.workbooks.Create,
            'workbook-delete': mistralclient.commands.v2.workbooks.Delete,
            'workbook-update': mistralclient.commands.v2.workbooks.Update,
            'workbook-upload-definition':
            mistralclient.commands.v2.workbooks.UploadDefinition,
            'workbook-get-definition':
            mistralclient.commands.v2.workbooks.GetDefinition,
            'execution-list': mistralclient.commands.v2.executions.List,
            'execution-get': mistralclient.commands.v2.executions.Get,
            'execution-get-input':
            mistralclient.commands.v2.executions.GetInput,
            'execution-get-output':
            mistralclient.commands.v2.executions.GetOutput,
            'execution-create': mistralclient.commands.v2.executions.Create,
            'execution-delete': mistralclient.commands.v2.executions.Delete,
            'execution-update': mistralclient.commands.v2.executions.Update,
            'task-list': mistralclient.commands.v2.tasks.List,
            'task-get': mistralclient.commands.v2.tasks.Get,
            'task-get-output': mistralclient.commands.v2.tasks.GetOutput,
            'task-get-parameters':
            mistralclient.commands.v2.tasks.GetParameters,
            'task-get-result': mistralclient.commands.v2.tasks.GetResult,
            'task-update': mistralclient.commands.v2.tasks.Update,
            'workflow-list': mistralclient.commands.v2.workflows.List,
            'workflow-get': mistralclient.commands.v2.workflows.Get,
            'workflow-create': mistralclient.commands.v2.workflows.Create,
            'workflow-delete': mistralclient.commands.v2.workflows.Delete,
            'workflow-update': mistralclient.commands.v2.workflows.Update,
            'workflow-upload-definition':
            mistralclient.commands.v2.workflows.UploadDefinition,
            'workflow-get-definition':
            mistralclient.commands.v2.workflows.GetDefinition
        }


def main(argv=sys.argv[1:]):
    return MistralShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
