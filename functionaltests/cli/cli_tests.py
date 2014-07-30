# Copyright (c) 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tempest import cli


class ClientTestBase(cli.ClientTestBase):

    def mistral(self, action, flags='', params='', admin=True, fail_ok=False,
                keystone_version=3):
        """Executes Mistral command."""
        return self.cmd_with_auth(
            'mistral', action, flags, params, admin, fail_ok, keystone_version)


class SimpleMistralCLITests(ClientTestBase):
    """Basic tests, check '-list', '-help' commands."""

    @classmethod
    def setUpClass(cls):
        super(SimpleMistralCLITests, cls).setUpClass()

    def test_command_help(self):
        help = self.mistral('--help')

        self.assertIn('Command-line interface to the Mistral APIs', help)
        self.assertIn('Commands:', help)

        expected_commands = ('complete', 'execution-create',
                             'execution-delete', 'execution-get',
                             'execution-list', 'execution-update',
                             'help', 'task-get', 'task-list',
                             'task-update', 'workbook-create',
                             'workbook-delete', 'workbook-get',
                             'workbook-get-definition', 'workbook-list',
                             'workbook-update', 'workbook-upload-definition')
        for command in expected_commands:
            self.assertIn(command, help)

    def test_workbooks_list(self):
        workbooks = self.parser.listing(self.mistral('workbook-list'))
        self.assertTableStruct(workbooks,
                               ['Name', 'Description', 'Tags'])

    def test_executions_list(self):
        executions = self.parser.listing(
            self.mistral('execution-list', params='""'))
        self.assertTableStruct(executions,
                               ['ID', 'Workbook', 'Task', 'State'])

    def test_tasks_list(self):
        tasks = self.parser.listing(
            self.mistral('task-list', params='"", ""'))
        self.assertTableStruct(tasks,
                               ['ID', 'Workbook', 'Execution', 'Name',
                                'Description', 'State', 'Tags'])
