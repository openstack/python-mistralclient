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

from tempest_lib import exceptions

from mistralclient.tests.functional.cli import base


MISTRAL_URL = "http://localhost:8989/v2"


class SimpleMistralCLITests(base.MistralCLIAuth):
    """Basic tests, check '-list', '-help' commands."""

    _mistral_url = MISTRAL_URL

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
                               ['Name', 'Tags', 'Input',
                                'Created at', 'Updated at'])

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

    def test_cron_trigger_list(self):
        triggers = self.parser.listing(
            self.mistral('cron-trigger-list'))
        self.assertTableStruct(triggers,
                               ['Name', 'Pattern', 'Workflow',
                                'Next execution time',
                                'Created at', 'Updated at'])

    def test_actions_list(self):
        actions = self.parser.listing(
            self.mistral('action-list'))
        self.assertTableStruct(actions,
                               ['Name', 'Is system', 'Input',
                                'Description', 'Tags', 'Created at',
                                'Updated at'])


class ClientTestBase(base.MistralCLIAuth):

    _mistral_url = MISTRAL_URL

    @classmethod
    def setUpClass(cls):
        super(ClientTestBase, cls).setUpClass()

        cls.wb_def = os.path.relpath(
            'functionaltests/resources/v2/wb_v2.yaml', os.getcwd())

        cls.wb_with_tags_def = os.path.relpath(
            'functionaltests/resources/v2/wb_with_tags_v2.yaml', os.getcwd())

        cls.wf_def = os.path.relpath(
            'functionaltests/resources/v2/wf_v2.yaml', os.getcwd())

        cls.act_def = os.path.relpath(
            'functionaltests/resources/v2/action_v2.yaml', os.getcwd())

    def setUp(self):
        super(ClientTestBase, self).setUp()

        self.actions = []

    def tearDown(self):
        super(ClientTestBase, self).tearDown()

        for object in ['execution', 'workflow', 'workbook', 'cron-trigger']:
            objects = self.mistral_command('{0}-list'.format(object))
            if object == 'execution':
                identifiers = [obj['ID'] for obj in objects]
            else:
                identifiers = [obj['Name'] for obj in objects]
            for id in identifiers:
                if id != "<none>":
                    self.mistral('{0}-delete'.format(object), params=id)

        for act in self.actions:
            self.mistral('action-delete', params=act)
        del self.actions

    def get_value_of_field(self, obj, field):
        return [o['Value'] for o in obj
                if o['Field'] == "{0}".format(field)][0]

    def get_item_info(self, get_from, get_by, value):
        return [i for i in get_from if i[get_by] == value][0]

    def mistral_command(self, cmd, params=""):
        return self.parser.listing(self.mistral('{0}'.format(cmd),
                                                params='{0}'.format(params)))


class WorkbookCLITests(ClientTestBase):
    """Test suite checks commands to work with workbooks."""

    @classmethod
    def setUpClass(cls):
        super(WorkbookCLITests, cls).setUpClass()

    def test_workbook_create_delete(self):
        wb = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_def))
        self.assertTableStruct(wb, ['Field', 'Value'])

        wfs = self.mistral_command('workflow-list')
        self.assertIn('wb.wf1', [wf['Name'] for wf in wfs])

        name = self.get_value_of_field(wb, "Name")
        self.assertEqual('wb', name)

        wbs = self.mistral_command('workbook-list')
        self.assertIn('wb', [workbook['Name'] for workbook in wbs])

        self.mistral_command('workbook-delete', params='wb')

        wbs = self.mistral_command('workbook-list')
        self.assertNotIn('wb', [workbook['Name'] for workbook in wbs])

    def test_workbook_update(self):
        wb = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_def))

        tags = self.get_value_of_field(wb, 'Tags')
        self.assertNotIn('tag', tags)

        wb = self.mistral_command(
            'workbook-update', params='{0}'.format(self.wb_with_tags_def))
        self.assertTableStruct(wb, ['Field', 'Value'])

        name = self.get_value_of_field(wb, 'Name')
        tags = self.get_value_of_field(wb, 'Tags')

        self.assertEqual('wb', name)
        self.assertIn('tag', tags)

    def test_workbook_get(self):
        created = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_with_tags_def))
        fetched = self.mistral_command('workbook-get', params='wb')

        created_wb_name = self.get_value_of_field(created, 'Name')
        fetched_wb_name = self.get_value_of_field(fetched, 'Name')

        self.assertEqual(created_wb_name, fetched_wb_name)

        created_wb_tag = self.get_value_of_field(created, 'Tags')
        fetched_wb_tag = self.get_value_of_field(fetched, 'Tags')

        self.assertEqual(created_wb_tag, fetched_wb_tag)

    def test_workbook_get_definition(self):
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))

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
            'workflow-create', params='{0}'.format(self.wf_def))
        self.assertTableStruct(wf, ['Name', 'Created at', 'Updated at'])

        self.assertEqual('wf', wf[0]['Name'])

        wfs = self.mistral_command('workflow-list')
        self.assertIn('wf', [workflow['Name'] for workflow in wfs])

        self.mistral_command('workflow-delete', params='wf')
        wfs = self.mistral_command('workflow-list')
        self.assertNotIn('wf', [workflow['Name'] for workflow in wfs])

    def test_workflow_update(self):
        self.mistral(
            'workflow-create', params='{0}'.format(self.wf_def))

        wf = self.mistral_command(
            'workflow-update', params='{0}'.format(self.wf_def))
        self.assertTableStruct(wf, ['Name', 'Created at', 'Updated at'])

        self.assertEqual('wf', wf[0]['Name'])

    def test_workflow_get(self):
        created = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))

        fetched = self.mistral_command('workflow-get', params='wf')
        created_wf_name = created[0]['Name']
        fetched_wf_name = self.get_value_of_field(fetched, 'Name')

        self.assertEqual(created_wf_name, fetched_wf_name)

    def test_workflow_get_definition(self):
        self.mistral(
            'workflow-create', params='{0}'.format(self.wf_def))

        definition = self.mistral_command(
            'workflow-get-definition', params='wf')
        self.assertNotIn('404 Not Found', definition)


