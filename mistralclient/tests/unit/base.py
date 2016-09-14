# Copyright 2013 - Mirantis, Inc.
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

import mock
from oslotest import base
from requests_mock.contrib import fixture


class BaseClientTest(base.BaseTestCase):
    _client = None

    def setUp(self):
        super(BaseClientTest, self).setUp()
        self.requests_mock = self.useFixture(fixture.Fixture())


class BaseCommandTest(base.BaseTestCase):
    def setUp(self):
        super(BaseCommandTest, self).setUp()
        self.app = mock.Mock()
        self.client = self.app.client_manager.workflow_engine

    def call(self, command, app_args=[], prog_name=''):
        cmd = command(self.app, app_args)

        parsed_args = cmd.get_parser(prog_name).parse_args(app_args)

        return cmd.take_action(parsed_args)
