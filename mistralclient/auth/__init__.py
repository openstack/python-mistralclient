# Copyright 2016 - Brocade Communications Systems, Inc.
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

import abc

from stevedore import driver


def get_auth_handler(auth_type):
    mgr = driver.DriverManager(
        'mistralclient.auth',
        auth_type,
        invoke_on_load=True
    )

    return mgr.driver


class AuthHandler(metaclass=abc.ABCMeta):
    """Abstract base class for an authentication plugin."""

    @abc.abstractmethod
    def authenticate(self, req):
        raise NotImplementedError()
