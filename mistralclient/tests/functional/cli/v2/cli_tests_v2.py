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

import os

from tempest import cli
from tempest import exceptions


MISTRAL_URL = "http://localhost:8989/v2"


class MistralCLIAuth(cli.ClientTestBase):

    def mistral(self, action, flags='', params='', admin=True, fail_ok=False,
                keystone_version=3):
        """Executes Mistral command."""
        mistral_url_op = "--os-mistral-url %s" % MISTRAL_URL

        return self.cmd_with_auth(
            'mistral %s' % mistral_url_op, action, flags, params, admin,
            fail_ok, keystone_version)


class SimpleMistralCLITests(MistralCLIAuth):
    """Basic tests, check '-list', '-help' commands."""

    @classmethod
    def setUpClass(cls):
        super(SimpleMistralCLITests, cls).setUpClass()

    def test_workbooks_list(self):
        workbooks = self.parser.listing(self.mistral('workbook-list'))
        self.assertTableStruct(workbooks,
                               ['Name', 'Tags', 'Created at', 'Updated at'])

    def test_workflow_list(self):
        workflows = self.parser.listing(
            self.mistral('workflow-list'))
        self.assertTableStruct(workflows,
                               ['Name', 'Tags', 'Created at', 'Updated at'])

    def test_executions_list(self):
        executions = self.parser.listing(
            self.mistral('execution-list'))
        self.assertTableStruct(executions,
                               ['ID', 'Workflow', 'State',
                                'Created at', 'Updated at'])

    def test_tasks_list(self):
        tasks = self.parser.listing(
            self.mistral('task-list'))
        self.assertTableStruct(tasks,
                               ['ID', 'Name', 'Workflow name', 'Execution ID',
                                'State'])


class ClientTestBase(MistralCLIAuth):

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()

        cls.wb_def = os.path.relpath(
            'functionaltests/resources/v2/wb_v2.yaml', os.getcwd())

        cls.wf_def = os.path.relpath(
            'functionaltests/resources/v2/wf_v2.yaml', os.getcwd())

    def tearDown(self):
        super(ClientTestBase, self).tearDown()

        for object in ['execution', 'workflow', 'workbook']:
            objects = self.mistral_command('{0}-list'.format(object))
            if object == 'execution':
                identifiers = [obj['ID'] for obj in objects]
            else:
                identifiers = [obj['Name'] for obj in objects]
            for id in identifiers:
                if id != "<none>":
                    self.mistral('{0}-delete'.format(object), params=id)

    def get_value_of_field(self, obj, field):
        return [o['Value'] for o in obj
                if o['Field'] == "{0}".format(field)][0]

    def mistral_command(self, cmd, params=""):
        return self.parser.listing(self.mistral('{0}'.format(cmd),
                                                params='{0}'.format(params)))