class ExecutionCLITests(ClientTestBase):
    """Test suite checks commands to work with executions."""

    def setUp(self):
        super(ExecutionCLITests, self).setUp()

        self.mistral(
            'workbook-create', params='{0}'.format(self.wb_def))

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
            'execution-update', params='{0} "PAUSED"'.format(exec_id))

        updated_exec_id = self.get_value_of_field(execution, 'ID')
        status = self.get_value_of_field(execution, 'State')

        self.assertEqual(exec_id, updated_exec_id)
        self.assertEqual('PAUSED', status)

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


class TriggerCLITests(ClientTestBase):
    """Test suite checks commands to work with triggers."""

    def setUp(self):
        super(TriggerCLITests, self).setUp()

        self.mistral(
            'workbook-create', params='{0}'.format(self.wb_def))

    def tearDown(self):
        super(TriggerCLITests, self).tearDown()

    def test_trigger_create_delete(self):
        trigger = self.mistral_command(
            'cron-trigger-create', params='trigger "5 * * * *" wb.wf1 {}')

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(trigger, 'Name')
        wf_name = self.get_value_of_field(trigger, 'Workflow')
        created_at = self.get_value_of_field(trigger, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual('wb.wf1', wf_name)
        self.assertIsNotNone(created_at)

        trgs = self.mistral_command('cron-trigger-list')
        self.assertIn(tr_name, [tr['Name'] for tr in trgs])
        self.assertIn(wf_name, [tr['Workflow'] for tr in trgs])

        self.mistral('cron-trigger-delete', params='{0}'.format(tr_name))

        trgs = self.mistral_command('cron-trigger-list')
        self.assertNotIn(tr_name, [tr['Name'] for tr in trgs])

    def test_two_triggers_for_one_wf(self):
        self.mistral(
            'cron-trigger-create', params='trigger1 "5 * * * *" wb.wf1 {}')

        self.mistral(
            'cron-trigger-create', params='trigger2 "15 * * * *" wb.wf1 {}')

        trgs = self.mistral_command('cron-trigger-list')
        self.assertIn("trigger1", [tr['Name'] for tr in trgs])
        self.assertIn("trigger2", [tr['Name'] for tr in trgs])

        self.mistral('cron-trigger-delete', params='trigger1')
        self.mistral('cron-trigger-delete', params='trigger2')

    def test_trigger_get(self):
        trigger = self.mistral_command(
            'cron-trigger-create', params='trigger "5 * * * *" wb.wf1 {}')

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(trigger, 'Name')

        fetched_tr = self.mistral_command(
            'cron-trigger-get', params='trigger')

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(fetched_tr, 'Name')
        wf_name = self.get_value_of_field(fetched_tr, 'Workflow')
        created_at = self.get_value_of_field(fetched_tr, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual('wb.wf1', wf_name)
        self.assertIsNotNone(created_at)

        self.mistral('cron-trigger-delete', params='{0}'.format(tr_name))


class ActionCLITests(ClientTestBase):
    """Test suite checks commands to work with actions."""

    @classmethod
    def setUpClass(cls):
        super(ActionCLITests, cls).setUpClass()

    def test_action_create_delete(self):
        acts = self.mistral_command(
            'action-create', params='{0}'.format(self.act_def))
        self.assertTableStruct(acts, ['Name', 'Is system', 'Input',
                                      'Description', 'Tags',
                                      'Created at', 'Updated at'])

        self.assertIn('greeting', [action['Name'] for action in acts])
        self.assertIn('farewell', [action['Name'] for action in acts])

        action_1 = self.get_item_info(
            get_from=acts, get_by='Name', value='greeting')
        action_2 = self.get_item_info(
            get_from=acts, get_by='Name', value='farewell')

        self.assertEqual(action_1['Tags'], 'hello')
        self.assertEqual(action_2['Tags'], '<none>')

        self.assertEqual(action_1['Is system'], 'False')
        self.assertEqual(action_2['Is system'], 'False')

        self.assertEqual(action_1['Input'], 'name')
        self.assertEqual(action_2['Input'], '')

        acts = self.mistral_command('action-list')
        self.assertIn(action_1['Name'], [action['Name'] for action in acts])
        self.assertIn(action_2['Name'], [action['Name'] for action in acts])

        self.mistral_command(
            'action-delete', params='{0}'.format(action_1['Name']))
        self.mistral_command(
            'action-delete', params='{0}'.format(action_2['Name']))

        acts = self.mistral_command('action-list')
        self.assertNotIn(action_1['Name'], [action['Name'] for action in acts])
        self.assertNotIn(action_2['Name'], [action['Name'] for action in acts])

    def test_action_update(self):
        acts = self.mistral_command(
            'action-create', params='{0}'.format(self.act_def))

        self.actions.extend([action['Name'] for action in acts])

        created_action = self.get_item_info(
            get_from=acts, get_by='Name', value='greeting')

        acts = self.mistral_command(
            'action-update', params='{0}'.format(self.act_def))

        updated_action = self.get_item_info(
            get_from=acts, get_by='Name', value='greeting')

        self.assertEqual(created_action['Created at'].split(".")[0],
                         updated_action['Created at'])
        self.assertEqual(created_action['Name'], updated_action['Name'])
        self.assertNotEqual(created_action['Updated at'],
                            updated_action['Updated at'])

    def test_action_get_definition(self):
        acts = self.mistral_command(
            'action-create', params='{0}'.format(self.act_def))

        self.actions.extend([action['Name'] for action in acts])

        definition = self.mistral_command(
            'action-get-definition', params='greeting')
        self.assertNotIn('404 Not Found', definition)


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
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-create',
                          params='{0}'.format(self.wb_def))

    def test_wb_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workbook-create', params='wb')

    def test_wb_delete_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-delete', params='wb')

    def test_wb_update_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workbook-update', params='wb')

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
                          'workflow-create', params='')

    def test_wf_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'workflow-create', params='wf')

    def test_wf_delete_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-delete', params='wf')

    def test_wf_update_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'workflow-update', params='wf')

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
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'execution-create', params='wb param {}')

    def test_ex_create_with_invalid_input(self):
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'execution-create', params="wb.wf1 input")

    def test_ex_get_nonexist_execution(self):
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-get', params='wb.wf1 id')

    def test_tr_create_without_pattern(self):
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'cron-trigger-create', params='tr "" wb.wf1 {}')

    def test_tr_create_invalid_pattern(self):
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'cron-trigger-create', params='tr "q" wb.wf1 {}')

    def test_tr_create_invalid_pattern_value_out_of_range(self):
        self.mistral('workbook-create', params='{0}'.format(self.wb_def))
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'cron-trigger-create',
                          params='tr "88 * * * *" wb.wf1 {}')

    def test_tr_create_nonexistent_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'cron-trigger-create',
                          params='tr "* * * * *" wb.wf1 {}')

    def test_tr_delete_nonexistant_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'cron-trigger-delete', params='tr')

    def test_tr_get_nonexistant_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'cron-trigger-get', params='tr')

    def test_action_get_nonexistent(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'action-get', params='nonexist')

    def test_action_double_creation(self):
        acts = self.mistral_command(
            'action-create', params='{0}'.format(self.act_def))
        self.actions.extend([action['Name'] for action in acts])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'action-create',
                          params='{0}'.format(self.act_def))

    def test_action_create_without_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'action-create',
                          params='')

    def test_action_create_invalid_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'action-create',
                          params='{0}'.format(self.wb_def))

    def test_action_delete_nonexistent_act(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'action-delete',
                          params='nonexist')

    def test_action_delete_standard_action(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'action-delete',
                          params='heat.events_get')

    def test_action_get_definition_nonexistent_action(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'action-get-definition',
                          params='nonexist')
