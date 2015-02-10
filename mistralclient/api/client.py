# Copyright 2013 - Mirantis, Inc.
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

import six

from mistralclient.api.v1 import client as client_v1
from mistralclient.api.v2 import client as client_v2


def client(mistral_url=None, username=None, api_key=None,
           project_name=None, auth_url=None, project_id=None,
           endpoint_type='publicURL', service_type='workflow',
           auth_token=None, user_id=None, cacert=None):

        if mistral_url and not isinstance(mistral_url, six.string_types):
            raise RuntimeError('Mistral url should be string')

        if not mistral_url:
            mistral_url = "http://localhost:8989/v2"

        version = determine_client_version(mistral_url)

        if version == 1:
            client_cls = client_v1.Client
        else:
            client_cls = client_v2.Client

        return client_cls(mistral_url=mistral_url, username=username,
                          api_key=api_key, project_name=project_name,
                          auth_url=auth_url, project_id=project_id,
                          endpoint_type=endpoint_type,
                          service_type=service_type, auth_token=auth_token,
                          user_id=user_id, cacert=cacert)


def determine_client_version(mistral_url):
    if mistral_url.find("v2") != -1:
        return 2
    elif mistral_url.find("v1") != -1:
        return 1

    raise RuntimeError("Can not determine mistral API version")
