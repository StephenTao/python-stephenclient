# Copyright 2015 - StackStorm, Inc.
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

import argparse
import logging

from cliff import command
from cliff import show

from highlanderclient.api.v1 import maccleods
from highlanderclient.commands.v1 import base
from highlanderclient import exceptions as exc
from highlanderclient import utils


LOG = logging.getLogger(__name__)


def format(maccleod=None):
    columns = (
        'Name',
        'dialog',
        'Created at',
        'Updated at'
    )

    if maccleod:
        data = (
            maccleod.name,
            ', '.join(maccleod.dialog or '') or '<none>',
            maccleod.created_at,
        )

        if hasattr(maccleod, 'updated_at'):
            data += (maccleod.updated_at,)
        else:
            data += (None,)

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class List(base.HighlanderLister):
    """List all maccleods dialog."""

    def _get_format_function(self):
        return format

    def _get_resources(self, parsed_args):
        return maccleods.MaccleodManager(self.app.client).list()


class Get(show.ShowOne):
    """Show specific maccleod."""

    def get_parser(self, prog_name):
        parser = super(Get, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            help='Maccleod name'
        )

        return parser

    def take_action(self, parsed_args):
        maccleod = maccleods.MaccleodManager(self.app.client).get(
            parsed_args.name)

        return format(maccleod)


class Create(show.ShowOne):
    """Create new maccleod."""

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='Maccleod definition file'
        )

        return parser

    def take_action(self, parsed_args):
        maccleod = maccleods.MaccleodManager(self.app.client).create(
            parsed_args.definition.read())

        return format(maccleod)


class Delete(command.Command):
    """Delete maccleod."""

    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument('name', nargs='+', help='Name of maccleod(s).')

        return parser

    def take_action(self, parsed_args):
        wb_mgr = maccleods.MaccleodManager(self.app.client)
        utils.do_action_on_many(
            lambda s: wb_mgr.delete(s),
            parsed_args.name,
            "Request to delete macCleod %s has been accepted.",
            "Unable to delete the specified macCleod(s)."
        )


class Update(show.ShowOne):
    """Update maccleod."""

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='maccleod definition file'
        )

        return parser

    def take_action(self, parsed_args):
        maccleod = maccleods.MaccleodManager(self.app.client).update(
            parsed_args.definition.read())

        return format(maccleod)


class GetDefinition(command.Command):
    """Show maccleod definition."""

    def get_parser(self, prog_name):
        parser = super(GetDefinition, self).get_parser(prog_name)

        parser.add_argument('name', help='maccleod name')

        return parser

    def take_action(self, parsed_args):
        definition = maccleods.MaccleodManager(self.app.client).get(
            parsed_args.name).definition

        self.app.stdout.write(definition or "\n")


class Validate(show.ShowOne):
    """Validate maccleod."""

    def get_parser(self, prog_name):
        parser = super(Validate, self).get_parser(prog_name)

        parser.add_argument(
            'definition',
            type=argparse.FileType('r'),
            help='maccleod definition file'
        )

        return parser

    def take_action(self, parsed_args):
        result = maccleods.MaccleodManager(self.app.client).validate(
            parsed_args.definition.read())

        if not result.get('valid', None):
            raise exc.HighlanderClientException(
                result.get('error', 'Unknown exception.'))

        return tuple(), tuple()
