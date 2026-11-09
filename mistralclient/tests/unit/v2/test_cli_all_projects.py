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

from mistralclient.commands.v2 import code_sources
from mistralclient.commands.v2 import cron_triggers
from mistralclient.commands.v2 import dynamic_actions
from mistralclient.commands.v2 import event_triggers
from mistralclient.commands.v2 import executions
from mistralclient.commands.v2 import tasks
from mistralclient.commands.v2 import workflows
from mistralclient.tests.unit import base

COMMANDS = [
    (executions.List, 'executions'),
    (workflows.List, 'workflows'),
    (cron_triggers.List, 'cron_triggers'),
    (event_triggers.List, 'event_triggers'),
    (code_sources.List, 'code_sources'),
    (dynamic_actions.List, 'dynamic_actions'),
]


class TestCLIAllProjects(base.BaseCommandTest):

    def _list(self, manager):
        manager = getattr(self.client, manager)
        manager.list.return_value = []

        return manager.list

    def test_all_projects(self):
        for command, manager in COMMANDS:
            list_mock = self._list(manager)

            self.call(command, app_args=['--all-projects'])

            self.assertIs(True, list_mock.call_args[1]['all_projects'])

    def test_no_all_projects(self):
        for command, manager in COMMANDS:
            list_mock = self._list(manager)

            self.call(command)

            self.assertNotIn('all_projects', list_mock.call_args[1])

    def test_all_projects_not_supported(self):
        self._list('tasks')

        self.assertRaises(
            SystemExit,
            self.call,
            tasks.List,
            app_args=['--all-projects']
        )
