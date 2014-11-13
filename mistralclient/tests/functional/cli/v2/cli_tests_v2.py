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

        cls.wf_with_delay_def = os.path.relpath(
            'functionaltests/resources/v2/wf_delay_v2.yaml', os.getcwd())

        cls.act_def = os.path.relpath(
            'functionaltests/resources/v2/action_v2.yaml', os.getcwd())

    def setUp(self):
        super(ClientTestBase, self).setUp()

        self.actions = []
        self.executions = []
        self.workflows = []
        self.workbooks = []
        self.cron_triggers = []

    def tearDown(self):
        super(ClientTestBase, self).tearDown()

        del self.actions
        del self.executions
        del self.workflows
        del self.workbooks
        del self.cron_triggers

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

    def tearDown(self):
        for wb in self.workbooks:
            self.mistral('workbook-delete', params=wb)

        super(WorkbookCLITests, self).tearDown()

    def test_workbook_create_delete(self):
        wb = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_def))
        wb_name = self.get_value_of_field(wb, "Name")
        self.workbooks.append(wb_name)
        self.assertTableStruct(wb, ['Field', 'Value'])

        wbs = self.mistral_command('workbook-list')
        self.assertIn(wb_name, [workbook['Name'] for workbook in wbs])

        wbs = self.mistral_command('workbook-list')
        self.assertIn(wb_name, [workbook['Name'] for workbook in wbs])

        self.mistral_command('workbook-delete', params=wb_name)

        wbs = self.mistral_command('workbook-list')
        self.assertNotIn(wb_name, [workbook['Name'] for workbook in wbs])
        self.workbooks.remove(wb_name)

    def test_workbook_update(self):
        wb = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_def))
        wb_name = self.get_value_of_field(wb, "Name")
        self.workbooks.append(wb_name)

        tags = self.get_value_of_field(wb, 'Tags')
        self.assertNotIn('tag', tags)

        wb = self.mistral_command(
            'workbook-update', params='{0}'.format(self.wb_with_tags_def))
        self.assertTableStruct(wb, ['Field', 'Value'])

        name = self.get_value_of_field(wb, 'Name')
        tags = self.get_value_of_field(wb, 'Tags')

        self.assertEqual(wb_name, name)
        self.assertIn('tag', tags)

    def test_workbook_get(self):
        created = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_with_tags_def))
        wb_name = self.get_value_of_field(created, "Name")
        self.workbooks.append(wb_name)

        fetched = self.mistral_command('workbook-get', params=wb_name)

        created_wb_name = self.get_value_of_field(created, 'Name')
        fetched_wb_name = self.get_value_of_field(fetched, 'Name')

        self.assertEqual(created_wb_name, fetched_wb_name)

        created_wb_tag = self.get_value_of_field(created, 'Tags')
        fetched_wb_tag = self.get_value_of_field(fetched, 'Tags')

        self.assertEqual(created_wb_tag, fetched_wb_tag)

    def test_workbook_get_definition(self):
        wb = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_def))
        wb_name = self.get_value_of_field(wb, "Name")
        self.workbooks.append(wb_name)

        definition = self.mistral_command(
            'workbook-get-definition', params=wb_name)
        self.assertNotIn('404 Not Found', definition)


