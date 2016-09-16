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

from mistralclient.api.v2 import client as client_v2


def client(auth_type='keystone', **kwargs):
    return client_v2.Client(auth_type=auth_type, **kwargs)


def determine_client_version(mistral_version):
    if mistral_version.find("v2") != -1:
        return 2

    raise RuntimeError("Cannot determine mistral API version")
