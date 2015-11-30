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

import logging

from mistralclient.commands.v2 import base


LOG = logging.getLogger(__name__)


def format_list(service=None):
    columns = ('Name', 'Type')

    if service:
        data = (service.name, service.type)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.MistralLister):
    """List all services."""

    def _get_format_function(self):
        return format_list

    def _get_resources(self, parsed_args):
        mistral_client = self.app.client_manager.workflow_engine
        return mistral_client.services.list()