class WorkflowCLITests(ClientTestBase):
    """Test suite checks commands to work with workflows."""

    @classmethod
    def setUpClass(cls):
        super(WorkflowCLITests, cls).setUpClass()

    def tearDown(self):
        for wf in self.workflows:
            self.mistral('workflow-delete', params=wf)

        super(WorkflowCLITests, self).tearDown()

    def test_workflow_create_delete(self):
        init_wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        wf_name = init_wf[0]['Name']
        self.workflows.extend([workflow['Name'] for workflow in init_wf])
        self.assertTableStruct(init_wf, ['Name', 'Created at', 'Updated at'])

        wfs = self.mistral_command('workflow-list')
        self.assertIn(wf_name, [workflow['Name'] for workflow in wfs])

        self.mistral_command('workflow-delete', params=wf_name)

        wfs = self.mistral_command('workflow-list')
        self.assertNotIn(wf_name, [workflow['Name'] for workflow in wfs])
        for w in [workflow['Name'] for workflow in init_wf]:
            self.workflows.remove(w)

    def test_workflow_update(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        wf_name = wf[0]['Name']
        self.workflows.extend([workflow['Name'] for workflow in wf])

        upd_wf = self.mistral_command(
            'workflow-update', params='{0}'.format(self.wf_def))
        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        self.assertEqual(wf_name, upd_wf[0]['Name'])

    def test_workflow_get(self):
        created = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        wf_name = created[0]['Name']
        self.workflows.extend([workflow['Name'] for workflow in created])

        fetched = self.mistral_command('workflow-get', params=wf_name)
        fetched_wf_name = self.get_value_of_field(fetched, 'Name')
        self.assertEqual(wf_name, fetched_wf_name)

    def test_workflow_get_definition(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        wf_name = wf[0]['Name']
        self.workflows.extend([workflow['Name'] for workflow in wf])

        definition = self.mistral_command(
            'workflow-get-definition', params=wf_name)
        self.assertNotIn('404 Not Found', definition)


class ExecutionCLITests(ClientTestBase):
    """Test suite checks commands to work with executions."""

    @classmethod
    def setUpClass(cls):
        super(ExecutionCLITests, cls).setUpClass()

    def setUp(self):
        super(ExecutionCLITests, self).setUp()

        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.wf_name = wf[0]['Name']
        self.workflows.extend([workflow['Name'] for workflow in wf])

        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_with_delay_def))
        self.wf_with_delay_name = wf[0]['Name']
        self.workflows += [self.wf_with_delay_name]

    def tearDown(self):
        for ex in self.executions:
            self.mistral('execution-delete', params=ex)

        self.mistral('workflow-delete', params=self.wf_name)
        self.mistral('workflow-delete', params=self.wf_with_delay_name)

        super(ExecutionCLITests, self).tearDown()

    def test_execution_create_delete(self):
        execution = self.mistral_command(
            'execution-create', params=self.wf_name)

        exec_id = self.get_value_of_field(execution, 'ID')
        self.executions.append(exec_id)
        self.assertTableStruct(execution, ['Field', 'Value'])

        wf = self.get_value_of_field(execution, 'Workflow')
        created_at = self.get_value_of_field(execution, 'Created at')

        self.assertEqual(self.wf_name, wf)
        self.assertIsNotNone(created_at)

        execs = self.mistral_command('execution-list')
        self.assertIn(exec_id, [ex['ID'] for ex in execs])
        self.assertIn(wf, [ex['Workflow'] for ex in execs])
        self.assertIn('SUCCESS', [ex['State'] for ex in execs])

        self.mistral_command('execution-delete', params=exec_id)
        self.executions.remove(exec_id)

    def test_execution_update(self):
        execution = self.mistral_command(
            'execution-create', params=self.wf_with_delay_name)
        exec_id = self.get_value_of_field(execution, 'ID')
        self.executions.append(exec_id)

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
            'execution-create', params=self.wf_name)

        exec_id = self.get_value_of_field(execution, 'ID')
        self.executions.append(exec_id)

        execution = self.mistral_command(
            'execution-get', params='{0}'.format(exec_id))

        gotten_id = self.get_value_of_field(execution, 'ID')
        wf = self.get_value_of_field(execution, 'Workflow')

        self.assertEqual(exec_id, gotten_id)
        self.assertEqual(self.wf_name, wf)

    def test_execution_get_input(self):
        execution = self.mistral_command(
            'execution-create', params=self.wf_name)

        exec_id = self.get_value_of_field(execution, 'ID')
        self.executions.append(exec_id)

        ex_input = self.mistral_command('execution-get-input', params=exec_id)
        self.assertEqual([], ex_input)

    def test_execution_get_output(self):
        execution = self.mistral_command(
            'execution-create', params=self.wf_name)

        exec_id = self.get_value_of_field(execution, 'ID')
        self.executions.append(exec_id)

        ex_output = self.mistral_command(
            'execution-get-output', params=exec_id)
        self.assertEqual([], ex_output)