class WorkbookCLITests(ClientTestBase):
    """Test suite checks commands to work with workbooks."""

    @classmethod
    def setUpClass(cls):
        super(WorkbookCLITests, cls).setUpClass()

    def test_workbook_create_delete(self):
        wb1 = self.mistral_command(
            'workbook-create', params='wb wb_tag {0}'.format(self.wb_def))
        self.assertTableStruct(wb1, ['Field', 'Value'])

        wfs = self.mistral_command('workflow-list')
        self.assertIn('wb.wf1', [wf['Name'] for wf in wfs])

        wb2 = self.mistral_command(
            'workbook-create', params='wb_without_def wb_tag')

        name1 = self.get_value_of_field(wb1, "Name")
        name2 = self.get_value_of_field(wb2, "Name")
        self.assertEqual('wb', name1)
        self.assertEqual('wb_without_def', name2)

        wbs = self.mistral_command('workbook-list')
        self.assertIn('wb', [workbook['Name'] for workbook in wbs])
        self.assertIn('wb_without_def',
                      [workbook['Name'] for workbook in wbs])

        self.mistral_command('workbook-delete', params='wb')
        self.mistral_command('workbook-delete', params='wb_without_def')

        wbs = self.mistral_command('workbook-list')
        self.assertNotIn('wb', [workbook['Name'] for workbook in wbs])
        self.assertNotIn('wb_without_def',
                         [workbook['Name'] for workbook in wbs])

    def test_workbook_update(self):
        self.mistral_command('workbook-create', params='wb')

        wb = self.mistral_command('workbook-update', params='wb tag')
        self.assertTableStruct(wb, ['Field', 'Value'])

        name = self.get_value_of_field(wb, 'Name')
        tags = self.get_value_of_field(wb, "Tags")

        self.assertEqual('wb', name)
        self.assertIn('tag', tags)

    def test_workbook_get(self):
        created = self.mistral_command('workbook-create', params='wb')
        fetched = self.mistral_command('workbook-get', params='wb')

        created_wb_name = self.get_value_of_field(created, 'Name')
        fetched_wb_name = self.get_value_of_field(fetched, 'Name')

        self.assertEqual(created_wb_name, fetched_wb_name)

        created_wb_tag = self.get_value_of_field(created, 'Tags')
        fetched_wb_tag = self.get_value_of_field(fetched, 'Tags')

        self.assertEqual(created_wb_tag, fetched_wb_tag)

    def test_workbook_upload_get_definition(self):
        self.mistral('workbook-create', params='wb')
        self.mistral('workbook-upload-definition',
                     params='wb {0}'.format(self.wb_def))

        definition = self.mistral_command('workbook-get-definition',
                                          params='wb')
        self.assertNotIn('404 Not Found', definition)


class WorkflowCLITests(ClientTestBase):
    """Test suite checks commands to work with workflows."""

    @classmethod
    def setUpClass(cls):
        super(WorkflowCLITests, cls).setUpClass()

    def test_workflow_create_delete(self):
        wf = self.mistral_command(
            'workflow-create', params='wf wf_tag {0}'.format(self.wf_def))
        self.assertTableStruct(wf, ['Field', 'Value'])

        name = self.get_value_of_field(wf, "Name")
        self.assertEqual('wf', name)

        wfs = self.mistral_command('workflow-list')
        self.assertIn('wf', [workflow['Name'] for workflow in wfs])

        self.mistral_command('workflow-delete', params='wf')
        wfs = self.mistral_command('workflow-list')
        self.assertNotIn('wf', [workflow['Name'] for workflow in wfs])

    def test_workflow_update(self):
        self.mistral(
            'workflow-create', params='wf wf_tag {0}'.format(self.wf_def))

        wf = self.mistral_command('workflow-update', params='wf tag')
        self.assertTableStruct(wf, ['Field', 'Value'])

        name = self.get_value_of_field(wf, 'Name')
        tags = self.get_value_of_field(wf, "Tags")

        self.assertEqual('wf', name)
        self.assertIn('tag', tags)

    def test_workflow_get(self):
        created = self.mistral_command(
            'workflow-create', params='wf wf_tag {0}'.format(self.wf_def))

        fetched = self.mistral_command('workflow-get', params='wf')

        created_wf_name = self.get_value_of_field(created, 'Name')
        fetched_wf_name = self.get_value_of_field(fetched, 'Name')

        self.assertEqual(created_wf_name, fetched_wf_name)

        created_wf_tag = self.get_value_of_field(created, 'Tags')
        fetched_wf_tag = self.get_value_of_field(fetched, 'Tags')

        self.assertEqual(created_wf_tag, fetched_wf_tag)

    def test_workflow_upload_get_definition(self):
        self.mistral(
            'workflow-create', params='wf wf_tag {0}'.format(self.wf_def))
        self.mistral(
            'workflow-upload-definition',
            params='wf {0}'.format(self.wf_def))

        definition = self.mistral_command(
            'workflow-get-definition', params='wf')
        self.assertNotIn('404 Not Found', definition)


