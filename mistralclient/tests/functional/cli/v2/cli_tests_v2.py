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

from tempest.lib import exceptions

from mistralclient.tests.functional.cli import base
from mistralclient.tests.functional.cli.v2 import base_v2


MISTRAL_URL = "http://localhost:8989/v2"


class SimpleMistralCLITests(base.MistralCLIAuth):
    """Basic tests, check '-list', '-help' commands."""

    _mistral_url = MISTRAL_URL

    @classmethod
    def setUpClass(cls):
        super(SimpleMistralCLITests, cls).setUpClass()

    def test_workbooks_list(self):
        workbooks = self.parser.listing(self.mistral('workbook-list'))

        self.assertTableStruct(
            workbooks,
            ['Name', 'Tags', 'Created at', 'Updated at']
        )

    def test_workflow_list(self):
        workflows = self.parser.listing(self.mistral('workflow-list'))

        self.assertTableStruct(
            workflows,
            ['ID', 'Name', 'Tags', 'Input', 'Created at', 'Updated at']
        )

    def test_executions_list(self):
        executions = self.parser.listing(self.mistral('execution-list'))

        self.assertTableStruct(
            executions,
            ['ID', 'Workflow name', 'Workflow ID', 'State', 'Created at',
             'Updated at']
        )

    def test_tasks_list(self):
        tasks = self.parser.listing(self.mistral('task-list'))

        self.assertTableStruct(
            tasks,
            ['ID', 'Name', 'Workflow name', 'Execution ID', 'State']
        )

    def test_cron_trigger_list(self):
        triggers = self.parser.listing(self.mistral('cron-trigger-list'))

        self.assertTableStruct(
            triggers,
            ['Name', 'Workflow', 'Pattern', 'Next execution time',
             'Remaining executions', 'Created at', 'Updated at']
        )

    def test_event_trigger_list(self):
        triggers = self.parser.listing(self.mistral('event-trigger-list'))

        self.assertTableStruct(
            triggers,
            ['ID', 'Name', 'Workflow ID', 'Exchange', 'Topic', 'Event',
             'Created at', 'Updated at']
        )

    def test_actions_list(self):
        actions = self.parser.listing(self.mistral('action-list'))

        self.assertTableStruct(
            actions,
            ['Name', 'Is system', 'Input', 'Description',
             'Tags', 'Created at', 'Updated at']
        )

    def test_environments_list(self):
        envs = self.parser.listing(self.mistral('environment-list'))

        self.assertTableStruct(
            envs,
            ['Name', 'Description', 'Scope', 'Created at', 'Updated at']
        )

    def test_action_execution_list(self):
        act_execs = self.parser.listing(self.mistral('action-execution-list'))

        self.assertTableStruct(
            act_execs,
            ['ID', 'Name', 'Workflow name', 'State', 'Accepted']
        )

    def test_action_execution_list_with_limit(self):
        act_execs = self.parser.listing(
            self.mistral(
                'action-execution-list',
                params='--limit 1'
            )
        )

        self.assertEqual(1, len(act_execs))


class WorkbookCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with workbooks."""

    @classmethod
    def setUpClass(cls):
        super(WorkbookCLITests, cls).setUpClass()

    def test_workbook_create_delete(self):
        wb = self.mistral_admin('workbook-create', params=self.wb_def)

        wb_name = self.get_field_value(wb, "Name")

        self.assertTableStruct(wb, ['Field', 'Value'])

        wbs = self.mistral_admin('workbook-list')
        self.assertIn(wb_name, [w['Name'] for w in wbs])

        wbs = self.mistral_admin('workbook-list')
        self.assertIn(wb_name, [w['Name'] for w in wbs])

        self.mistral_admin('workbook-delete', params=wb_name)

        wbs = self.mistral_admin('workbook-list')
        self.assertNotIn(wb_name, [w['Name'] for w in wbs])

    def test_workbook_create_with_tags(self):
        wb = self.workbook_create(self.wb_with_tags_def)

        self.assertIn('tag', self.get_field_value(wb, 'Tags'))

    def test_workbook_update(self):
        wb = self.workbook_create(self.wb_def)

        wb_name = self.get_field_value(wb, "Name")

        init_update_at = self.get_field_value(wb, "Updated at")
        tags = self.get_field_value(wb, 'Tags')

        self.assertNotIn('tag', tags)

        wb = self.mistral_admin('workbook-update', params=self.wb_def)

        update_at = self.get_field_value(wb, "Updated at")
        name = self.get_field_value(wb, 'Name')
        tags = self.get_field_value(wb, 'Tags')

        self.assertEqual(wb_name, name)
        self.assertNotIn('tag', tags)
        self.assertEqual(init_update_at, update_at)

        wb = self.mistral_admin(
            'workbook-update',
            params=self.wb_with_tags_def
        )

        self.assertTableStruct(wb, ['Field', 'Value'])

        update_at = self.get_field_value(wb, "Updated at")
        name = self.get_field_value(wb, 'Name')
        tags = self.get_field_value(wb, 'Tags')

        self.assertEqual(wb_name, name)
        self.assertIn('tag', tags)
        self.assertNotEqual(init_update_at, update_at)

    def test_workbook_get(self):
        created = self.workbook_create(self.wb_with_tags_def)

        wb_name = self.get_field_value(created, "Name")

        fetched = self.mistral_admin('workbook-get', params=wb_name)

        created_wb_name = self.get_field_value(created, 'Name')
        fetched_wb_name = self.get_field_value(fetched, 'Name')

        self.assertEqual(created_wb_name, fetched_wb_name)

        created_wb_tag = self.get_field_value(created, 'Tags')
        fetched_wb_tag = self.get_field_value(fetched, 'Tags')

        self.assertEqual(created_wb_tag, fetched_wb_tag)

    def test_workbook_get_definition(self):
        wb = self.workbook_create(self.wb_def)

        wb_name = self.get_field_value(wb, "Name")

        definition = self.mistral_admin(
            'workbook-get-definition',
            params=wb_name
        )

        self.assertNotIn('404 Not Found', definition)

    def test_workbook_validate_with_valid_def(self):
        wb = self.mistral_admin('workbook-validate', params=self.wb_def)

        wb_valid = self.get_field_value(wb, 'Valid')
        wb_error = self.get_field_value(wb, 'Error')

        self.assertEqual('True', wb_valid)
        self.assertEqual('None', wb_error)

    def test_workbook_validate_with_invalid_def(self):
        self.create_file('wb.yaml', 'name: wb\n')

        wb = self.mistral_admin('workbook-validate', params='wb.yaml')

        wb_valid = self.get_field_value(wb, 'Valid')
        wb_error = self.get_field_value(wb, 'Error')

        self.assertEqual('False', wb_valid)
        self.assertNotEqual('None', wb_error)


class WorkflowCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with workflows."""

    @classmethod
    def setUpClass(cls):
        super(WorkflowCLITests, cls).setUpClass()

    def test_workflow_create_delete(self):
        init_wfs = self.mistral_admin('workflow-create', params=self.wf_def)

        wf_names = [wf['Name'] for wf in init_wfs]

        self.assertTableStruct(init_wfs, ['Name', 'Created at', 'Updated at'])

        wfs = self.mistral_admin('workflow-list')
        self.assertIn(wf_names[0], [workflow['Name'] for workflow in wfs])

        for wf_name in wf_names:
            self.mistral_admin('workflow-delete', params=wf_name)

        wfs = self.mistral_admin('workflow-list')
        for wf in wf_names:
            self.assertNotIn(wf, [workflow['Name'] for workflow in wfs])

    def test_workflow_within_namespace_create_delete(self):
        params = self.wf_def + ' --namespace abcdef'
        init_wfs = self.mistral_admin('workflow-create', params=params)

        wf_names = [wf['Name'] for wf in init_wfs]

        self.assertTableStruct(init_wfs, ['Name', 'Created at', 'Updated at'])

        wfs = self.mistral_admin('workflow-list')
        self.assertIn(wf_names[0], [workflow['Name'] for workflow in wfs])

        for wf_name in wf_names:
            self.mistral_admin(
                'workflow-delete',
                params=wf_name+' --namespace abcdef'
            )

        wfs = self.mistral_admin('workflow-list')
        for wf in wf_names:
            self.assertNotIn(wf, [workflow['Name'] for workflow in wfs])

        init_wfs = self.mistral_admin('workflow-create', params=params)
        wf_ids = [wf['ID'] for wf in init_wfs]
        for wf_id in wf_ids:
            self.mistral_admin('workflow-delete', params=wf_id)

        for wf in wf_names:
            self.assertNotIn(wf, [workflow['Name'] for workflow in wfs])

    def test_create_wf_with_tags(self):
        init_wfs = self.workflow_create(self.wf_def)
        wf_name = init_wfs[1]['Name']

        self.assertTableStruct(
            init_wfs,
            ['Name', 'Created at', 'Updated at', 'Tags']
        )

        created_wf_info = self.get_item_info(
            get_from=init_wfs,
            get_by='Name',
            value=wf_name
        )

        self.assertEqual('tag', created_wf_info['Tags'])

    def test_workflow_update(self):
        wf = self.workflow_create(self.wf_def)

        wf_name = wf[0]['Name']
        wf_id = wf[0]['ID']

        created_wf_info = self.get_item_info(
            get_from=wf,
            get_by='Name',
            value=wf_name
        )

        # Update a workflow with definition unchanged.
        upd_wf = self.mistral_admin(
            'workflow-update',
            params='{0}'.format(self.wf_def)
        )

        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf,
            get_by='Name',
            value=wf_name
        )

        self.assertEqual(wf_name, upd_wf[0]['Name'])
        self.assertEqual(
            created_wf_info['Created at'].split(".")[0],
            updated_wf_info['Created at']
        )
        self.assertEqual(
            created_wf_info['Updated at'],
            updated_wf_info['Updated at']
        )

        # Update a workflow with definition changed.
        upd_wf = self.mistral_admin(
            'workflow-update',
            params='{0}'.format(self.wf_with_delay_def)
        )

        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf,
            get_by='Name',
            value=wf_name
        )

        self.assertEqual(wf_name, upd_wf[0]['Name'])
        self.assertEqual(
            created_wf_info['Created at'].split(".")[0],
            updated_wf_info['Created at']
        )
        self.assertNotEqual(
            created_wf_info['Updated at'],
            updated_wf_info['Updated at']
        )

        # Update a workflow with uuid.
        upd_wf = self.mistral_admin(
            'workflow-update',
            params='{0} --id {1}'.format(self.wf_with_delay_def, wf_id)
        )

        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf,
            get_by='ID',
            value=wf_id
        )

        self.assertEqual(wf_name, upd_wf[0]['Name'])
        self.assertEqual(
            created_wf_info['Created at'].split(".")[0],
            updated_wf_info['Created at']
        )
        self.assertNotEqual(
            created_wf_info['Updated at'],
            updated_wf_info['Updated at']
        )

    def test_workflow_update_within_namespace(self):
        namespace = 'abc'
        wf = self.workflow_create(self.wf_def, namespace=namespace)

        wf_name = wf[0]['Name']
        wf_id = wf[0]['ID']
        wf_namespace = wf[0]['Namespace']
        created_wf_info = self.get_item_info(
            get_from=wf,
            get_by='Name',
            value=wf_name
        )

        # Update a workflow with definition unchanged.
        upd_wf = self.mistral_admin(
            'workflow-update',
            params='{0} --namespace {1}'.format(self.wf_def, namespace)
        )

        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf,
            get_by='Name',
            value=wf_name
        )

        self.assertEqual(wf_name, upd_wf[0]['Name'])
        self.assertEqual(namespace, wf_namespace)
        self.assertEqual(wf_namespace, upd_wf[0]['Namespace'])
        self.assertEqual(
            created_wf_info['Created at'].split(".")[0],
            updated_wf_info['Created at']
        )
        self.assertEqual(
            created_wf_info['Updated at'],
            updated_wf_info['Updated at']
        )

        # Update a workflow with definition changed.
        upd_wf = self.mistral_admin(
            'workflow-update',
            params='{0} --namespace {1}'.format(
                self.wf_with_delay_def,
                namespace
            )
        )

        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf,
            get_by='Name',
            value=wf_name
        )

        self.assertEqual(wf_name, upd_wf[0]['Name'])
        self.assertEqual(
            created_wf_info['Created at'].split(".")[0],
            updated_wf_info['Created at']
        )
        self.assertNotEqual(
            created_wf_info['Updated at'],
            updated_wf_info['Updated at']
        )

        # Update a workflow with uuid.
        upd_wf = self.mistral_admin(
            'workflow-update',
            params='{0} --id {1}'.format(self.wf_with_delay_def, wf_id)
        )

        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf,
            get_by='ID',
            value=wf_id
        )

        self.assertEqual(wf_name, upd_wf[0]['Name'])
        self.assertEqual(
            created_wf_info['Created at'].split(".")[0],
            updated_wf_info['Created at']
        )
        self.assertNotEqual(
            created_wf_info['Updated at'],
            updated_wf_info['Updated at']
        )

    def test_workflow_update_truncate_input(self):
        input_value = "very_long_input_parameter_name_that_should_be_truncated"

        wf_def = """
        version: "2.0"
        workflow1:
          input:
            - {0}
          tasks:
            task1:
              action: std.noop
        """.format(input_value)

        self.create_file('wf.yaml', wf_def)
        self.workflow_create('wf.yaml')

        updated_wf = self.mistral_admin('workflow-update', params='wf.yaml')

        updated_wf_info = self.get_item_info(
            get_from=updated_wf,
            get_by='Name',
            value='workflow1'
        )

        self.assertEqual(updated_wf_info['Input'][:-3], input_value[:25])

    def test_workflow_get(self):
        created = self.workflow_create(self.wf_def)

        wf_name = created[0]['Name']

        fetched = self.mistral_admin('workflow-get', params=wf_name)
        fetched_wf_name = self.get_field_value(fetched, 'Name')

        self.assertEqual(wf_name, fetched_wf_name)

    def test_workflow_get_with_id(self):
        created = self.workflow_create(self.wf_def)

        wf_name = created[0]['Name']
        wf_id = created[0]['ID']

        fetched = self.mistral_admin('workflow-get', params=wf_id)
        fetched_wf_name = self.get_field_value(fetched, 'Name')

        self.assertEqual(wf_name, fetched_wf_name)

    def test_workflow_get_definition(self):
        wf = self.workflow_create(self.wf_def)

        wf_name = wf[0]['Name']

        definition = self.mistral_admin(
            'workflow-get-definition',
            params=wf_name
        )

        self.assertNotIn('404 Not Found', definition)

    def test_workflow_validate_with_valid_def(self):
        wf = self.mistral_admin('workflow-validate', params=self.wf_def)

        wf_valid = self.get_field_value(wf, 'Valid')
        wf_error = self.get_field_value(wf, 'Error')

        self.assertEqual('True', wf_valid)
        self.assertEqual('None', wf_error)

    def test_workflow_validate_with_invalid_def(self):
        self.create_file('wf.yaml', 'name: wf\n')

        wf = self.mistral_admin('workflow-validate', params='wf.yaml')

        wf_valid = self.get_field_value(wf, 'Valid')
        wf_error = self.get_field_value(wf, 'Error')

        self.assertEqual('False', wf_valid)
        self.assertNotEqual('None', wf_error)

    def test_workflow_list_with_filter(self):
        workflows = self.parser.listing(self.mistral('workflow-list'))

        self.assertTableStruct(
            workflows,
            ['ID', 'Name', 'Tags', 'Input', 'Created at', 'Updated at']
        )

        # We know that we have more than one workflow by default.
        self.assertGreater(len(workflows), 1)

        # Now let's provide a filter to the list command.
        workflows = self.parser.listing(
            self.mistral(
                'workflow-list',
                params='--filter name=std.create_instance'
            )
        )

        self.assertTableStruct(
            workflows,
            ['ID', 'Name', 'Tags', 'Input', 'Created at', 'Updated at']
        )

        self.assertEqual(1, len(workflows))

        self.assertIn('std.create_instance', workflows[0]['Name'])


class ExecutionCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with executions."""

    @classmethod
    def setUpClass(cls):
        super(ExecutionCLITests, cls).setUpClass()

    def setUp(self):
        super(ExecutionCLITests, self).setUp()

        wfs = self.workflow_create(self.wf_def)
        self.async_wf = self.workflow_create(self.async_wf_def)[0]

        self.direct_wf = wfs[0]
        self.reverse_wf = wfs[1]

        self.create_file('input', '{\n    "farewell": "Bye"\n}\n')
        self.create_file('task_name', '{\n    "task_name": "goodbye"\n}\n')

    def test_execution_by_id_of_workflow_within_namespace(self):
        namespace = 'abc'

        wfs = self.workflow_create(self.lowest_level_wf, namespace=namespace)

        wf_def_name = wfs[0]['Name']
        wf_id = wfs[0]['ID']

        execution = self.execution_create(wf_id)

        self.assertTableStruct(execution, ['Field', 'Value'])

        wf_name = self.get_field_value(execution, 'Workflow name')
        wf_namespace = self.get_field_value(execution, 'Workflow namespace')
        wf_id = self.get_field_value(execution, 'Workflow ID')

        self.assertEqual(wf_def_name, wf_name)
        self.assertEqual(namespace, wf_namespace)
        self.assertIsNotNone(wf_id)

    def test_execution_within_namespace_create_delete(self):
        namespace = 'abc'

        self.workflow_create(self.lowest_level_wf)
        self.workflow_create(self.lowest_level_wf, namespace=namespace)
        self.workflow_create(self.middle_wf, namespace=namespace)
        self.workflow_create(self.top_level_wf)
        wfs = self.workflow_create(self.top_level_wf, namespace=namespace)

        top_wf_name = wfs[0]['Name']
        execution = self.mistral_admin(
            'execution-create',
            params='{0} --namespace {1}'.format(top_wf_name, namespace)
        )
        exec_id = self.get_field_value(execution, 'ID')

        self.assertTableStruct(execution, ['Field', 'Value'])

        wf_name = self.get_field_value(execution, 'Workflow name')
        wf_namespace = self.get_field_value(execution, 'Workflow namespace')
        wf_id = self.get_field_value(execution, 'Workflow ID')
        created_at = self.get_field_value(execution, 'Created at')

        self.assertEqual(top_wf_name, wf_name)
        self.assertEqual(namespace, wf_namespace)
        self.assertIsNotNone(wf_id)
        self.assertIsNotNone(created_at)

        execs = self.mistral_admin('execution-list')

        self.assertIn(exec_id, [ex['ID'] for ex in execs])
        self.assertIn(wf_name, [ex['Workflow name'] for ex in execs])
        self.assertIn(namespace, [ex['Workflow namespace'] for ex in execs])

        self.mistral_admin('execution-delete', params=exec_id)

    def test_execution_create_delete(self):

        execution = self.mistral_admin(
            'execution-create',
            params='{0} -d "execution test"'.format(self.direct_wf['Name'])
        )

        exec_id = self.get_field_value(execution, 'ID')

        self.assertTableStruct(execution, ['Field', 'Value'])

        wf_name = self.get_field_value(execution, 'Workflow name')
        wf_id = self.get_field_value(execution, 'Workflow ID')
        created_at = self.get_field_value(execution, 'Created at')
        description = self.get_field_value(execution, 'Description')

        self.assertEqual(self.direct_wf['Name'], wf_name)
        self.assertIsNotNone(wf_id)
        self.assertIsNotNone(created_at)
        self.assertEqual("execution test", description)

        execs = self.mistral_admin('execution-list')

        self.assertIn(exec_id, [ex['ID'] for ex in execs])
        self.assertIn(wf_name, [ex['Workflow name'] for ex in execs])

        self.mistral_admin('execution-delete', params=exec_id)

    def test_execution_create_with_input_and_start_task(self):
        execution = self.execution_create(
            "%s input task_name" % self.reverse_wf['Name']
        )

        exec_id = self.get_field_value(execution, 'ID')

        result = self.wait_execution_success(exec_id)

        self.assertTrue(result)

    def test_execution_update(self):
        execution = self.execution_create(self.async_wf['Name'])

        exec_id = self.get_field_value(execution, 'ID')
        status = self.get_field_value(execution, 'State')

        self.assertEqual('RUNNING', status)

        # Update execution state.
        execution = self.mistral_admin(
            'execution-update',
            params='{0} -s PAUSED'.format(exec_id))

        updated_exec_id = self.get_field_value(execution, 'ID')
        status = self.get_field_value(execution, 'State')

        self.assertEqual(exec_id, updated_exec_id)
        self.assertEqual('PAUSED', status)

        # Update execution description.
        execution = self.mistral_admin(
            'execution-update',
            params='{0} -d "execution update test"'.format(exec_id)
        )

        description = self.get_field_value(execution, 'Description')

        self.assertEqual("execution update test", description)

    def test_execution_get(self):
        execution = self.execution_create(self.direct_wf['Name'])

        exec_id = self.get_field_value(execution, 'ID')

        execution = self.mistral_admin(
            'execution-get',
            params='{0}'.format(exec_id)
        )

        gotten_id = self.get_field_value(execution, 'ID')
        wf_name = self.get_field_value(execution, 'Workflow name')
        wf_id = self.get_field_value(execution, 'Workflow ID')

        self.assertIsNotNone(wf_id)
        self.assertEqual(exec_id, gotten_id)
        self.assertEqual(self.direct_wf['Name'], wf_name)

    def test_execution_get_input(self):
        execution = self.execution_create(self.direct_wf['Name'])
        exec_id = self.get_field_value(execution, 'ID')

        ex_input = self.mistral_admin('execution-get-input', params=exec_id)

        self.assertEqual([], ex_input)

    def test_execution_get_output(self):
        execution = self.execution_create(self.direct_wf['Name'])

        exec_id = self.get_field_value(execution, 'ID')

        ex_output = self.mistral_admin('execution-get-output', params=exec_id)

        self.assertEqual([], ex_output)

    def test_executions_list_with_task(self):
        wrapping_wf = self.workflow_create(self.wf_wrapping_wf)
        decoy = self.execution_create(wrapping_wf[-1]['Name'])
        wrapping_wf_ex = self.execution_create(wrapping_wf[-1]['Name'])

        wrapping_wf_ex_id = self.get_field_value(wrapping_wf_ex, 'ID')

        self.assertIsNot(wrapping_wf_ex_id, self.get_field_value(decoy, 'ID'))

        tasks = self.mistral_admin('task-list', params=wrapping_wf_ex_id)

        wrapping_task_id = tasks[-1]['ID']

        wf_execs = self.mistral_cli(
            True,
            'execution-list',
            params="--task {}".format(wrapping_task_id)
        )

        self.assertEqual(1, len(wf_execs))

        wf_exec = wf_execs[0]

        self.assertEqual(wrapping_task_id, wf_exec['Task Execution ID'])

    def test_executions_list_with_pagination(self):
        self.execution_create(
            params='{0} -d "a"'.format(self.direct_wf['Name'])
        )

        self.execution_create(
            params='{0} -d "b"'.format(self.direct_wf['Name'])
        )

        all_wf_execs = self.mistral_cli(True, 'execution-list')

        self.assertEqual(2, len(all_wf_execs))

        wf_execs = self.mistral_cli(
            True,
            'execution-list',
            params="--limit 1"
        )

        self.assertEqual(1, len(wf_execs))

        wf_ex1_id = all_wf_execs[0]['ID']
        wf_ex2_id = all_wf_execs[1]['ID']

        wf_execs = self.mistral_cli(
            True,
            'execution-list',
            params="--marker %s" % wf_ex1_id
        )

        self.assertNotIn(wf_ex1_id, [ex['ID'] for ex in wf_execs])
        self.assertIn(wf_ex2_id, [ex['ID'] for ex in wf_execs])

        wf_execs = self.mistral_cli(
            True,
            'execution-list',
            params="--sort_keys Description"
        )

        self.assertIn(wf_ex1_id, [ex['ID'] for ex in wf_execs])
        self.assertIn(wf_ex2_id, [ex['ID'] for ex in wf_execs])

        wf_ex1_index = -1
        wf_ex2_index = -1

        for idx, ex in enumerate(wf_execs):
            if ex['ID'] == wf_ex1_id:
                wf_ex1_index = idx
            elif ex['ID'] == wf_ex2_id:
                wf_ex2_index = idx

        self.assertLess(wf_ex1_index, wf_ex2_index)

        wf_execs = self.mistral_cli(
            True,
            'execution-list',
            params="--sort_keys Description --sort_dirs=desc"
        )

        self.assertIn(wf_ex1_id, [ex['ID'] for ex in wf_execs])
        self.assertIn(wf_ex2_id, [ex['ID'] for ex in wf_execs])

        wf_ex1_index = -1
        wf_ex2_index = -1

        for idx, ex in enumerate(wf_execs):
            if ex['ID'] == wf_ex1_id:
                wf_ex1_index = idx
            elif ex['ID'] == wf_ex2_id:
                wf_ex2_index = idx

        self.assertGreater(wf_ex1_index, wf_ex2_index)

    def test_execution_list_with_filter(self):
        wf_ex1 = self.execution_create(
            params='{0} -d "a"'.format(self.direct_wf['Name'])
        )

        wf_ex1_id = self.get_field_value(wf_ex1, 'ID')

        self.execution_create(
            params='{0} -d "b"'.format(self.direct_wf['Name'])
        )

        # Request a list without filters.
        wf_execs = self.mistral_cli(True, 'execution-list')

        self.assertTableStruct(
            wf_execs,
            ['ID', 'Workflow name', 'Workflow ID', 'State', 'Created at',
             'Updated at']
        )

        self.assertEqual(2, len(wf_execs))

        # Now let's provide a filter.
        wf_execs = self.mistral_cli(
            True,
            'execution-list',
            params='--filter description=a'
        )

        self.assertTableStruct(
            wf_execs,
            ['ID', 'Workflow name', 'Workflow ID', 'State', 'Created at',
             'Updated at']
        )

        self.assertEqual(1, len(wf_execs))

        self.assertEqual(wf_ex1_id, wf_execs[0]['ID'])
        self.assertEqual('a', wf_execs[0]['Description'])


class CronTriggerCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with cron-triggers."""

    @classmethod
    def setUpClass(cls):
        super(CronTriggerCLITests, cls).setUpClass()

    def setUp(self):
        super(CronTriggerCLITests, self).setUp()

        wf = self.workflow_create(self.wf_def)

        self.wf_name = wf[0]['Name']

    def test_cron_trigger_create_delete(self):
        trigger = self.mistral_admin(
            'cron-trigger-create',
            params=('trigger %s {} --pattern "5 * * * *" --count 5'
                    ' --first-time "4242-12-25 13:37"' % self.wf_name)
        )

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_field_value(trigger, 'Name')
        wf_name = self.get_field_value(trigger, 'Workflow')
        created_at = self.get_field_value(trigger, 'Created at')
        remain = self.get_field_value(trigger, 'Remaining executions')
        next_time = self.get_field_value(trigger, 'Next execution time')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_name, wf_name)
        self.assertIsNotNone(created_at)
        self.assertEqual("4242-12-25 13:37:00", next_time)
        self.assertEqual("5", remain)

        triggers = self.mistral_admin('cron-trigger-list')

        self.assertIn(tr_name, [tr['Name'] for tr in triggers])
        self.assertIn(wf_name, [tr['Workflow'] for tr in triggers])

        self.mistral('cron-trigger-delete', params=tr_name)

        triggers = self.mistral_admin('cron-trigger-list')

        self.assertNotIn(tr_name, [tr['Name'] for tr in triggers])

    def test_two_cron_triggers_for_one_wf(self):
        self.cron_trigger_create('trigger1', self.wf_name, '{}', "5 * * * *")

        self.cron_trigger_create('trigger2', self.wf_name, '{}', "15 * * * *")

        triggers = self.mistral_admin('cron-trigger-list')

        self.assertIn("trigger1", [tr['Name'] for tr in triggers])
        self.assertIn("trigger2", [tr['Name'] for tr in triggers])

    def test_cron_trigger_get(self):
        trigger = self.cron_trigger_create(
            'trigger',
            self.wf_name,
            '{}',
            "5 * * * *"
        )

        self.assertTableStruct(trigger, ['Field', 'Value'])

        fetched_tr = self.mistral_admin(
            'cron-trigger-get',
            params='trigger'
        )

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_field_value(fetched_tr, 'Name')
        wf_name = self.get_field_value(fetched_tr, 'Workflow')
        created_at = self.get_field_value(fetched_tr, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_name, wf_name)
        self.assertIsNotNone(created_at)


class EventTriggerCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with event-triggers."""

    @classmethod
    def setUpClass(cls):
        super(EventTriggerCLITests, cls).setUpClass()

    def setUp(self):
        super(EventTriggerCLITests, self).setUp()

        wf = self.workflow_create(self.wf_def)

        self.wf_id = wf[0]['ID']

    def test_event_trigger_create_delete(self):
        trigger = self.mistral_admin(
            'event-trigger-create',
            params=('trigger %s dummy_exchange dummy_topic event.dummy {}' %
                    self.wf_id))

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_id = self.get_field_value(trigger, 'ID')
        tr_name = self.get_field_value(trigger, 'Name')
        wf_id = self.get_field_value(trigger, 'Workflow ID')
        created_at = self.get_field_value(trigger, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_id, wf_id)
        self.assertIsNotNone(created_at)

        triggers = self.mistral_admin('event-trigger-list')

        self.assertIn(tr_name, [tr['Name'] for tr in triggers])
        self.assertIn(wf_id, [tr['Workflow ID'] for tr in triggers])

        self.mistral('event-trigger-delete', params=tr_id)

        triggers = self.mistral_admin('event-trigger-list')

        self.assertNotIn(tr_name, [tr['Name'] for tr in triggers])

    def test_two_event_triggers_for_one_wf(self):
        self.event_trigger_create('trigger1',
                                  self.wf_id,
                                  'dummy_exchange',
                                  'dummy_topic',
                                  'event.dummy',
                                  '{}')

        self.event_trigger_create('trigger2',
                                  self.wf_id,
                                  'dummy_exchange',
                                  'dummy_topic',
                                  'dummy.event',
                                  '{}')

        triggers = self.mistral_admin('event-trigger-list')

        self.assertIn('trigger1', [tr['Name'] for tr in triggers])
        self.assertIn('trigger2', [tr['Name'] for tr in triggers])

    def test_event_trigger_get(self):
        trigger = self.event_trigger_create('trigger',
                                            self.wf_id,
                                            'dummy_exchange',
                                            'dummy_topic',
                                            'event.dummy.other',
                                            '{}')

        self.assertTableStruct(trigger, ['Field', 'Value'])

        ev_tr_id = self.get_field_value(trigger, 'ID')
        fetched_tr = self.mistral_admin('event-trigger-get', params=ev_tr_id)

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_field_value(fetched_tr, 'Name')
        wf_id = self.get_field_value(fetched_tr, 'Workflow ID')
        created_at = self.get_field_value(fetched_tr, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_id, wf_id)
        self.assertIsNotNone(created_at)


class TaskCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with tasks."""

    def setUp(self):
        super(TaskCLITests, self).setUp()

        wfs = self.workflow_create(self.wf_def)

        self.direct_wf = wfs[0]
        self.reverse_wf = wfs[1]

        self.create_file('input', '{\n    "farewell": "Bye"\n}\n')
        self.create_file('task_name', '{\n    "task_name": "goodbye"\n}\n')

    def test_task_get(self):
        wf_ex = self.execution_create(self.direct_wf['Name'])

        wf_ex_id = self.get_field_value(wf_ex, 'ID')

        tasks = self.mistral_admin('task-list', params=wf_ex_id)

        created_task_id = tasks[-1]['ID']

        fetched_task = self.mistral_admin('task-get', params=created_task_id)
        fetched_task_id = self.get_field_value(fetched_task, 'ID')
        fetched_task_wf_namespace = self.get_field_value(
            fetched_task,
            'Workflow namespace'
        )
        task_execution_id = self.get_field_value(fetched_task, 'Execution ID')

        self.assertEqual(created_task_id, fetched_task_id)
        self.assertEqual('', fetched_task_wf_namespace)
        self.assertEqual(wf_ex_id, task_execution_id)

    def test_task_get_list_within_namespace(self):
        namespace = 'aaa'
        self.workflow_create(self.wf_def, namespace=namespace)
        wf_ex = self.execution_create(
            self.direct_wf['Name'] + ' --namespace ' + namespace
        )

        wf_ex_id = self.get_field_value(wf_ex, 'ID')

        tasks = self.mistral_admin('task-list', params=wf_ex_id)

        created_task_id = tasks[-1]['ID']
        created_wf_namespace = tasks[-1]['Workflow namespace']

        fetched_task = self.mistral_admin('task-get', params=created_task_id)
        fetched_task_id = self.get_field_value(fetched_task, 'ID')
        fetched_task_wf_namespace = self.get_field_value(
            fetched_task,
            'Workflow namespace'
        )
        task_execution_id = self.get_field_value(fetched_task, 'Execution ID')

        self.assertEqual(created_task_id, fetched_task_id)
        self.assertEqual(namespace, created_wf_namespace)
        self.assertEqual(created_wf_namespace, fetched_task_wf_namespace)
        self.assertEqual(wf_ex_id, task_execution_id)

    def test_task_list_with_filter(self):
        wf_exec = self.execution_create(
            "%s input task_name" % self.reverse_wf['Name']
        )

        exec_id = self.get_field_value(wf_exec, 'ID')

        self.assertTrue(self.wait_execution_success(exec_id))

        # Request task executions without filters.
        tasks = self.parser.listing(self.mistral('task-list'))

        self.assertTableStruct(
            tasks,
            ['ID', 'Name', 'Workflow name', 'Execution ID', 'State']
        )

        self.assertEqual(2, len(tasks))

        # Now let's provide a filter.
        tasks = self.parser.listing(
            self.mistral(
                'task-list',
                params='--filter name=goodbye'
            )
        )

        self.assertTableStruct(
            tasks,
            ['ID', 'Name', 'Workflow name', 'Execution ID', 'State']
        )

        self.assertEqual(1, len(tasks))

        self.assertEqual('goodbye', tasks[0]['Name'])

    def test_task_list_with_limit(self):
        wf_exec = self.execution_create(
            "%s input task_name" % self.reverse_wf['Name']
        )

        exec_id = self.get_field_value(wf_exec, 'ID')

        self.assertTrue(self.wait_execution_success(exec_id))

        tasks = self.parser.listing(self.mistral('task-list'))

        tasks = self.parser.listing(
            self.mistral(
                'task-list',
                params='--limit 1'
            )
        )

        self.assertEqual(1, len(tasks))


class ActionCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with actions."""

    @classmethod
    def setUpClass(cls):
        super(ActionCLITests, cls).setUpClass()

    def test_action_create_delete(self):
        init_acts = self.mistral_admin('action-create', params=self.act_def)

        self.assertTableStruct(
            init_acts,
            [
                'Name', 'Is system', 'Input', 'Description', 'Tags',
                'Created at', 'Updated at'
            ]
        )

        self.assertIn('greeting', [action['Name'] for action in init_acts])
        self.assertIn('farewell', [action['Name'] for action in init_acts])

        action_1 = self.get_item_info(
            get_from=init_acts,
            get_by='Name',
            value='greeting'
        )
        action_2 = self.get_item_info(
            get_from=init_acts,
            get_by='Name',
            value='farewell'
        )

        self.assertEqual('<none>', action_1['Tags'])
        self.assertEqual('<none>', action_2['Tags'])

        self.assertEqual('False', action_1['Is system'])
        self.assertEqual('False', action_2['Is system'])

        self.assertEqual('name', action_1['Input'])
        self.assertEqual('None', action_2['Input'])

        acts = self.mistral_admin('action-list')

        self.assertIn(action_1['Name'], [action['Name'] for action in acts])
        self.assertIn(action_2['Name'], [action['Name'] for action in acts])

        self.mistral_admin(
            'action-delete',
            params='{0}'.format(action_1['Name'])
        )
        self.mistral_admin(
            'action-delete',
            params='{0}'.format(action_2['Name'])
        )

        acts = self.mistral_admin('action-list')

        self.assertNotIn(action_1['Name'], [action['Name'] for action in acts])
        self.assertNotIn(action_2['Name'], [action['Name'] for action in acts])

    def test_action_update(self):
        actions = self.action_create(self.act_def)

        created_action = self.get_item_info(
            get_from=actions,
            get_by='Name',
            value='greeting'
        )

        actions = self.mistral_admin('action-update', params=self.act_def)

        updated_action = self.get_item_info(
            get_from=actions,
            get_by='Name',
            value='greeting'
        )

        self.assertEqual(
            created_action['Created at'].split(".")[0],
            updated_action['Created at']
        )
        self.assertEqual(created_action['Name'], updated_action['Name'])
        self.assertEqual(
            created_action['Updated at'],
            updated_action['Updated at']
        )

        actions = self.mistral_admin('action-update', params=self.act_tag_def)

        updated_action = self.get_item_info(
            get_from=actions,
            get_by='Name',
            value='greeting'
        )

        self.assertEqual('tag, tag1', updated_action['Tags'])
        self.assertEqual(
            created_action['Created at'].split(".")[0],
            updated_action['Created at']
        )
        self.assertEqual(created_action['Name'], updated_action['Name'])
        self.assertNotEqual(
            created_action['Updated at'],
            updated_action['Updated at']
        )

    def test_action_update_with_id(self):
        acts = self.action_create(self.act_def)

        created_action = self.get_item_info(
            get_from=acts,
            get_by='Name',
            value='greeting'
        )

        action_id = created_action['ID']

        params = '{0} --id {1}'.format(self.act_tag_def, action_id)
        acts = self.mistral_admin('action-update', params=params)

        updated_action = self.get_item_info(
            get_from=acts,
            get_by='ID',
            value=action_id
        )

        self.assertEqual(
            created_action['Created at'].split(".")[0],
            updated_action['Created at']
        )
        self.assertEqual(created_action['Name'], updated_action['Name'])
        self.assertNotEqual(
            created_action['Updated at'],
            updated_action['Updated at']
        )

    def test_action_update_truncate_input(self):
        input_value = "very_long_input_parameter_name_that_should_be_truncated"

        act_def = """
        version: "2.0"
        action1:
          input:
            - {0}
          base: std.noop
        """.format(input_value)

        self.create_file('action.yaml', act_def)
        self.action_create('action.yaml')

        updated_act = self.mistral_admin('action-update', params='action.yaml')

        updated_act_info = self.get_item_info(
            get_from=updated_act,
            get_by='Name',
            value='action1'
        )

        self.assertEqual(updated_act_info['Input'][:-3], input_value[:25])

    def test_action_get_definition(self):
        self.action_create(self.act_def)

        definition = self.mistral_admin(
            'action-get-definition',
            params='greeting'
        )

        self.assertNotIn('404 Not Found', definition)

    def test_action_get_with_id(self):
        created = self.action_create(self.act_def)

        action_name = created[0]['Name']
        action_id = created[0]['ID']

        fetched = self.mistral_admin('action-get', params=action_id)
        fetched_action_name = self.get_field_value(fetched, 'Name')

        self.assertEqual(action_name, fetched_action_name)

    def test_action_list_with_filter(self):
        actions = self.parser.listing(self.mistral('action-list'))

        self.assertTableStruct(
            actions,
            ['Name', 'Is system', 'Input', 'Description',
             'Tags', 'Created at', 'Updated at']
        )

        # NOTE(rakhmerov): This length isn't really a number of actions.
        # The problem is that one entity in a table may be on more than
        # one lines depending on their data. For example, for the
        # workflows that we use in our tests it works fine and parsing
        # algorithm is able to parse entities correctly even if they are
        # on multiple lines, but for actions it doesn't. So the only thing
        # we can do is only check if unfiltered table is bigger than
        # filtered.
        # We need to think how to improve it.
        unfiltered_len = len(actions)

        self.assertGreater(unfiltered_len, 0)

        # Now let's provide a filter to the list command.
        actions = self.parser.listing(
            self.mistral(
                'action-list',
                params='--filter name=in:std.echo,std.noop'
            )
        )

        self.assertTableStruct(
            actions,
            ['Name', 'Is system', 'Input', 'Description',
             'Tags', 'Created at', 'Updated at']
        )

        self.assertGreater(unfiltered_len, len(actions))

        action_names = [a['Name'] for a in actions]

        self.assertIn('std.echo', action_names)
        self.assertIn('std.noop', action_names)
        self.assertNotIn('std.ssh', action_names)


class EnvironmentCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with environments."""

    def setUp(self):
        super(EnvironmentCLITests, self).setUp()

        self.create_file(
            'env.yaml',
            'name: env\n'
            'description: Test env\n'
            'variables:\n'
            '  var: "value"'
        )

    def test_environment_create(self):
        env = self.mistral_admin('environment-create', params='env.yaml')

        env_name = self.get_field_value(env, 'Name')
        env_desc = self.get_field_value(env, 'Description')

        self.assertTableStruct(env, ['Field', 'Value'])

        envs = self.mistral_admin('environment-list')

        self.assertIn(env_name, [en['Name'] for en in envs])
        self.assertIn(env_desc, [en['Description'] for en in envs])

        self.mistral_admin('environment-delete', params=env_name)

        envs = self.mistral_admin('environment-list')

        self.assertNotIn(env_name, [en['Name'] for en in envs])

    def test_environment_create_without_description(self):
        self.create_file(
            'env_without_des.yaml',
            'name: env\n'
            'variables:\n'
            '  var: "value"'
        )

        env = self.mistral_admin(
            'environment-create',
            params='env_without_des.yaml'
        )

        env_name = self.get_field_value(env, 'Name')
        env_desc = self.get_field_value(env, 'Description')

        self.assertTableStruct(env, ['Field', 'Value'])

        envs = self.mistral_admin('environment-list')

        self.assertIn(env_name, [en['Name'] for en in envs])
        self.assertIn(env_desc, 'None')

        self.mistral_admin('environment-delete', params='env')

        envs = self.mistral_admin('environment-list')

        self.assertNotIn(env_name, [en['Name'] for en in envs])

    def test_environment_update(self):
        env = self.environment_create('env.yaml')

        env_name = self.get_field_value(env, 'Name')
        env_desc = self.get_field_value(env, 'Description')
        env_created_at = self.get_field_value(env, 'Created at')
        env_updated_at = self.get_field_value(env, 'Updated at')

        self.assertIsNotNone(env_created_at)
        self.assertEqual('None', env_updated_at)

        self.create_file(
            'env_upd.yaml',
            'name: env\n'
            'description: Updated env\n'
            'variables:\n'
            '  var: "value"'
        )

        env = self.mistral_admin('environment-update', params='env_upd.yaml')

        self.assertTableStruct(env, ['Field', 'Value'])

        updated_env_name = self.get_field_value(env, 'Name')
        updated_env_desc = self.get_field_value(env, 'Description')
        updated_env_created_at = self.get_field_value(env, 'Created at')
        updated_env_updated_at = self.get_field_value(env, 'Updated at')

        self.assertEqual(env_name, updated_env_name)
        self.assertNotEqual(env_desc, updated_env_desc)
        self.assertEqual('Updated env', updated_env_desc)
        self.assertEqual(env_created_at.split('.')[0], updated_env_created_at)
        self.assertIsNotNone(updated_env_updated_at)

    def test_environment_get(self):
        env = self.environment_create('env.yaml')

        env_name = self.get_field_value(env, 'Name')
        env_desc = self.get_field_value(env, 'Description')

        env = self.mistral_admin('environment-get', params=env_name)

        fetched_env_name = self.get_field_value(env, 'Name')
        fetched_env_desc = self.get_field_value(env, 'Description')

        self.assertTableStruct(env, ['Field', 'Value'])
        self.assertEqual(env_name, fetched_env_name)
        self.assertEqual(env_desc, fetched_env_desc)


