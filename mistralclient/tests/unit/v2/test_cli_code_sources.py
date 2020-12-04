# Copyright 2014 - Mirantis, Inc.
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

from unittest import mock


from mistralclient.api.v2 import code_sources
from mistralclient.commands.v2 import code_sources as code_src_cmd
from mistralclient.tests.unit import base


CODE_SRC_CONTENT = """
from mistral_lib import actions

class HelloAction(actions.Action):
    def __init__(self, f_name, l_name):
        super(HelloAction, self).__init__()

        self._f_name = f_name
        self._l_name = l_name

    def run(self, context):
        return 'Hello %s %s!' % (self._f_name, self._l_name)
"""

CODE_SRC_DICT = {
    'id': '1-2-3-4',
    'name': 'hello_module',
    'namespace': '',
    'project_id': '12345',
    'scope': 'private',
    'content': CODE_SRC_CONTENT,
    'created_at': '1',
    'updated_at': '1'
}

CODE_SRC = code_sources.CodeSource(mock, CODE_SRC_DICT)


class TestCLICodeSources(base.BaseCommandTest):
    @mock.patch('argparse.open', create=True)
    def test_create(self, mock_open):
        self.client.code_sources.create.return_value = CODE_SRC

        result = self.call(
            code_src_cmd.Create,
            app_args=['hello_module', 'hello.py']
        )

        self.assertEqual(
            ('1-2-3-4', 'hello_module', '', '12345', 'private', '1', '1'),
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    def test_create_public(self, mock_open):
        code_src_dict = CODE_SRC_DICT.copy()
        code_src_dict['scope'] = 'public'

        code_src = code_sources.CodeSource(mock, code_src_dict)

        self.client.code_sources.create.return_value = code_src

        result = self.call(
            code_src_cmd.Create,
            app_args=['hello_module', '1.txt', '--public']
        )

        self.assertEqual(
            ('1-2-3-4', 'hello_module', '', '12345', 'public', '1', '1'),
            result[1]
        )

        self.assertEqual(
            'public',
            self.client.code_sources.create.call_args[1]['scope']
        )

    @mock.patch('argparse.open', create=True)
    def test_update(self, mock_open):
        self.client.code_sources.update.return_value = CODE_SRC

        result = self.call(
            code_src_cmd.Update,
            app_args=['hello_module', 'hello.py']
        )

        self.assertEqual(
            ('1-2-3-4', 'hello_module', '', '12345', 'private', '1', '1'),
            result[1]
        )

    @mock.patch('argparse.open', create=True)
    def test_update_public(self, mock_open):
        code_src_dict = CODE_SRC_DICT.copy()
        code_src_dict['scope'] = 'public'

        code_src = code_sources.CodeSource(mock, code_src_dict)

        self.client.code_sources.update.return_value = code_src

        result = self.call(
            code_src_cmd.Update,
            app_args=['hello_module', 'hello.py', '--public']
        )

        self.assertEqual(
            ('1-2-3-4', 'hello_module', '', '12345', 'public', '1', '1'),
            result[1]
        )

        self.assertEqual(
            'public',
            self.client.code_sources.update.call_args[1]['scope']
        )

    @mock.patch('argparse.open', create=True)
    def test_update_with_id(self, mock_open):
        self.client.code_sources.update.return_value = CODE_SRC

        result = self.call(
            code_src_cmd.Update,
            app_args=['1-2-3-4', 'hello.py']
        )

        self.assertEqual(
            ('1-2-3-4', 'hello_module', '', '12345', 'private', '1', '1'),
            result[1]
        )

    def test_list(self):
        self.client.code_sources.list.return_value = [CODE_SRC]

        result = self.call(code_src_cmd.List)

        self.assertEqual(
            [('1-2-3-4', 'hello_module', '', '12345', 'private', '1', '1')],
            result[1]
        )

    def test_get(self):
        self.client.code_sources.get.return_value = CODE_SRC

        result = self.call(code_src_cmd.Get, app_args=['hello_module'])

        self.assertEqual(
            ('1-2-3-4', 'hello_module', '', '12345', 'private', '1', '1'),
            result[1]
        )

    def test_delete(self):
        self.call(code_src_cmd.Delete, app_args=['hello_module'])

        self.client.code_sources.delete.assert_called_once_with(
            'hello_module',
            None
        )

    def test_get_content(self):
        self.client.code_sources.get.return_value = CODE_SRC

        self.call(code_src_cmd.GetContent, app_args=['hello_module'])

        self.app.stdout.write.assert_called_with(CODE_SRC_CONTENT)
