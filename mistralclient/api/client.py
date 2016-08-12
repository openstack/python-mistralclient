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

from mistralclient.api.v2 import client as client_v2
from mistralclient.auth import auth_types


def client(mistral_url=None, username=None, api_key=None,
           project_name=None, auth_url=None, project_id=None,
           endpoint_type='publicURL', service_type='workflow',
           auth_token=None, user_id=None, cacert=None, insecure=False,
           profile=None, auth_type=auth_types.KEYSTONE, client_id=None,
           client_secret=None, target_username=None, target_api_key=None,
           target_project_name=None, target_auth_url=None,
           target_project_id=None, target_auth_token=None,
           target_user_id=None, target_cacert=None, target_insecure=False,
           **kwargs):

        if mistral_url and not isinstance(mistral_url, six.string_types):
            raise RuntimeError('Mistral url should be a string.')

        return client_v2.Client(
            mistral_url=mistral_url,
            username=username,
            api_key=api_key,
            project_name=project_name,
            auth_url=auth_url,
            project_id=project_id,
            endpoint_type=endpoint_type,
            service_type=service_type,
            auth_token=auth_token,
            user_id=user_id,
            cacert=cacert,
            insecure=insecure,
            profile=profile,
            auth_type=auth_type,
            client_id=client_id,
            client_secret=client_secret,
            target_username=target_username,
            target_api_key=target_api_key,
            target_project_name=target_project_name,
            target_auth_url=target_auth_url,
            target_project_id=target_project_id,
            target_auth_token=target_auth_token,
            target_user_id=target_user_id,
            target_cacert=target_cacert,
            target_insecure=target_insecure,
            **kwargs
        )


def determine_client_version(mistral_version):
    if mistral_version.find("v2") != -1:
        return 2

    raise RuntimeError("Can not determine mistral API version")