class ActionExecutionCLITests(base_v2.MistralClientTestBase):
    """Test suite checks commands to work with action executions."""

    def setUp(self):
        super(ActionExecutionCLITests, self).setUp()

        wfs = self.workflow_create(self.wf_def)

        self.direct_wf = wfs[0]

        direct_wf_exec = self.execution_create(self.direct_wf['Name'])

        self.direct_ex_id = self.get_field_value(direct_wf_exec, 'ID')

    def test_act_execution_get(self):
        self.wait_execution_success(self.direct_ex_id)

        task = self.mistral_admin('task-list', params=self.direct_ex_id)[0]

        act_ex_from_list = self.mistral_admin(
            'action-execution-list',
            params=task['ID']
        )[0]

        act_ex = self.mistral_admin(
            'action-execution-get',
            params=act_ex_from_list['ID']
        )

        wf_name = self.get_field_value(act_ex, 'Workflow name')
        state = self.get_field_value(act_ex, 'State')

        self.assertEqual(
            act_ex_from_list['ID'],
            self.get_field_value(act_ex, 'ID')
        )
        self.assertEqual(self.direct_wf['Name'], wf_name)
        self.assertEqual('SUCCESS', state)

    def test_act_execution_list_with_limit(self):
        self.wait_execution_success(self.direct_ex_id)

        act_execs = self.mistral_admin('action-execution-list')

        # The workflow execution started in setUp()
        # generates 2 action executions.
        self.assertGreater(len(act_execs), 1)

        act_execs = self.mistral_admin(
            'action-execution-list',
            params="--limit 1"
        )

        self.assertEqual(len(act_execs), 1)

        act_ex = act_execs[0]

        self.assertEqual(self.direct_wf['Name'], act_ex['Workflow name'])
        self.assertEqual('SUCCESS', act_ex['State'])

    def test_act_execution_get_list_within_namespace(self):
        namespace = 'bbb'
        self.workflow_create(self.wf_def, namespace=namespace)
        wf_ex = self.execution_create(
            self.direct_wf['Name'] + ' --namespace ' + namespace
        )
        exec_id = self.get_field_value(wf_ex, 'ID')
        self.wait_execution_success(exec_id)
        task = self.mistral_admin('task-list', params=exec_id)[0]

        act_ex_from_list = self.mistral_admin(
            'action-execution-list',
            params=task['ID']
        )[0]

        act_ex = self.mistral_admin(
            'action-execution-get',
            params=act_ex_from_list['ID']
        )

        wf_name = self.get_field_value(act_ex, 'Workflow name')
        wf_namespace = self.get_field_value(act_ex, 'Workflow namespace')
        status = self.get_field_value(act_ex, 'State')

        self.assertEqual(
            act_ex_from_list['ID'],
            self.get_field_value(act_ex, 'ID')
        )
        self.assertEqual(self.direct_wf['Name'], wf_name)
        self.assertEqual('SUCCESS', status)
        self.assertEqual(namespace, wf_namespace)
        self.assertEqual(namespace, act_ex_from_list['Workflow namespace'])

    def test_act_execution_create_delete(self):
        action_ex = self.mistral_admin(
            'run-action',
            params="std.echo '{0}' --save-result".format(
                '{"output": "Hello!"}')
        )

        action_ex_id = self.get_field_value(action_ex, 'ID')

        self.assertTableStruct(action_ex, ['Field', 'Value'])

        name = self.get_field_value(action_ex, 'Name')
        wf_name = self.get_field_value(action_ex, 'Workflow name')
        task_name = self.get_field_value(action_ex, 'Task name')

        self.assertEqual('std.echo', name)
        self.assertEqual('None', wf_name)
        self.assertEqual('None', task_name)

        action_exs = self.mistral_admin('action-execution-list')

        self.assertIn(action_ex_id, [ex['ID'] for ex in action_exs])

        self.mistral_admin('action-execution-delete', params=action_ex_id)

        action_exs = self.mistral_admin('action-execution-list')

        self.assertNotIn(action_ex_id, [ex['ID'] for ex in action_exs])


