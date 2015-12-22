# Copyright 2015 Huawei Technologies Co., Ltd.
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

from mistralclient.api.v2 import services
from mistralclient.commands.v2 import services as service_cmd
from mistralclient.tests.unit import base


SERVICE_DICT = {
    'name': 'service_name',
    'type': 'service_type',
}

SERVICE = services.Service(mock, SERVICE_DICT)


class TestCLIServicesV2(base.BaseCommandTest):
    def test_list(self):
        self.client.services.list.return_value = [SERVICE]
        expected = (SERVICE_DICT['name'], SERVICE_DICT['type'],)

        result = self.call(service_cmd.List)

        self.assertListEqual([expected], result[1])
