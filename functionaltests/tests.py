from base import MistralBase


class Workbooks(MistralBase):

    def test_get_workbook_list(self):
        wbs = self.mistral_client.workbooks.list()
        self.assertIsInstance(wbs, list)

    def test_create_workbook(self):
        wbs = self.mistral_client.workbooks.list()
        self.mistral_client.workbooks.create("new_wb")
        wbs_with_new_wb = self.mistral_client.workbooks.list()

        self.assertEqual(len(wbs)+1, len(wbs_with_new_wb))
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
        received_definition = \
            self.mistral_client.workbooks.get_definition("wb")

        self.assertEqual(self.definition, received_definition)
