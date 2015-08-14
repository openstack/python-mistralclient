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

from mistralclient.api.v2 import services
from mistralclient.tests.unit.v2 import base


SERVICE = {
    'name': 'service_name',
    'type': 'service_type',
}

URL_TEMPLATE = '/services'


class TestServicesV2(base.BaseClientV2Test):
    def test_list(self):
        mock = self.mock_http_get(content={'services': [SERVICE]})

        service_list = self.services.list()

        self.assertEqual(1, len(service_list))

        srv = service_list[0]

        self.assertDictEqual(
            services.Service(self.services, SERVICE).to_dict(),
            srv.to_dict()
        )

        mock.assert_called_once_with(URL_TEMPLATE)
