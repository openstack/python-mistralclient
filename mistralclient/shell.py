# Copyright 2015 - StackStorm, Inc.
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

"""
Command-line interface to the Mistral APIs
"""

import argparse
import logging
import os
import sys

from cliff import app
from cliff import commandmanager
from osc_lib.command import command

from mistralclient.api import client
from mistralclient.auth import auth_types
import mistralclient.commands.v2.action_executions
import mistralclient.commands.v2.actions
import mistralclient.commands.v2.cron_triggers
import mistralclient.commands.v2.environments
import mistralclient.commands.v2.event_triggers
import mistralclient.commands.v2.executions
import mistralclient.commands.v2.members
import mistralclient.commands.v2.services
import mistralclient.commands.v2.tasks
import mistralclient.commands.v2.workbooks
import mistralclient.commands.v2.workflows
from mistralclient import exceptions as exe


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


class OpenStackHelpFormatter(argparse.HelpFormatter):

    def __init__(self, prog, indent_increment=2, max_help_position=32,
                 width=None):
        super(OpenStackHelpFormatter, self).__init__(
            prog,
            indent_increment,
            max_help_position,
            width
        )

    def start_section(self, heading):
        # Title-case the headings.
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


class HelpAction(argparse.Action):
    """Custom help action.

    Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v2 :\n')

        for name, ep in sorted(app.command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)

        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))

        sys.exit(0)


class BashCompletionCommand(command.Command):
    """Prints all of the commands and options for bash-completion."""

    def take_action(self, parsed_args):
        commands = set()
        options = set()

        for option, _action in self.app.parser._option_string_actions.items():
            options.add(option)

        for command_name, _cmd in self.app.command_manager:
            commands.add(command_name)

        print(' '.join(commands | options))


class MistralShell(app.App):

    def __init__(self):
        super(MistralShell, self).__init__(
            description=__doc__.strip(),
            version=mistralclient.__version__,
            command_manager=commandmanager.CommandManager('mistral.cli'),
        )

        # Set v2 commands by default
        self._set_shell_commands(self._get_commands_v2())

    def configure_logging(self):
        log_lvl = logging.DEBUG if self.options.debug else logging.WARNING
        logging.basicConfig(
            format="%(levelname)s (%(module)s) %(message)s",
            level=log_lvl
        )
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
            formatter_class=OpenStackHelpFormatter,
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
            action=HelpAction,
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
            default=env('OS_MISTRAL_URL'),
            help='Mistral API host (Env: OS_MISTRAL_URL)'
        )

        parser.add_argument(
            '--os-mistral-version',
            action='store',
            dest='mistral_version',
            default=env('OS_MISTRAL_VERSION', default='v2'),
            help='Mistral API version (default = v2) (Env: '
                 'OS_MISTRAL_VERSION)'
        )

        parser.add_argument(
            '--os-mistral-service-type',
            action='store',
            dest='service_type',
            default=env('OS_MISTRAL_SERVICE_TYPE', default='workflowv2'),
            help='Mistral service-type (should be the same name as in '
                 'keystone-endpoint) (default = workflowv2) (Env: '
                 'OS_MISTRAL_SERVICE_TYPE)'
        )

        parser.add_argument(
            '--os-mistral-endpoint-type',
            action='store',
            dest='endpoint_type',
            default=env('OS_MISTRAL_ENDPOINT_TYPE', default='publicURL'),
            help='Mistral endpoint-type (should be the same name as in '
                 'keystone-endpoint) (default = publicURL) (Env: '
                 'OS_MISTRAL_ENDPOINT_TYPE)'
        )

        parser.add_argument(
            '--os-username',
            action='store',
            dest='username',
            default=env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)'
        )

        parser.add_argument(
            '--os-password',
            action='store',
            dest='password',
            default=env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)'
        )

        parser.add_argument(
            '--os-tenant-id',
            action='store',
            dest='tenant_id',
            default=env('OS_TENANT_ID', 'OS_PROJECT_ID'),
            help='Authentication tenant identifier (Env: OS_TENANT_ID'
                 ' or OS_PROJECT_ID)'
        )

        parser.add_argument(
            '--os-project-id',
            action='store',
            dest='project_id',
            default=env('OS_TENANT_ID', 'OS_PROJECT_ID'),
            help='Authentication project identifier (Env: OS_TENANT_ID'
                 ' or OS_PROJECT_ID), will use tenant_id if both tenant_id'
                 ' and project_id are set'
        )

        parser.add_argument(
            '--os-tenant-name',
            action='store',
            dest='tenant_name',
            default=env('OS_TENANT_NAME', 'OS_PROJECT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME'
                 ' or OS_PROJECT_NAME)'
        )

        parser.add_argument(
            '--os-project-name',
            action='store',
            dest='project_name',
            default=env('OS_TENANT_NAME', 'OS_PROJECT_NAME'),
            help='Authentication project name (Env: OS_TENANT_NAME'
                 ' or OS_PROJECT_NAME), will use tenant_name if both'
                 ' tenant_name and project_name are set'
        )

        parser.add_argument(
            '--os-auth-token',
            action='store',
            dest='token',
            default=env('OS_AUTH_TOKEN'),
            help='Authentication token (Env: OS_AUTH_TOKEN)'
        )

        parser.add_argument(
            '--os-project-domain-name',
            action='store',
            dest='project_domain_name',
            default=env('OS_PROJECT_DOMAIN_NAME'),
            help='Authentication project domain name or ID'
                 ' (Env: OS_PROJECT_DOMAIN_NAME or OS_PROJECT_DOMAIN_NAME)'
        )

        parser.add_argument(
            '--os-project-domain-id',
            action='store',
            dest='project_domain_id',
            default=env('OS_PROJECT_DOMAIN_ID'),
            help='Authentication project domain ID'
                 ' (Env: OS_PROJECT_DOMAIN_ID)'
        )

        parser.add_argument(
            '--os-user-domain-name',
            action='store',
            dest='user_domain_name',
            default=env('OS_USER_DOMAIN_NAME'),
            help='Authentication user domain name'
                 ' (Env: OS_USER_DOMAIN_NAME)'
        )

        parser.add_argument(
            '--os-user-domain-id',
            action='store',
            dest='user_domain_id',
            default=env('OS_USER_DOMAIN_ID'),
            help='Authentication user domain name'
                 ' (Env: OS_USER_DOMAIN_ID)'
        )

        parser.add_argument(
            '--os-auth-url',
            action='store',
            dest='auth_url',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)'
        )

        parser.add_argument(
            '--os-cert',
            action='store',
            dest='os_cert',
            default=env('OS_CERT'),
            help='Client Certificate (Env: OS_CERT)'
        )

        parser.add_argument(
            '--os-key',
            action='store',
            dest='os_key',
            default=env('OS_KEY'),
            help='Client Key (Env: OS_KEY)'
        )

        parser.add_argument(
            '--os-cacert',
            action='store',
            dest='os_cacert',
            default=env('OS_CACERT'),
            help='Authentication CA Certificate (Env: OS_CACERT)'
        )

        parser.add_argument(
            '--os-region-name',
            action='store',
            dest='region_name',
            default=env('OS_REGION_NAME'),
            help='Region name (Env: OS_REGION_NAME)'
        )

        parser.add_argument(
            '--insecure',
            action='store_true',
            dest='insecure',
            default=env('MISTRALCLIENT_INSECURE', default=False),
            help='Disables SSL/TLS certificate verification '
                 '(Env: MISTRALCLIENT_INSECURE)'
        )

        parser.add_argument(
            '--auth-type',
            action='store',
            dest='auth_type',
            default=env('MISTRAL_AUTH_TYPE', default='keystone'),
            help='Authentication type. Valid options are: %s.'
                 ' (Env: MISTRAL_AUTH_TYPE)' % ', '.join(auth_types.ALL)
        )

        parser.add_argument(
            '--openid-client-id',
            action='store',
            dest='client_id',
            default=env('OPENID_CLIENT_ID'),
            help='Client ID (according to OpenID Connect).'
                 ' (Env: OPENID_CLIENT_ID)'
        )

        parser.add_argument(
            '--openid-client-secret',
            action='store',
            dest='client_secret',
            default=env('OPENID_CLIENT_SECRET'),
            help='Client secret (according to OpenID Connect)'
                 ' (Env: OPENID_CLIENT_SECRET)'
        )

        parser.add_argument(
            '--os-target-username',
            action='store',
            dest='target_username',
            default=env('OS_TARGET_USERNAME', default='admin'),
            help='Authentication username for target cloud'
                 ' (Env: OS_TARGET_USERNAME)'
        )

        parser.add_argument(
            '--os-target-password',
            action='store',
            dest='target_password',
            default=env('OS_TARGET_PASSWORD'),
            help='Authentication password for target cloud'
                 ' (Env: OS_TARGET_PASSWORD)'
        )

        parser.add_argument(
            '--os-target-tenant-id',
            action='store',
            dest='target_tenant_id',
            default=env('OS_TARGET_TENANT_ID'),
            help='Authentication tenant identifier for target cloud'
                 ' (Env: OS_TARGET_TENANT_ID)'
        )

        parser.add_argument(
            '--os-target-tenant-name',
            action='store',
            dest='target_tenant_name',
            default=env('OS_TARGET_TENANT_NAME'),
            help='Authentication tenant name for target cloud'
                 ' (Env: OS_TARGET_TENANT_NAME)'
        )

        parser.add_argument(
            '--os-target-auth-token',
            action='store',
            dest='target_token',
            default=env('OS_TARGET_AUTH_TOKEN'),
            help='Authentication token for target cloud'
                 ' (Env: OS_TARGET_AUTH_TOKEN)'
        )

        parser.add_argument(
            '--os-target-auth-url',
            action='store',
            dest='target_auth_url',
            default=env('OS_TARGET_AUTH_URL'),
            help='Authentication URL for target cloud'
                 ' (Env: OS_TARGET_AUTH_URL)'
        )

        parser.add_argument(
            '--os-target_cacert',
            action='store',
            dest='target_cacert',
            default=env('OS_TARGET_CACERT'),
            help='Authentication CA Certificate for target cloud'
                 ' (Env: OS_TARGET_CACERT)'
        )

        parser.add_argument(
            '--os-target-region-name',
            action='store',
            dest='target_region_name',
            default=env('OS_TARGET_REGION_NAME'),
            help='Region name for target cloud'
                 '(Env: OS_TARGET_REGION_NAME)'
        )

        parser.add_argument(
            '--os-target-user-domain-name',
            action='store',
            dest='target_user_domain_name',
            default=env('OS_TARGET_USER_DOMAIN_NAME'),
            help='User domain name for target cloud'
                 '(Env: OS_TARGET_USER_DOMAIN_NAME)'
        )

        parser.add_argument(
            '--os-target-user-domain-id',
            action='store',
            dest='target_user_domain_id',
            default=env('OS_TARGET_USER_DOMAIN_ID'),
            help='User domain ID for target cloud'
                 '(Env: OS_TARGET_USER_DOMAIN_ID)'
        )

        parser.add_argument(
            '--os-target-project-domain-name',
            action='store',
            dest='target_project_domain_name',
            default=env('OS_TARGET_PROJECT_DOMAIN_NAME'),
            help='Project domain name for target cloud'
                 '(Env: OS_TARGET_PROJECT_DOMAIN_NAME)'
        )

        parser.add_argument(
            '--os-target-project-domain-id',
            action='store',
            dest='target_project_domain_id',
            default=env('OS_TARGET_PROJECT_DOMAIN_ID'),
            help='Project domain ID for target cloud'
                 '(Env: OS_TARGET_PROJECT_DOMAIN_ID)'
        )

        parser.add_argument(
            '--target_insecure',
            action='store_true',
            dest='target_insecure',
            default=env('TARGET_MISTRALCLIENT_INSECURE', default=False),
            help='Disables SSL/TLS certificate verification for target cloud '
                 '(Env: TARGET_MISTRALCLIENT_INSECURE)'
        )

        parser.add_argument(
            '--profile',
            dest='profile',
            metavar='HMAC_KEY',
            default=env('OS_PROFILE'),
            help='HMAC key to use for encrypting context data for performance '
                 'profiling of operation. This key should be one of the '
                 'values configured for the osprofiler middleware in mistral, '
                 'it is specified in the profiler section of the mistral '
                 'configuration (i.e. /etc/mistral/mistral.conf). Without the '
                 'key, profiling will not be triggered even if osprofiler is '
                 'enabled on the server side.'
        )

        return parser

    def initialize_app(self, argv):
        self._clear_shell_commands()

        ver = client.determine_client_version(self.options.mistral_version)

        self._set_shell_commands(self._get_commands(ver))

        # bash-completion and help messages should not require client creation
        need_client = not (
            ('bash-completion' in argv) or
            ('help' in argv) or
            ('-h' in argv) or
            ('--help' in argv) or
            not argv)

        # Set default for auth_url if not supplied. The default is not
        # set at the parser to support use cases where auth is not enabled.
        # An example use case would be a developer's environment.
        if not self.options.auth_url:
            if self.options.password or self.options.token:
                self.options.auth_url = 'http://localhost:35357/v3'

        if (self.options.auth_type == 'keystone' and
                not self.options.auth_url.endswith("/v2.0")):
            # Assume that keystone V3 is used and try to be more user-friendly,
            # i.e provide default values for domains
            if (not self.options.project_domain_id and
                    not self.options.project_domain_name):
                self.options.project_domain_id = "default"
            if (not self.options.user_domain_id and
                    not self.options.user_domain_name):
                self.options.user_domain_id = "default"
            if (not self.options.target_project_domain_id and
                    not self.options.target_project_domain_name):
                self.options.target_project_domain_id = "default"
            if (not self.options.target_user_domain_id and
                    not self.options.target_user_domain_name):
                self.options.target_user_domain_id = "default"

        if self.options.auth_url and not self.options.token:
            if not self.options.username:
                raise exe.IllegalArgumentException(
                    ("You must provide a username "
                     "via --os-username env[OS_USERNAME]")
                )

            if not self.options.password:
                raise exe.IllegalArgumentException(
                    ("You must provide a password "
                     "via --os-password env[OS_PASSWORD]")
                )
        self.client = self._create_client() if need_client else None

        # Adding client_manager variable to make mistral client work with
        # unified OpenStack client.
        ClientManager = type(
            'ClientManager',
            (object,),
            dict(workflow_engine=self.client)
        )

        self.client_manager = ClientManager()

    def _create_client(self):
        kwargs = {
            'cert': self.options.os_cert,
            'key': self.options.os_key,
            'user_domain_name': self.options.user_domain_name,
            'user_domain_id': self.options.user_domain_id,
            'project_domain_name': self.options.project_domain_name,
            'project_domain_id': self.options.project_domain_id,
            'target_project_domain_name':
                self.options.target_project_domain_name,
            'target_project_domain_id': self.options.target_project_domain_id,
            'target_user_domain_name': self.options.target_user_domain_name,
            'target_user_domain_id': self.options.target_user_domain_id
        }

        return client.client(
            mistral_url=self.options.mistral_url,
            username=self.options.username,
            api_key=self.options.password,
            project_name=self.options.tenant_name or self.options.project_name,
            auth_url=self.options.auth_url,
            project_id=self.options.tenant_id or self.options.project_id,
            endpoint_type=self.options.endpoint_type,
            service_type=self.options.service_type,
            region_name=self.options.region_name,
            auth_token=self.options.token,
            cacert=self.options.os_cacert,
            insecure=self.options.insecure,
            profile=self.options.profile,
            auth_type=self.options.auth_type,
            client_id=self.options.client_id,
            client_secret=self.options.client_secret,
            target_username=self.options.target_username,
            target_api_key=self.options.target_password,
            target_project_name=self.options.target_tenant_name,
            target_auth_url=self.options.target_auth_url,
            target_project_id=self.options.target_tenant_id,
            target_auth_token=self.options.target_token,
            target_cacert=self.options.target_cacert,
            target_region_name=self.options.target_region_name,
            target_insecure=self.options.target_insecure,
            **kwargs
        )

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
        if version == 2:
            return self._get_commands_v2()

        return {}

    @staticmethod
    def _get_commands_v2():
        return {
            'bash-completion': BashCompletionCommand,
            'workbook-list': mistralclient.commands.v2.workbooks.List,
            'workbook-get': mistralclient.commands.v2.workbooks.Get,
            'workbook-create': mistralclient.commands.v2.workbooks.Create,
            'workbook-delete': mistralclient.commands.v2.workbooks.Delete,
            'workbook-update': mistralclient.commands.v2.workbooks.Update,
            'workbook-get-definition':
            mistralclient.commands.v2.workbooks.GetDefinition,
            'workbook-validate': mistralclient.commands.v2.workbooks.Validate,
            'workflow-list': mistralclient.commands.v2.workflows.List,
            'workflow-get': mistralclient.commands.v2.workflows.Get,
            'workflow-create': mistralclient.commands.v2.workflows.Create,
            'workflow-delete': mistralclient.commands.v2.workflows.Delete,
            'workflow-update': mistralclient.commands.v2.workflows.Update,
            'workflow-get-definition':
            mistralclient.commands.v2.workflows.GetDefinition,
            'workflow-validate': mistralclient.commands.v2.workflows.Validate,
            'environment-create':
            mistralclient.commands.v2.environments.Create,
            'environment-delete':
            mistralclient.commands.v2.environments.Delete,
            'environment-update':
            mistralclient.commands.v2.environments.Update,
            'environment-list': mistralclient.commands.v2.environments.List,
            'environment-get': mistralclient.commands.v2.environments.Get,
            'environment-get-definition':
            mistralclient.commands.v2.environments.GetDefinition,
            'run-action': mistralclient.commands.v2.action_executions.Create,
            'action-execution-list':
            mistralclient.commands.v2.action_executions.List,
            'action-execution-get':
            mistralclient.commands.v2.action_executions.Get,
            'action-execution-get-input':
            mistralclient.commands.v2.action_executions.GetInput,
            'action-execution-get-output':
            mistralclient.commands.v2.action_executions.GetOutput,
            'action-execution-update':
            mistralclient.commands.v2.action_executions.Update,
            'action-execution-delete':
            mistralclient.commands.v2.action_executions.Delete,
            'execution-create': mistralclient.commands.v2.executions.Create,
            'execution-delete': mistralclient.commands.v2.executions.Delete,
            'execution-update': mistralclient.commands.v2.executions.Update,
            'execution-list': mistralclient.commands.v2.executions.List,
            'execution-get': mistralclient.commands.v2.executions.Get,
            'execution-get-input':
            mistralclient.commands.v2.executions.GetInput,
            'execution-get-output':
            mistralclient.commands.v2.executions.GetOutput,
            'task-list': mistralclient.commands.v2.tasks.List,
            'task-get': mistralclient.commands.v2.tasks.Get,
            'task-get-published': mistralclient.commands.v2.tasks.GetPublished,
            'task-get-result': mistralclient.commands.v2.tasks.GetResult,
            'task-rerun': mistralclient.commands.v2.tasks.Rerun,
            'action-list': mistralclient.commands.v2.actions.List,
            'action-get': mistralclient.commands.v2.actions.Get,
            'action-create': mistralclient.commands.v2.actions.Create,
            'action-delete': mistralclient.commands.v2.actions.Delete,
            'action-update': mistralclient.commands.v2.actions.Update,
            'action-get-definition':
            mistralclient.commands.v2.actions.GetDefinition,
            'action-validate': mistralclient.commands.v2.actions.Validate,
            'cron-trigger-list': mistralclient.commands.v2.cron_triggers.List,
            'cron-trigger-get': mistralclient.commands.v2.cron_triggers.Get,
            'cron-trigger-create':
            mistralclient.commands.v2.cron_triggers.Create,
            'cron-trigger-delete':
            mistralclient.commands.v2.cron_triggers.Delete,
            'event-trigger-list':
            mistralclient.commands.v2.event_triggers.List,
            'event-trigger-get': mistralclient.commands.v2.event_triggers.Get,
            'event-trigger-create':
            mistralclient.commands.v2.event_triggers.Create,
            'event-trigger-delete':
            mistralclient.commands.v2.event_triggers.Delete,
            'service-list': mistralclient.commands.v2.services.List,
            'member-create': mistralclient.commands.v2.members.Create,
            'member-delete': mistralclient.commands.v2.members.Delete,
            'member-update': mistralclient.commands.v2.members.Update,
            'member-list': mistralclient.commands.v2.members.List,
            'member-get': mistralclient.commands.v2.members.Get,
        }


def main(argv=sys.argv[1:]):
    return MistralShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
