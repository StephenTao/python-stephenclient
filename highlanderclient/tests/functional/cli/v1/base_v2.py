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
import time

from tempest_lib import exceptions

from highlanderclient.tests.functional.cli import base


HIGHLANDER_URL = "http://localhost:8989/v1"


class HighlanderClientTestBase(base.HighlanderCLIAuth, base.HighlanderCLIAltAuth):

    _highlander_url = HIGHLANDER_URL

    @classmethod
    def setUpClass(cls):
        super(HighlanderClientTestBase, cls).setUpClass()

        cls.wb_def = os.path.relpath(
            'functionaltests/resources/v1/wb_v1.yaml', os.getcwd())

        cls.wb_with_tags_def = os.path.relpath(
            'functionaltests/resources/v1/wb_with_tags_v1.yaml', os.getcwd())

        cls.wf_def = os.path.relpath(
            'functionaltests/resources/v1/wf_v1.yaml', os.getcwd())

        cls.wf_with_delay_def = os.path.relpath(
            'functionaltests/resources/v1/wf_delay_v1.yaml', os.getcwd())

        cls.act_def = os.path.relpath(
            'functionaltests/resources/v1/action_v1.yaml', os.getcwd())

        cls.act_tag_def = os.path.relpath(
            'functionaltests/resources/v1/action_v1_tags.yaml', os.getcwd())

    def setUp(self):
        super(HighlanderClientTestBase, self).setUp()

    def get_value_of_field(self, obj, field):
        return [o['Value'] for o in obj
                if o['Field'] == "{0}".format(field)][0]

    def get_item_info(self, get_from, get_by, value):
        return [i for i in get_from if i[get_by] == value][0]

    def highlander_admin(self, cmd, params=""):
        self.clients = self._get_admin_clients()
        return self.parser.listing(self.highlander(
            '{0}'.format(cmd), params='{0}'.format(params)))

    def highlander_alt_user(self, cmd, params=""):
        self.clients = self._get_alt_clients()
        return self.parser.listing(self.highlander_alt(
            '{0}'.format(cmd), params='{0}'.format(params)))

    def highlander_cli(self, admin, cmd, params):
        if admin:
            return self.highlander_admin(cmd, params)
        else:
            return self.highlander_alt_user(cmd, params)
    def mccleod_create(self, wb_def, admin=True):
            mc = self.highlander_cli(
                admin,
                'mccleod-create',
                params='{0}'.format(wb_def))
            mc_name = self.get_value_of_field(wb, "Name")
            self.addCleanup(self.highlander_cli,
                            admin,
                            'mccleod-delete',
                            params=mc_name)
            return mc
    def workbook_create(self, wb_def, admin=True):
        wb = self.highlander_cli(
            admin,
            'workbook-create',
            params='{0}'.format(wb_def))
        wb_name = self.get_value_of_field(wb, "Name")
        self.addCleanup(self.highlander_cli,
                        admin,
                        'workbook-delete',
                        params=wb_name)
        self.addCleanup(self.highlander_cli,
                        admin,
                        'workflow-delete',
                        params='wb.wf1')

        return wb

    def workflow_create(self, wf_def, admin=True):
        wf = self.highlander_cli(
            admin,
            'workflow-create',
            params='{0}'.format(wf_def))
        for workflow in wf:
            self.addCleanup(self.highlander_cli,
                            admin,
                            'workflow-delete',
                            params=workflow['Name'])

        return wf

    def action_create(self, act_def, admin=True):
        acts = self.highlander_cli(
            admin,
            'action-create',
            params='{0}'.format(act_def))
        for action in acts:
            self.addCleanup(self.highlander_cli,
                            admin,
                            'action-delete',
                            params=action['Name'])

        return acts

    def cron_trigger_create(self, name, wf_name, wf_input, pattern=None,
                            count=None, first_time=None, admin=True):
        optional_params = ""
        if pattern:
            optional_params += ' --pattern "{}"'.format(pattern)
        if count:
            optional_params += ' --count {}'.format(count)
        if first_time:
            optional_params += ' --first-time "{}"'.format(first_time)
        trigger = self.highlander_cli(
            admin,
            'cron-trigger-create',
            params='{} {} {} {}'.format(name, wf_name, wf_input,
                                        optional_params))
        self.addCleanup(self.highlander_cli,
                        admin,
                        'cron-trigger-delete',
                        params=name)

        return trigger

    def execution_create(self, params, admin=True):
        ex = self.highlander_cli(admin, 'execution-create', params=params)
        exec_id = self.get_value_of_field(ex, 'ID')
        self.addCleanup(self.highlander_cli,
                        admin,
                        'execution-delete',
                        params=exec_id)

        return ex

    def environment_create(self, params, admin=True):
        env = self.highlander_cli(admin, 'environment-create', params=params)
        env_name = self.get_value_of_field(env, 'Name')
        self.addCleanup(self.highlander_cli,
                        admin,
                        'environment-delete',
                        params=env_name)

        return env

    def create_file(self, file_name, file_body=""):
        f = open(file_name, 'w')
        f.write(file_body)
        f.close()
        self.addCleanup(os.remove, file_name)

    def wait_execution_success(self, exec_id, timeout=180):
        start_time = time.time()

        ex = self.highlander_admin('execution-get', params=exec_id)
        exec_state = self.get_value_of_field(ex, 'State')

        expected_states = ['SUCCESS', 'RUNNING']

        while exec_state != 'SUCCESS':
            if time.time() - start_time > timeout:
                msg = ("Execution exceeds timeout {0} to change state "
                       "to SUCCESS. Execution: {1}".format(timeout, ex))
                raise exceptions.TimeoutException(msg)

            ex = self.highlander_admin('execution-get', params=exec_id)
            exec_state = self.get_value_of_field(ex, 'State')

            if exec_state not in expected_states:
                msg = ("Execution state %s is not in expected "
                       "states: %s" % (exec_state, expected_states))
                raise exceptions.TempestException(msg)

            time.sleep(2)

        return True
