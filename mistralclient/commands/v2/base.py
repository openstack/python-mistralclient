# Copyright 2014 - Mirantis, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import abc
import textwrap

from osc_lib.command import command
import six


@six.add_metaclass(abc.ABCMeta)
class MistralLister(command.Lister):
    @abc.abstractmethod
    def _get_format_function(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_resources(self, parsed_args):
        """Gets a list of API resources (e.g. using client)."""
        raise NotImplementedError

    def _validate_parsed_args(self, parsed_args):
        # No-op by default.
        pass

    def take_action(self, parsed_args):
        self._validate_parsed_args(parsed_args)

        f = self._get_format_function()

        ret = self._get_resources(parsed_args)
        if not isinstance(ret, list):
            ret = [ret]

        data = [f(r)[1] for r in ret]

        if data:
            return f()[0], data
        else:
            return f()


def cut(string, length=25):
    if string and len(string) > length:
        return "%s..." % string[:length]
    else:
        return string


def wrap(string, width=25):
    if string and len(string) > width:
        return textwrap.fill(string, width)
    else:
        return string


def get_filters(parsed_args):
    filters = {}

    if parsed_args.filters:
        for f in parsed_args.filters:
            arr = f.split('=')

            if len(arr) != 2:
                raise ValueError('Invalid filter: %s' % f)

            filters[arr[0]] = arr[1]

    return filters