class CronTriggerCLITests(ClientTestBase):
    """Test suite checks commands to work with cron-triggers."""

    @classmethod
    def setUpClass(cls):
        super(CronTriggerCLITests, cls).setUpClass()

    def setUp(self):
        super(CronTriggerCLITests, self).setUp()

        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.wf_name = wf[0]['Name']
        self.workflows.append(self.wf_name)

    def tearDown(self):
        for tr in self.cron_triggers:
            self.mistral('cron-trigger-delete', params=tr)

        self.mistral('workflow-delete', params=self.wf_name)

        super(CronTriggerCLITests, self).tearDown()

    def test_cron_trigger_create_delete(self):
        trigger = self.mistral_command(
            'cron-trigger-create',
            params='trigger "5 * * * *" %s {}' % self.wf_name)
        cron_tr_name = 'trigger'
        self.cron_triggers.append(cron_tr_name)
        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(trigger, 'Name')
        wf_name = self.get_value_of_field(trigger, 'Workflow')
        created_at = self.get_value_of_field(trigger, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_name, wf_name)
        self.assertIsNotNone(created_at)

        trgs = self.mistral_command('cron-trigger-list')
        self.assertIn(tr_name, [tr['Name'] for tr in trgs])
        self.assertIn(wf_name, [tr['Workflow'] for tr in trgs])

        self.mistral('cron-trigger-delete', params='{0}'.format(tr_name))

        trgs = self.mistral_command('cron-trigger-list')
        self.assertNotIn(tr_name, [tr['Name'] for tr in trgs])
        self.cron_triggers.remove(cron_tr_name)

    def test_two_cron_triggers_for_one_wf(self):
        self.mistral(
            'cron-trigger-create',
            params='trigger1 "5 * * * *" %s {}' % self.wf_name)
        self.cron_triggers.append('trigger1')
        self.mistral(
            'cron-trigger-create',
            params='trigger2 "15 * * * *" %s {}' % self.wf_name)
        self.cron_triggers.append('trigger2')

        trgs = self.mistral_command('cron-trigger-list')
        self.assertIn("trigger1", [tr['Name'] for tr in trgs])
        self.assertIn("trigger2", [tr['Name'] for tr in trgs])

        self.mistral('cron-trigger-delete', params='trigger1')
        self.mistral('cron-trigger-delete', params='trigger2')

        self.cron_triggers.remove('trigger1')
        self.cron_triggers.remove('trigger2')

    def test_cron_trigger_get(self):
        trigger = self.mistral_command(
            'cron-trigger-create',
            params='trigger "5 * * * *" %s {}' % self.wf_name)
        self.cron_triggers.append('trigger')
        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(trigger, 'Name')

        fetched_tr = self.mistral_command(
            'cron-trigger-get', params='trigger')

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(fetched_tr, 'Name')
        wf_name = self.get_value_of_field(fetched_tr, 'Workflow')
        created_at = self.get_value_of_field(fetched_tr, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_name, wf_name)
        self.assertIsNotNone(created_at)

        self.mistral('cron-trigger-delete', params='{0}'.format(tr_name))
        self.cron_triggers.remove('trigger')


class ActionCLITests(ClientTestBase):
    """Test suite checks commands to work with actions."""

    @classmethod
    def setUpClass(cls):
        super(ActionCLITests, cls).setUpClass()

    def tearDown(self):
        for act in self.actions:
            self.mistral('action-delete', params=act)

        super(ActionCLITests, self).tearDown()

    def test_action_create_delete(self):
        init_acts = self.mistral_command(
            'action-create', params='{0}'.format(self.act_def))
        self.actions.extend([action['Name'] for action in init_acts])
        self.assertTableStruct(init_acts, ['Name', 'Is system', 'Input',
                                           'Description', 'Tags',
                                           'Created at', 'Updated at'])

        self.assertIn('greeting', [action['Name'] for action in init_acts])
        self.assertIn('farewell', [action['Name'] for action in init_acts])

        action_1 = self.get_item_info(
            get_from=init_acts, get_by='Name', value='greeting')
        action_2 = self.get_item_info(
            get_from=init_acts, get_by='Name', value='farewell')

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
        for a in [action['Name'] for action in init_acts]:
            self.actions.remove(a)

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

    def tearDown(self):
        for wb in self.workbooks:
            self.mistral('workbook-delete', params=wb)

        for cron_tr in self.cron_triggers:
            self.mistral('cron-trigger-delete', params=cron_tr)

        for wf in self.workflows:
            self.mistral('workflow-delete', params=wf)

        for act in self.actions:
            self.mistral('action-delete', params=act)

        super(NegativeCLITests, self).tearDown()

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
        wb = self.mistral_command(
            'workbook-create', params='{0}'.format(self.wb_def))
        wb_name = self.get_value_of_field(wb, "Name")
        self.workbooks.append(wb_name)
        self.workflows.append('wb.wf1')
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
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.workflows.append(wf[0]['Name'])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-create',
                          params='%s param {}' % wf[0]['Name'])

    def test_ex_create_with_invalid_input(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.workflows.append(wf[0]['Name'])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-create',
                          params="%s input" % wf[0]['Name'])

    def test_ex_get_nonexist_execution(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.workflows.append(wf[0]['Name'])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'execution-get',
                          params='%s id' % wf[0]['Name'])

    def test_tr_create_without_pattern(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.workflows.append(wf[0]['Name'])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'cron-trigger-create',
                          params='tr "" %s {}' % wf[0]['Name'])

    def test_tr_create_invalid_pattern(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.workflows.append(wf[0]['Name'])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'cron-trigger-create',
                          params='tr "q" %s {}' % wf[0]['Name'])

    def test_tr_create_invalid_pattern_value_out_of_range(self):
        wf = self.mistral_command(
            'workflow-create', params='{0}'.format(self.wf_def))
        self.workflows.append(wf[0]['Name'])
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'cron-trigger-create',
                          params='tr "88 * * * *" %s {}' % wf[0]['Name'])

    def test_tr_create_nonexistent_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral, 'cron-trigger-create',
                          params='tr "* * * * *" wb.wf1 {}')

    def test_tr_delete_nonexistant_tr(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.mistral,
                          'cron-trigger-delete', params='tr')

    def test_tr_get_nonexistant_tr(self):
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
