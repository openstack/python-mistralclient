# -*- coding: utf-8 -*-
#
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


class MistralClientException(Exception):
    """Base Exception for Mistral client

    To correctly use this class, inherit from it and define
    a 'message' and 'code' properties.
    """
    message = "An unknown exception occurred"
    code = "UNKNOWN_EXCEPTION"

    def __str__(self):
        return self.message

    def __init__(self, message=message):
        self.message = message
        super(MistralClientException, self).__init__(
            '%s: %s' % (self.code, self.message))


class IllegalArgumentException(MistralClientException):
    message = "IllegalArgumentException occurred"
    code = "ILLEGAL_ARGUMENT_EXCEPTION"

    def __init__(self, message=None):
        if message:
            self.message = message
