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

import copy
import datetime
import json
import os
import tempfile

import mock
import yaml

from highlanderclient.api.v2 import environments
from highlanderclient.commands.v2 import environments as environment_cmd
from highlanderclient.tests.unit import base


ENVIRONMENT_DICT = {
    'name': 'env1',
    'description': 'Test Environment #1',
    'scope': 'private',
    'variables': {
        'server': 'localhost',
        'database': 'test',
        'timeout': 600,
        'verbose': True
    },
    'created_at': str(datetime.datetime.utcnow()),
    'updated_at': str(datetime.datetime.utcnow())
}

ENVIRONMENT = environments.Environment(mock, ENVIRONMENT_DICT)
EXPECTED_RESULT = (ENVIRONMENT_DICT['name'],
                   ENVIRONMENT_DICT['description'],
                   json.dumps(ENVIRONMENT_DICT['variables'], indent=4),
                   ENVIRONMENT_DICT['scope'],
                   ENVIRONMENT_DICT['created_at'],
                   ENVIRONMENT_DICT['updated_at'])


class TestCLIEnvironmentsV2(base.BaseCommandTest):

    @mock.patch('highlanderclient.api.v2.environments.EnvironmentManager.create')
    def _test_create(self, content, mock):
        mock.return_value = ENVIRONMENT

        with tempfile.NamedTemporaryFile() as f:
            f.write(content)
            f.flush()
            file_path = os.path.abspath(f.name)
            result = self.call(environment_cmd.Create, app_args=[file_path])
            self.assertEqual(EXPECTED_RESULT, result[1])

    def test_create_from_json(self):
        self._test_create(json.dumps(ENVIRONMENT_DICT, indent=4))

    def test_create_from_yaml(self):
        yml = yaml.dump(ENVIRONMENT_DICT, default_flow_style=False)
        self._test_create(yml)

    @mock.patch('highlanderclient.api.v2.environments.EnvironmentManager.update')
    def _test_update(self, content, mock):
        mock.return_value = ENVIRONMENT

        with tempfile.NamedTemporaryFile() as f:
            f.write(content)
            f.flush()
            file_path = os.path.abspath(f.name)
            result = self.call(environment_cmd.Update, app_args=[file_path])
            self.assertEqual(EXPECTED_RESULT, result[1])

    def test_update_from_json(self):
        env = copy.deepcopy(ENVIRONMENT_DICT)
        del env['created_at']
        del env['updated_at']
        self._test_update(json.dumps(env, indent=4))

    def test_update_from_yaml(self):
        env = copy.deepcopy(ENVIRONMENT_DICT)
        del env['created_at']
        del env['updated_at']
        yml = yaml.dump(env, default_flow_style=False)
        self._test_update(yml)

    @mock.patch('highlanderclient.api.v2.environments.EnvironmentManager.list')
    def test_list(self, mock):
        mock.return_value = (ENVIRONMENT,)
        expected = (ENVIRONMENT_DICT['name'],
                    ENVIRONMENT_DICT['description'],
                    ENVIRONMENT_DICT['scope'],
                    ENVIRONMENT_DICT['created_at'],
                    ENVIRONMENT_DICT['updated_at'])

        result = self.call(environment_cmd.List)

        self.assertListEqual([expected], result[1])

    @mock.patch('highlanderclient.api.v2.environments.EnvironmentManager.get')
    def test_get(self, mock):
        mock.return_value = ENVIRONMENT

        result = self.call(environment_cmd.Get, app_args=['name'])

        self.assertEqual(EXPECTED_RESULT, result[1])

    @mock.patch('highlanderclient.api.v2.environments.EnvironmentManager.delete')
    def test_delete(self, del_mock):
        self.call(environment_cmd.Delete, app_args=['name'])

        del_mock.assert_called_once_with('name')

    @mock.patch('highlanderclient.api.v2.environments.EnvironmentManager.delete')
    def test_delete_with_multi_names(self, del_mock):
        self.call(environment_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, del_mock.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            del_mock.call_args_list
        )
