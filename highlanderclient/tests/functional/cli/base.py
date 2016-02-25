# Copyright (c) 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

from tempest import config
from tempest_lib.cli import base

CONF = config.CONF


class HighlanderCLIAuth(base.ClientTestBase):

    _highlander_url = None

    def _get_admin_clients(self):
        clients = base.CLIClient(
            username=CONF.identity.admin_username,
            password=CONF.identity.admin_password,
            tenant_name=CONF.identity.admin_tenant_name,
            uri=CONF.identity.uri,
            cli_dir='/usr/local/bin')

        return clients

    def _get_clients(self):
        return self._get_admin_clients()

    def highlander(self, action, flags='', params='', fail_ok=False):
        """Executes Highlander command."""
        highlander_url_op = "--os-highlander-url %s" % self._highlander_url

        if 'WITHOUT_AUTH' in os.environ:
            return base.execute(
                'highlander %s' % highlander_url_op, action, flags, params,
                fail_ok, merge_stderr=False, cli_dir='')
        else:
            return self.clients.cmd_with_auth(
                'highlander %s' % highlander_url_op, action, flags, params,
                fail_ok)


class HighlanderCLIAltAuth(base.ClientTestBase):

    _highlander_url = None

    def _get_alt_clients(self):
        clients = base.CLIClient(
            username=CONF.identity.alt_username,
            password=CONF.identity.alt_password,
            tenant_name=CONF.identity.alt_tenant_name,
            uri=CONF.identity.uri,
            cli_dir='/usr/local/bin')

        return clients

    def _get_clients(self):
        return self._get_alt_clients()

    def highlander_alt(self, action, flags='', params='', mode='alt_user'):
        """Executes Highlander command for alt_user from alt_tenant."""
        highlander_url_op = "--os-highlander-url %s" % self._highlander_url

        return self.clients.cmd_with_auth(
            'highlander %s' % highlander_url_op, action, flags, params)
