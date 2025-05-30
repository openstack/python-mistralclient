# Copyright 2014 - Mirantis, Inc.
# Copyright 2020 - Nokia Software.
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
import datetime
import textwrap

from osc_lib.command import command
from oslo_utils import timeutils


DEFAULT_LIMIT = 100


class MistralFormatter(metaclass=abc.ABCMeta):
    COLUMNS = []

    @classmethod
    def fields(cls):
        # Column should be a tuple:
        # (<field name>, <field title>, <optional synthetic flag>)
        # If the 3rd value is specified and it's True then
        # the field is synthetic (calculated) and should not be requested
        # from the API client.
        return [c[0] for c in cls.COLUMNS if len(c) == 2 or not c[2]]

    @classmethod
    def headings(cls):
        return [c[1] for c in cls.COLUMNS]

    @classmethod
    def format_list(cls, instance=None):
        return cls.format(instance, lister=True)

    @staticmethod
    def format(instance=None, lister=False):
        pass


class MistralLister(command.Lister, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _get_format_function(self):
        raise NotImplementedError

    def get_parser(self, parsed_args):
        parser = super(MistralLister, self).get_parser(parsed_args)

        parser.add_argument(
            '--marker',
            type=str,
            help='The last execution uuid of the previous page, displays list '
                 'of executions after "marker".',
            default='',
            nargs='?'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of entries to return in a single result. ',
            nargs='?'
        )
        parser.add_argument(
            '--sort_keys',
            help='Comma-separated list of sort keys to sort results by. '
                 'Default: created_at. '
                 'Example: mistral execution-list --sort_keys=id,description',
            default='created_at',
            nargs='?'
        )
        parser.add_argument(
            '--sort_dirs',
            help='Comma-separated list of sort directions. Default: asc. '
                 'Example: mistral execution-list --sort_keys=id,description '
                 '--sort_dirs=asc,desc',
            default='asc',
            nargs='?'
        )
        parser.add_argument(
            '--filter',
            dest='filters',
            action='append',
            help='Filters. Can be repeated.'
        )

        return parser

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


class MistralExecutionLister(MistralLister, metaclass=abc.ABCMeta):
    def get_parser(self, parsed_args):
        parser = super(MistralExecutionLister, self).get_parser(parsed_args)
        parser.set_defaults(limit=DEFAULT_LIMIT)
        parser.add_argument(
            '--oldest',
            help='Display the executions starting from the oldest entries '
                 'instead of the newest',
            default=False,
            action='store_true'
        )

        return parser

    def take_action(self, parsed_args):
        self._validate_parsed_args(parsed_args)

        f = self._get_format_function()

        reverse_results = False
        if (parsed_args.marker == '' and parsed_args.sort_dirs == 'asc' and
            parsed_args.sort_keys == 'created_at' and
                not parsed_args.oldest):
            reverse_results = True
            parsed_args.sort_dirs = 'desc'

        ret = self._get_resources(parsed_args)
        if not isinstance(ret, list):
            ret = [ret]

        if reverse_results:
            ret.reverse()

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


def get_duration_str(start_dt_str, end_dt_str):
    """Builds a human friendly duration string.

    :param start_dt_str: Start date time as an ISO string.
    :param end_dt_str: End date time as an ISO string. If empty, duration is
        calculated from the current time.
    :return: Duration(delta) string.
    """
    if not start_dt_str:
        return ''

    start_dt = datetime.datetime.strptime(start_dt_str, '%Y-%m-%d %H:%M:%S')

    if end_dt_str:
        end_dt = datetime.datetime.strptime(end_dt_str, '%Y-%m-%d %H:%M:%S')

        return str(end_dt - start_dt)

    delta_from_now = timeutils.utcnow() - start_dt

    # If delta is too small then we won't show any value. It means that
    # the corresponding process (e.g. an execution) just started.
    if delta_from_now < datetime.timedelta(seconds=2):
        return '...'

    # Drop microseconds to decrease verbosity.
    delta = (
        delta_from_now
        - datetime.timedelta(microseconds=delta_from_now.microseconds)
    )

    return "{}...".format(delta)