class NegativeCLITests(base_v2.MistralClientTestBase):
    """This class contains negative tests."""

    def test_wb_list_extra_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-list',
            params='param'
        )

    def test_wb_get_unexist_wb(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-get',
            params='wb'
        )

    def test_wb_get_without_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-get'
        )

    def test_wb_create_same_name(self):
        self.workbook_create(self.wb_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.workbook_create,
            self.wb_def
        )

    def test_wb_create_with_wrong_path_to_definition(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook_create',
            'wb'
        )

    def test_wb_delete_unexist_wb(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-delete',
            params='wb'
        )

    def test_wb_update_wrong_path_to_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-update',
            params='wb'
        )

    def test_wb_update_nonexistant_wb(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-update',
            params=self.wb_with_tags_def
        )

    def test_wb_create_empty_def(self):
        self.create_file('empty')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-create',
            params='empty'
        )

    def test_wb_update_empty_def(self):
        self.create_file('empty')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-update',
            params='empty'
        )

    def test_wb_get_definition_unexist_wb(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-get-definition',
            params='wb'
        )

    def test_wb_create_invalid_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-create',
            params=self.wf_def
        )

    def test_wb_update_invalid_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-update',
            params=self.wf_def
        )

    def test_wb_update_without_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workbook-update'
        )

    def test_wf_list_extra_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-list',
            params='param'
        )

    def test_wf_get_unexist_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-get',
            params='wf'
        )

    def test_wf_get_without_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-get'
        )

    def test_wf_create_without_definition(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-create',
            params=''
        )

    def test_wf_create_with_wrong_path_to_definition(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-create',
            params='wf'
        )

    def test_wf_delete_unexist_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-delete',
            params='wf'
        )

    def test_wf_update_unexist_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-update',
            params='wf'
        )

    def test_wf_get_definition_unexist_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-get-definition',
            params='wf'
        )

    def test_wf_get_definition_missed_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-get-definition'
        )

    def test_wf_create_invalid_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-create',
            params=self.wb_def
        )

    def test_wf_update_invalid_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-update',
            params=self.wb_def
        )

    def test_wf_create_empty_def(self):
        self.create_file('empty')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-create',
            params='empty'
        )

    def test_wf_update_empty_def(self):
        self.create_file('empty')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'workflow-update',
            params='empty'
        )

    def test_ex_list_extra_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-list',
            params='param'
        )

    def test_ex_create_unexist_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-create',
            params='wf'
        )

    def test_ex_create_unexist_task(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-create',
            params='%s param {}' % wf[0]['Name']
        )

    def test_ex_create_with_invalid_input(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-create',
            params="%s input" % wf[0]['Name']
        )

    def test_ex_get_nonexist_execution(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-get',
            params='%s id' % wf[0]['Name']
        )

    def test_ex_create_without_wf_name(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-create'
        )

    def test_ex_create_reverse_wf_without_start_task(self):
        wf = self.workflow_create(self.wf_def)

        self.create_file('input', '{\n    "farewell": "Bye"\n}\n')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-create ',
            params=wf[1]['Name']
        )

    def test_ex_create_missed_input(self):
        self.create_file('empty')

        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-create empty',
            params=wf[1]['Name']
        )

    def test_ex_update_both_state_and_description(self):
        wf = self.workflow_create(self.wf_def)
        execution = self.execution_create(params=wf[0]['Name'])

        exec_id = self.get_field_value(execution, 'ID')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-update',
            params='%s -s ERROR -d update' % exec_id
        )

    def test_ex_delete_nonexistent_execution(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution-delete',
            params='1a2b3c'
        )

    def test_tr_create_without_pattern(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr %s {}' % wf[0]['Name']
        )

    def test_tr_create_invalid_pattern(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr %s {} --pattern "q"' % wf[0]['Name']
        )

    def test_tr_create_invalid_pattern_value_out_of_range(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr %s {} --pattern "80 * * * *"' % wf[0]['Name']
        )

    def test_tr_create_nonexistent_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr wb.wf1 {} --pattern "* * * * *"'
        )

    def test_tr_delete_nonexistant_tr(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-delete',
            params='tr'
        )

    def test_tr_get_nonexistant_tr(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-get',
            params='tr'
        )

    def test_tr_create_invalid_count(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr wb.wf1 {} --pattern "* * * * *" --count q'
        )

    def test_tr_create_negative_count(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr wb.wf1 {} --pattern "* * * * *" --count -1')

    def test_tr_create_invalid_first_date(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr wb.wf1 {} --pattern "* * * * *" --first-date "q"'
        )

    def test_tr_create_count_only(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr wb.wf1 {} --count 42'
        )

    def test_tr_create_date_and_count_without_pattern(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'cron-trigger-create',
            params='tr wb.wf1 {} --count 42 --first-time "4242-12-25 13:37"'
        )

    def test_event_tr_create_missing_argument(self):
        wf = self.workflow_create(self.wf_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'event-trigger-create',
            params='tr %s exchange topic' % wf[0]['ID']
        )

    def test_event_tr_create_nonexistent_wf(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'event-trigger-create',
            params='456 4307362e-4a4a-4021-aa58-0fab23c9c751 '
                   'exchange topic event {} '
        )

    def test_event_tr_delete_nonexistent_tr(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'event-trigger-delete',
            params='789'
        )

    def test_event_tr_get_nonexistent_tr(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'event-trigger-get',
            params='789'
        )

    def test_action_get_nonexistent(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral,
            'action-get',
            params='nonexist'
        )

    def test_action_double_creation(self):
        self.action_create(self.act_def)

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-create',
            params='{0}'.format(self.act_def)
        )

    def test_action_create_without_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-create',
            params=''
        )

    def test_action_create_invalid_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-create',
            params='{0}'.format(self.wb_def)
        )

    def test_action_delete_nonexistent_act(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-delete',
            params='nonexist'
        )

    def test_action_delete_standard_action(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-delete',
            params='heat.events_get'
        )

    def test_action_get_definition_nonexistent_action(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-get-definition',
            params='nonexist'
        )

    def test_task_get_nonexistent_task(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'task-get',
            params='nonexist'
        )

    def test_env_get_without_param(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-get'
        )

    def test_env_get_nonexistent(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-get',
            params='nonexist'
        )

    def test_env_create_same_name(self):
        self.create_file(
            'env.yaml',
            'name: env\n'
            'description: Test env\n'
            'variables:\n'
            '  var: "value"'
        )

        self.environment_create('env.yaml')

        self.assertRaises(
            exceptions.CommandFailed,
            self.environment_create,
            'env.yaml'
        )

    def test_env_create_empty(self):
        self.create_file('env.yaml')

        self.assertRaises(
            exceptions.CommandFailed,
            self.environment_create,
            'env.yaml'
        )

    def test_env_create_with_wrong_path_to_definition(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'execution_create',
            'env'
        )

    def test_env_delete_unexist_env(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-delete',
            params='env'
        )

    def test_env_update_wrong_path_to_def(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-update',
            params='env'
        )

    def test_env_update_empty(self):
        self.create_file('env.yaml')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-update',
            params='env'
        )

    def test_env_update_nonexistant_env(self):
        self.create_file(
            'env.yaml',
            'name: env'
            'variables:\n  var: "value"'
        )

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-update',
            params='env.yaml'
        )

    def test_env_create_without_name(self):
        self.create_file('env.yaml', 'variables:\n  var: "value"')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-create',
            params='env.yaml'
        )

    def test_env_create_without_variables(self):
        self.create_file('env.yaml', 'name: env')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'environment-create',
            params='env.yaml'
        )

    def test_action_execution_get_without_params(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-execution-get'
        )

    def test_action_execution_get_unexistent_obj(self):
        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-execution-get',
            params='123456'
        )

    def test_action_execution_update(self):
        wfs = self.workflow_create(self.wf_def)
        direct_wf_exec = self.execution_create(wfs[0]['Name'])

        direct_ex_id = self.get_field_value(direct_wf_exec, 'ID')

        self.assertRaises(
            exceptions.CommandFailed,
            self.mistral_admin,
            'action-execution-update',
            params='%s ERROR' % direct_ex_id
        )

    def test_target_action_execution(self):
        command = (
            '--debug '
            '--os-target-tenant-name={tenantname} '
            '--os-target-username={username} '
            '--os-target-password="{password}" '
            '--os-target-auth-url="{auth_url}" '
            '--target_insecure '
            'run-action heat.stacks_list'
        ).format(
            tenantname=self.clients.tenant_name,
            username=self.clients.username,
            password=self.clients.password,
            auth_url=self.clients.uri
        )

        self.mistral_alt_user(cmd=command)
