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

from base import MistralBase


class MistralURLDefine(MistralBase):

    _mistral_url = "http://localhost:8989/v1"


class Workbooks(MistralURLDefine):

    def test_get_workbook_list(self):
        wbs = self.mistral_client.workbooks.list()
        self.assertIsInstance(wbs, list)

    def test_create_workbook(self):
        wbs = self.mistral_client.workbooks.list()
        self.mistral_client.workbooks.create("new_wb")
        wbs_with_new_wb = self.mistral_client.workbooks.list()

        self.assertEqual(len(wbs) + 1, len(wbs_with_new_wb))
        self.assertTrue(self.assert_item_in_list(
            wbs_with_new_wb, name="new_wb"))

    def test_get_workbook(self):
        received_wb = self.mistral_client.workbooks.get("wb")
        self.assertEqual(self.wb.name, received_wb.name)

    def test_update_workbook(self):
        updated_wb = self.mistral_client.workbooks.update(
            "wb", "New Description", ["tags"])

        self.assertEqual(self.wb.name, updated_wb.name)
        self.assertEqual("New Description", updated_wb.description)
        self.assertEqual(["tags"], updated_wb.tags)

    def test_upload_get_definition(self):
        self.mistral_client.workbooks.upload_definition("wb", self.definition)
        received_definition = (self.mistral_client.
                               workbooks.get_definition("wb"))

        self.assertEqual(self.definition, received_definition)


class Executions(MistralURLDefine):

    def test_create_execution(self):
        execution = self.create_execution()
        self.assertEqual("wb", execution.workbook_name)
        self.assertNotEqual(execution.id, None)

    def test_update_execution(self):
        execution = self.create_execution()
        updated_exec = self.mistral_client.executions.update(
            "wb", execution.id, "ERROR")
        self.assertEqual("ERROR", updated_exec.state)
        updated_exec = self.mistral_client.executions.update(
            None, execution.id, "SUCCESS")
        self.assertEqual("SUCCESS", updated_exec.state)

    def test_list_executions(self):
        execution = self.create_execution()
        exec_list = self.mistral_client.executions.list(None)
        self.assertTrue(self.assert_item_in_list(
            exec_list, id=execution.id))
        exec_list = self.mistral_client.executions.list("wb")
        self.assertTrue(self.assert_item_in_list(
            exec_list, id=execution.id, workbook_name="wb"))

    def test_get_execution(self):
        execution = self.create_execution()
        received_exec = self.mistral_client.executions.get(None, execution.id)
        self.assertEqual(execution.id, received_exec.id)
        received_exec = self.mistral_client.executions.get("wb", execution.id)
        self.assertEqual(execution.id, received_exec.id)


class Tasks(MistralURLDefine):

    def test_list_tasks(self):
        execution = self.create_execution()
        tasks_list = self.mistral_client.tasks.list(None, None)
        self.assertIsInstance(tasks_list, list)
        tasks_list = self.mistral_client.tasks.list(
            execution.workbook_name, None)
        self.assertIsInstance(tasks_list, list)
        tasks_list = self.mistral_client.tasks.list(None, execution.id)
        self.assertIsInstance(tasks_list, list)
        tasks_list = self.mistral_client.tasks.list(
            execution.workbook_name, execution.id)
        self.assertIsInstance(tasks_list, list)

    def test_get_task(self):
        execution = self.create_execution()
        task = self.mistral_client.tasks.list(None, None)[-1]
        received_task = self.mistral_client.tasks.get(None, None, task.id)
        self.assertIsNotNone(received_task)
        task = self.mistral_client.tasks.list("wb", None)[-1]
        received_task = self.mistral_client.tasks.get("wb", None, task.id)
        self.assertIsNotNone(received_task)
        task = self.mistral_client.tasks.list(None, execution.id)[-1]
        received_task = self.mistral_client.tasks.get(
            None, execution.id, task.id)
        self.assertIsNotNone(received_task)
        task = self.mistral_client.tasks.list("wb", execution.id)[-1]
        received_task = self.mistral_client.tasks.get(
            "wb", execution.id, task.id)
        self.assertIsNotNone(received_task)