class ExecutionCLITests(ClientTestBase):
    """Test suite checks commands to work with executions."""

    def setUp(self):
        super(ExecutionCLITests, self).setUp()

        self.mistral(
            'workbook-create', params='wb wb_tag {0}'.format(self.wb_def))

    def tearDown(self):
        super(ExecutionCLITests, self).tearDown()

    def test_execution_create_delete(self):
        execution = self.mistral_command(
            'execution-create', params='wb.wf1')

        self.assertTableStruct(execution, ['Field', 'Value'])

        exec_id = self.get_value_of_field(execution, 'ID')
        wf = self.get_value_of_field(execution, 'Workflow')
        created_at = self.get_value_of_field(execution, 'Created at')

        self.assertEqual('wb.wf1', wf)
        self.assertIsNotNone(created_at)

        execs = self.mistral_command('execution-list')
        self.assertIn(exec_id, [ex['ID'] for ex in execs])
        self.assertIn(wf, [ex['Workflow'] for ex in execs])
        self.assertIn('SUCCESS', [ex['State'] for ex in execs])

        self.mistral_command('execution-delete', params='{0}'.format(exec_id))

    def test_execution_update(self):
        execution = self.mistral_command('execution-create', params='wb.wf1')

        exec_id = self.get_value_of_field(execution, 'ID')
        status = self.get_value_of_field(execution, 'State')

        self.assertEqual('RUNNING', status)

        execution = self.mistral_command(
            'execution-update', params='{0} "STOPPED"'.format(exec_id))

        updated_exec_id = self.get_value_of_field(execution, 'ID')
        status = self.get_value_of_field(execution, 'State')

        self.assertEqual(exec_id, updated_exec_id)
        self.assertEqual('STOPPED', status)

    def test_execution_get(self):
        execution = self.mistral_command(
            'execution-create', params='wb.wf1')

        exec_id = self.get_value_of_field(execution, 'ID')

        execution = self.mistral_command(
            'execution-get', params='{0}'.format(exec_id))

        gotten_id = self.get_value_of_field(execution, 'ID')
        wf = self.get_value_of_field(execution, 'Workflow')

        self.assertEqual(exec_id, gotten_id)
        self.assertEqual('wb.wf1', wf)

    def test_execution_get_input(self):
        execution = self.mistral_command(
            'execution-create', params='wb.wf1')

        exec_id = self.get_value_of_field(execution, 'ID')
        ex_input = self.mistral_command('execution-get-input', params=exec_id)
        self.assertEqual([], ex_input)

    def test_execution_get_output(self):
        execution = self.mistral_command(
            'execution-create', params='wb.wf1')

        exec_id = self.get_value_of_field(execution, 'ID')
        ex_output = self.mistral_command(
            'execution-get-output', params=exec_id)
        self.assertEqual([], ex_output)


class NegativeCLITests(ClientTestBase):
    """This class contains negative tests."""

    def test_wb_list_extra_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-list', params='param')

    def test_wb_get_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-get', params='wb')

    def test_wb_get_without_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-get')

    def test_wb_create_same_name(self):
        self.mistral('workbook-create', params='wb')
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-create', params='wb')

    def test_wb_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workbook-create', params='wb pam pam pam')

    def test_wb_delete_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-delete', params='wb')

    def test_wb_update_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-update', params='wb tag def')

    def test_wb_upload_definition_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workbook-upload-definition', params='wb')

    def test_wb_upload_definition_using_wrong_path(self):
        self.mistral('workbook-create', params='wb')
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workbook-upload-definition', params='wb tag def')

    def test_wb_get_definition_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workbook-get-definition', params='wb')

    def test_wf_list_extra_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-list', params='param')

    def test_wf_get_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-get', params='wb')

    def test_wf_get_without_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-get')

    def test_wf_create_without_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workflow-create', params='wf tag')

    def test_wf_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workflow-create', params='wf tag def')

    def test_wf_delete_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-delete', params='wf')

    def test_wf_update_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-update', params='wb tag def')

    def test_wf_upload_definition_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workflow-upload-definition', params='wf')

    def test_wf_get_definition_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workflow-get-definition', params='wf')

    def test_ex_list_extra_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-list', params='param')

    def test_ex_create_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-create', params='wf')

    def test_ex_create_unexist_task(self):
        self.mistral('workbook-create', params='wb')
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'execution-create', params='wb param {}')

    def test_ex_create_without_context(self):
        self.mistral('workbook-create', params='wb')
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-create', params='wb.wf1')

    def test_ex_get_nonexist_execution(self):
        self.mistral('workbook-create', params='wb')
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-get', params='wb.wf1 id')
