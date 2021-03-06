# Copyright 2014 - Mirantis, Inc.
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

import mock

from highlanderclient.api.v2 import workflows
from highlanderclient.commands.v2 import workflows as workflow_cmd
from highlanderclient import exceptions as exc
from highlanderclient.tests.unit import base


WORKFLOW_DICT = {
    'name': 'a',
    'tags': ['a', 'b'],
    'input': 'param',
    'created_at': '1',
    'updated_at': '1'
}

WF_DEF = """
version: '2.0'

flow:
  tasks:
    task1:
      action: nova.servers_get server="1"
"""

WF_WITH_DEF_DICT = WORKFLOW_DICT.copy()
WF_WITH_DEF_DICT.update({'definition': WF_DEF})
WORKFLOW = workflows.Workflow(mock, WORKFLOW_DICT)
WORKFLOW_WITH_DEF = workflows.Workflow(mock, WF_WITH_DEF_DICT)


class TestCLIWorkflowsV2(base.BaseCommandTest):
    @mock.patch('argparse.open', create=True)
    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.create')
    def test_create(self, mock, mock_open):
        mock.return_value = (WORKFLOW,)

        result = self.call(workflow_cmd.Create, app_args=['1.txt'])

        self.assertEqual([('a', 'a, b', 'param', '1', '1')], result[1])

    @mock.patch('argparse.open', create=True)
    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.update')
    def test_update(self, mock, mock_open):
        mock.return_value = (WORKFLOW,)

        result = self.call(workflow_cmd.Update, app_args=['1.txt'])

        self.assertEqual([('a', 'a, b', 'param', '1', '1')], result[1])

    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.list')
    def test_list(self, mock):
        mock.return_value = (WORKFLOW,)

        result = self.call(workflow_cmd.List)

        self.assertEqual([('a', 'a, b', 'param', '1', '1')], result[1])

    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.get')
    def test_get(self, mock):
        mock.return_value = WORKFLOW

        result = self.call(workflow_cmd.Get, app_args=['name'])

        self.assertEqual(('a', 'a, b', 'param', '1', '1'), result[1])

    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.delete')
    def test_delete(self, del_mock):
        self.call(workflow_cmd.Delete, app_args=['name'])

        del_mock.assert_called_once_with('name')

    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.delete')
    def test_delete_with_multi_names(self, del_mock):
        self.call(workflow_cmd.Delete, app_args=['name1', 'name2'])

        self.assertEqual(2, del_mock.call_count)
        self.assertEqual(
            [mock.call('name1'), mock.call('name2')],
            del_mock.call_args_list
        )

    @mock.patch('highlanderclient.api.v2.workflows.'
                'WorkflowManager.get')
    def test_get_definition(self, mock):
        mock.return_value = WORKFLOW_WITH_DEF

        self.call(workflow_cmd.GetDefinition, app_args=['name'])

        self.app.stdout.write.assert_called_with(WF_DEF)

    @mock.patch('argparse.open', create=True)
    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.validate')
    def test_validate(self, mock, mock_open):
        mock.return_value = {'valid': True}
        mock_open.return_value = mock.MagicMock(spec=file)

        result = self.call(workflow_cmd.Validate, app_args=['wf.yaml'])

        self.assertEqual(result[0], tuple())
        self.assertEqual(result[1], tuple())

    @mock.patch('argparse.open', create=True)
    @mock.patch('highlanderclient.api.v2.workflows.WorkflowManager.validate')
    def test_validate_failed(self, mock, mock_open):
        mock.return_value = {'valid': False, 'error': 'Invalid DSL...'}
        mock_open.return_value = mock.MagicMock(spec=file)

        self.assertRaises(exc.HighlanderClientException,
                          self.call,
                          workflow_cmd.Validate,
                          app_args=['wf.yaml'])
