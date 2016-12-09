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

import json
import os.path
import tempfile
import yaml

from mistralclient import utils
from oslotest import base


ENV_DICT = {'k1': 'abc', 'k2': 123, 'k3': True}
ENV_STR = json.dumps(ENV_DICT)
ENV_YAML = yaml.safe_dump(ENV_DICT, default_flow_style=False)


class UtilityTest(base.BaseTestCase):

    def test_load_empty(self):
        self.assertDictEqual(dict(), utils.load_content(None))
        self.assertDictEqual(dict(), utils.load_content(''))
        self.assertDictEqual(dict(), utils.load_content('{}'))
        self.assertListEqual(list(), utils.load_content('[]'))

    def test_load_json_content(self):
        self.assertDictEqual(ENV_DICT, utils.load_content(ENV_STR))

    def test_load_json_file(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(ENV_STR.encode('utf-8'))
            f.flush()
            file_path = os.path.abspath(f.name)

            self.assertDictEqual(ENV_DICT, utils.load_file(file_path))

    def test_load_yaml_content(self):
        self.assertDictEqual(ENV_DICT, utils.load_content(ENV_YAML))

    def test_load_yaml_file(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(ENV_YAML.encode('utf-8'))
            f.flush()
            file_path = os.path.abspath(f.name)

            self.assertDictEqual(ENV_DICT, utils.load_file(file_path))

    def test_load_json(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(ENV_STR.encode('utf-8'))
            f.flush()
            self.assertDictEqual(ENV_DICT, utils.load_json(f.name))

        self.assertDictEqual(ENV_DICT, utils.load_json(ENV_STR))
