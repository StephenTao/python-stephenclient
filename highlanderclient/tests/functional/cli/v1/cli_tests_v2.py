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

from tempest_lib import decorators
from tempest_lib import exceptions

from highlanderclient.tests.functional.cli import base
from highlanderclient.tests.functional.cli.v1 import base_v1


HIGHLANDER_URL = "http://localhost:8989/v1"


class SimpleHighlanderCLITests(base.HighlanderCLIAuth):
    """Basic tests, check '-list', '-help' commands."""

    _highlander_url = HIGHLANDER_URL

    @classmethod
    def setUpClass(cls):
        super(SimpleHighlanderCLITests, cls).setUpClass()

    def test_workbooks_list(self):
        workbooks = self.parser.listing(self.highlander('workbook-list'))
        self.assertTableStruct(
            workbooks,
            ['Name', 'Tags', 'Created at', 'Updated at']
        )

    def test_workflow_list(self):
        workflows = self.parser.listing(
            self.highlander('workflow-list'))
        self.assertTableStruct(
            workflows,
            ['Name', 'Tags', 'Input', 'Created at', 'Updated at']
        )

    def test_executions_list(self):
        executions = self.parser.listing(
            self.highlander('execution-list'))
        self.assertTableStruct(
            executions,
            ['ID', 'Workflow', 'State', 'Created at', 'Updated at']
        )

    def test_tasks_list(self):
        tasks = self.parser.listing(
            self.highlander('task-list'))
        self.assertTableStruct(
            tasks,
            ['ID', 'Name', 'Workflow name', 'Execution ID', 'State']
        )

    def test_cron_trigger_list(self):
        triggers = self.parser.listing(
            self.highlander('cron-trigger-list'))
        self.assertTableStruct(
            triggers,
            ['Name', 'Workflow', 'Pattern', 'Next execution time',
             'Remaining executions', 'Created at', 'Updated at']
        )

    def test_actions_list(self):
        actions = self.parser.listing(
            self.highlander('action-list'))
        self.assertTableStruct(
            actions,
            ['Name', 'Is system', 'Input', 'Description',
             'Tags', 'Created at', 'Updated at']
        )

    def test_environments_list(self):
        envs = self.parser.listing(
            self.highlander('environment-list'))
        self.assertTableStruct(
            envs,
            ['Name', 'Description', 'Scope', 'Created at', 'Updated at']
        )

    def test_action_execution_list(self):
        act_execs = self.parser.listing(
            self.highlander('action-execution-list'))
        self.assertTableStruct(
            act_execs,
            ['ID', 'Name', 'Workflow name', 'State',
             'State info', 'Is accepted']
        )


class WorkbookCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with workbooks."""

    @classmethod
    def setUpClass(cls):
        super(WorkbookCLITests, cls).setUpClass()

    def test_workbook_create_delete(self):
        wb = self.highlander_admin(
            'workbook-create', params=self.wb_def)
        wb_name = self.get_value_of_field(wb, "Name")

        self.assertTableStruct(wb, ['Field', 'Value'])

        wbs = self.highlander_admin('workbook-list')
        self.assertIn(wb_name, [workbook['Name'] for workbook in wbs])

        wbs = self.highlander_admin('workbook-list')
        self.assertIn(wb_name, [workbook['Name'] for workbook in wbs])

        self.highlander_admin('workbook-delete', params=wb_name)

        wbs = self.highlander_admin('workbook-list')
        self.assertNotIn(wb_name, [workbook['Name'] for workbook in wbs])

    def test_workbook_create_with_tags(self):
        wb = self.workbook_create(self.wb_with_tags_def)

        tags = self.get_value_of_field(wb, 'Tags')
        self.assertIn('tag', tags)

    def test_workbook_update(self):
        wb = self.workbook_create(self.wb_def)
        wb_name = self.get_value_of_field(wb, "Name")

        init_update_at = self.get_value_of_field(wb, "Updated at")
        tags = self.get_value_of_field(wb, 'Tags')
        self.assertNotIn('tag', tags)

        wb = self.highlander_admin(
            'workbook-update', params=self.wb_def)
        update_at = self.get_value_of_field(wb, "Updated at")
        name = self.get_value_of_field(wb, 'Name')
        tags = self.get_value_of_field(wb, 'Tags')

        self.assertEqual(wb_name, name)
        self.assertNotIn('tag', tags)
        self.assertEqual(init_update_at, update_at)

        wb = self.highlander_admin(
            'workbook-update', params=self.wb_with_tags_def)
        self.assertTableStruct(wb, ['Field', 'Value'])

        update_at = self.get_value_of_field(wb, "Updated at")
        name = self.get_value_of_field(wb, 'Name')
        tags = self.get_value_of_field(wb, 'Tags')

        self.assertEqual(wb_name, name)
        self.assertIn('tag', tags)
        self.assertNotEqual(init_update_at, update_at)

    def test_workbook_get(self):
        created = self.workbook_create(self.wb_with_tags_def)
        wb_name = self.get_value_of_field(created, "Name")

        fetched = self.highlander_admin('workbook-get', params=wb_name)

        created_wb_name = self.get_value_of_field(created, 'Name')
        fetched_wb_name = self.get_value_of_field(fetched, 'Name')

        self.assertEqual(created_wb_name, fetched_wb_name)

        created_wb_tag = self.get_value_of_field(created, 'Tags')
        fetched_wb_tag = self.get_value_of_field(fetched, 'Tags')

        self.assertEqual(created_wb_tag, fetched_wb_tag)

    def test_workbook_get_definition(self):
        wb = self.workbook_create(self.wb_def)
        wb_name = self.get_value_of_field(wb, "Name")

        definition = self.highlander_admin(
            'workbook-get-definition', params=wb_name)
        self.assertNotIn('404 Not Found', definition)


class WorkflowCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with workflows."""

    @classmethod
    def setUpClass(cls):
        super(WorkflowCLITests, cls).setUpClass()

    def test_workflow_create_delete(self):
        init_wfs = self.highlander_admin(
            'workflow-create', params=self.wf_def)
        wf_name = [wf['Name'] for wf in init_wfs]
        self.assertTableStruct(init_wfs, ['Name', 'Created at', 'Updated at'])

        wfs = self.highlander_admin('workflow-list')
        self.assertIn(wf_name[0], [workflow['Name'] for workflow in wfs])

        for wf in wfs:
            self.highlander_admin('workflow-delete', params=wf['Name'])

        wfs = self.highlander_admin('workflow-list')
        for wf in wf_name:
            self.assertNotIn(wf, [workflow['Name'] for workflow in wfs])

    def test_create_wf_with_tags(self):
        init_wfs = self.workflow_create(self.wf_def)
        wf_name = init_wfs[1]['Name']
        self.assertTableStruct(init_wfs, ['Name', 'Created at',
                                          'Updated at', 'Tags'])

        created_wf_info = self.get_item_info(
            get_from=init_wfs, get_by='Name', value=wf_name)

        self.assertEqual('tag', created_wf_info['Tags'])

    def test_workflow_update(self):
        wf = self.workflow_create(self.wf_def)
        wf_name = wf[0]['Name']

        created_wf_info = self.get_item_info(
            get_from=wf, get_by='Name', value=wf_name)

        upd_wf = self.highlander_admin(
            'workflow-update', params='{0}'.format(self.wf_def))
        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf, get_by='Name', value=wf_name)

        self.assertEqual(wf_name, upd_wf[0]['Name'])

        self.assertEqual(created_wf_info['Created at'].split(".")[0],
                         updated_wf_info['Created at'])
        self.assertEqual(created_wf_info['Updated at'],
                         updated_wf_info['Updated at'])

        upd_wf = self.highlander_admin(
            'workflow-update', params='{0}'.format(self.wf_with_delay_def))
        self.assertTableStruct(upd_wf, ['Name', 'Created at', 'Updated at'])

        updated_wf_info = self.get_item_info(
            get_from=upd_wf, get_by='Name', value=wf_name)

        self.assertEqual(wf_name, upd_wf[0]['Name'])

        self.assertEqual(created_wf_info['Created at'].split(".")[0],
                         updated_wf_info['Created at'])
        self.assertNotEqual(created_wf_info['Updated at'],
                            updated_wf_info['Updated at'])

    def test_workflow_get(self):
        created = self.workflow_create(self.wf_def)
        wf_name = created[0]['Name']

        fetched = self.highlander_admin('workflow-get', params=wf_name)
        fetched_wf_name = self.get_value_of_field(fetched, 'Name')
        self.assertEqual(wf_name, fetched_wf_name)

    def test_workflow_get_definition(self):
        wf = self.workflow_create(self.wf_def)
        wf_name = wf[0]['Name']

        definition = self.highlander_admin(
            'workflow-get-definition', params=wf_name)
        self.assertNotIn('404 Not Found', definition)


class ExecutionCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with executions."""

    @classmethod
    def setUpClass(cls):
        super(ExecutionCLITests, cls).setUpClass()

    def setUp(self):
        super(ExecutionCLITests, self).setUp()

        wfs = self.workflow_create(self.wf_def)
        self.direct_wf = wfs[0]
        self.reverse_wf = wfs[1]

        self.create_file('input', '{\n    "farewell": "Bye"\n}\n')
        self.create_file('task_name', '{\n    "task_name": "goodbye"\n}\n')

    def test_execution_create_delete(self):
        execution = self.highlander_admin(
            'execution-create', params=self.direct_wf['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')
        self.assertTableStruct(execution, ['Field', 'Value'])

        wf = self.get_value_of_field(execution, 'Workflow')
        created_at = self.get_value_of_field(execution, 'Created at')

        self.assertEqual(self.direct_wf['Name'], wf)
        self.assertIsNotNone(created_at)

        execs = self.highlander_admin('execution-list')
        self.assertIn(exec_id, [ex['ID'] for ex in execs])
        self.assertIn(wf, [ex['Workflow'] for ex in execs])

        self.highlander_admin('execution-delete', params=exec_id)

    def test_execution_create_with_input_and_start_task(self):
        execution = self.execution_create(
            "%s input task_name" % self.reverse_wf['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')

        result = self.wait_execution_success(exec_id)
        self.assertTrue(result)

    def test_execution_update(self):
        execution = self.execution_create(self.direct_wf['Name'])

        exec_id = self.get_value_of_field(execution, 'ID')
        status = self.get_value_of_field(execution, 'State')

        self.assertEqual('RUNNING', status)

        execution = self.highlander_admin(
            'execution-update', params='{0} "PAUSED"'.format(exec_id))

        updated_exec_id = self.get_value_of_field(execution, 'ID')
        status = self.get_value_of_field(execution, 'State')

        self.assertEqual(exec_id, updated_exec_id)
        self.assertEqual('PAUSED', status)

    def test_execution_get(self):
        execution = self.execution_create(self.direct_wf['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')

        execution = self.highlander_admin(
            'execution-get', params='{0}'.format(exec_id))

        gotten_id = self.get_value_of_field(execution, 'ID')
        wf = self.get_value_of_field(execution, 'Workflow')

        self.assertEqual(exec_id, gotten_id)
        self.assertEqual(self.direct_wf['Name'], wf)

    def test_execution_get_input(self):
        execution = self.execution_create(self.direct_wf['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')

        ex_input = self.highlander_admin('execution-get-input', params=exec_id)
        self.assertEqual([], ex_input)

    def test_execution_get_output(self):
        execution = self.execution_create(self.direct_wf['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')

        ex_output = self.highlander_admin(
            'execution-get-output', params=exec_id)

        self.assertEqual([], ex_output)


class CronTriggerCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with cron-triggers."""

    @classmethod
    def setUpClass(cls):
        super(CronTriggerCLITests, cls).setUpClass()

    def setUp(self):
        super(CronTriggerCLITests, self).setUp()

        wf = self.workflow_create(self.wf_def)
        self.wf_name = wf[0]['Name']

    def test_cron_trigger_create_delete(self):
        trigger = self.highlander_admin(
            'cron-trigger-create',
            params=('trigger %s {} --pattern "5 * * * *" --count 5'
                    ' --first-time "4242-12-25 13:37"' % self.wf_name))
        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(trigger, 'Name')
        wf_name = self.get_value_of_field(trigger, 'Workflow')
        created_at = self.get_value_of_field(trigger, 'Created at')
        remain = self.get_value_of_field(trigger, 'Remaining executions')
        next_time = self.get_value_of_field(trigger, 'Next execution time')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_name, wf_name)
        self.assertIsNotNone(created_at)
        self.assertEqual("4242-12-25 13:37:00", next_time)
        self.assertEqual("5", remain)

        trgs = self.highlander_admin('cron-trigger-list')
        self.assertIn(tr_name, [tr['Name'] for tr in trgs])
        self.assertIn(wf_name, [tr['Workflow'] for tr in trgs])

        self.highlander('cron-trigger-delete', params=tr_name)

        trgs = self.highlander_admin('cron-trigger-list')
        self.assertNotIn(tr_name, [tr['Name'] for tr in trgs])

    def test_two_cron_triggers_for_one_wf(self):
        self.cron_trigger_create(
            'trigger1', self.wf_name, '{}', "5 * * * *")
        self.cron_trigger_create(
            'trigger2', self.wf_name, '{}', "15 * * * *")

        trgs = self.highlander_admin('cron-trigger-list')
        self.assertIn("trigger1", [tr['Name'] for tr in trgs])
        self.assertIn("trigger2", [tr['Name'] for tr in trgs])

    def test_cron_trigger_get(self):
        trigger = self.cron_trigger_create(
            'trigger', self.wf_name, '{}', "5 * * * *")
        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(trigger, 'Name')

        fetched_tr = self.highlander_admin(
            'cron-trigger-get', params='trigger')

        self.assertTableStruct(trigger, ['Field', 'Value'])

        tr_name = self.get_value_of_field(fetched_tr, 'Name')
        wf_name = self.get_value_of_field(fetched_tr, 'Workflow')
        created_at = self.get_value_of_field(fetched_tr, 'Created at')

        self.assertEqual('trigger', tr_name)
        self.assertEqual(self.wf_name, wf_name)
        self.assertIsNotNone(created_at)


class TaskCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with tasks."""

    def setUp(self):
        super(TaskCLITests, self).setUp()

        wfs = self.workflow_create(self.wf_def)
        self.direct_wf = wfs[0]
        self.reverse_wf = wfs[1]

        self.create_file('input', '{\n    "farewell": "Bye"\n}\n')
        self.create_file('task_name', '{\n    "task_name": "goodbye"\n}\n')

    def test_task_get(self):
        execution = self.execution_create(self.direct_wf['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')

        tasks = self.highlander_admin('task-list')
        created_task_id = tasks[-1]['ID']

        fetched_task = self.highlander_admin('task-get', params=created_task_id)
        fetched_task_id = self.get_value_of_field(fetched_task, 'ID')
        task_execution_id = self.get_value_of_field(fetched_task,
                                                    'Execution ID')

        self.assertEqual(created_task_id, fetched_task_id)
        self.assertEqual(exec_id, task_execution_id)


class ActionCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with actions."""

    @classmethod
    def setUpClass(cls):
        super(ActionCLITests, cls).setUpClass()

    def test_action_create_delete(self):
        init_acts = self.highlander_admin(
            'action-create', params=self.act_def)
        self.assertTableStruct(init_acts, ['Name', 'Is system', 'Input',
                                           'Description', 'Tags',
                                           'Created at', 'Updated at'])

        self.assertIn('greeting', [action['Name'] for action in init_acts])
        self.assertIn('farewell', [action['Name'] for action in init_acts])

        action_1 = self.get_item_info(
            get_from=init_acts, get_by='Name', value='greeting')
        action_2 = self.get_item_info(
            get_from=init_acts, get_by='Name', value='farewell')

        self.assertEqual(action_1['Tags'], '<none>')
        self.assertEqual(action_2['Tags'], '<none>')

        self.assertEqual(action_1['Is system'], 'False')
        self.assertEqual(action_2['Is system'], 'False')

        self.assertEqual(action_1['Input'], 'name')
        self.assertEqual(action_2['Input'], 'None')

        acts = self.highlander_admin('action-list')
        self.assertIn(action_1['Name'], [action['Name'] for action in acts])
        self.assertIn(action_2['Name'], [action['Name'] for action in acts])

        self.highlander_admin(
            'action-delete', params='{0}'.format(action_1['Name']))
        self.highlander_admin(
            'action-delete', params='{0}'.format(action_2['Name']))

        acts = self.highlander_admin('action-list')
        self.assertNotIn(action_1['Name'], [action['Name'] for action in acts])
        self.assertNotIn(action_2['Name'], [action['Name'] for action in acts])

    def test_action_update(self):
        acts = self.action_create(self.act_def)

        created_action = self.get_item_info(
            get_from=acts, get_by='Name', value='greeting')

        acts = self.highlander_admin('action-update', params=self.act_def)

        updated_action = self.get_item_info(
            get_from=acts, get_by='Name', value='greeting')

        self.assertEqual(created_action['Created at'].split(".")[0],
                         updated_action['Created at'])
        self.assertEqual(created_action['Name'], updated_action['Name'])
        self.assertEqual(created_action['Updated at'],
                         updated_action['Updated at'])

        acts = self.highlander_admin('action-update', params=self.act_tag_def)

        updated_action = self.get_item_info(
            get_from=acts, get_by='Name', value='greeting')

        self.assertEqual(updated_action['Tags'], 'tag, tag1')
        self.assertEqual(created_action['Created at'].split(".")[0],
                         updated_action['Created at'])
        self.assertEqual(created_action['Name'], updated_action['Name'])
        self.assertNotEqual(created_action['Updated at'],
                            updated_action['Updated at'])

    def test_action_get_definition(self):
        self.action_create(self.act_def)

        definition = self.highlander_admin(
            'action-get-definition', params='greeting')
        self.assertNotIn('404 Not Found', definition)


class EnvironmentCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with environments."""

    def setUp(self):
        super(EnvironmentCLITests, self).setUp()

        self.create_file('env.yaml',
                         'name: env\n'
                         'description: Test env\n'
                         'variables:\n'
                         '  var: "value"')

    def test_environment_create(self):
        env = self.highlander_admin('environment-create', params='env.yaml')
        env_name = self.get_value_of_field(env, 'Name')
        env_desc = self.get_value_of_field(env, 'Description')

        self.assertTableStruct(env, ['Field', 'Value'])

        envs = self.highlander_admin('environment-list')
        self.assertIn(env_name, [en['Name'] for en in envs])
        self.assertIn(env_desc, [en['Description'] for en in envs])

        self.highlander_admin('environment-delete', params=env_name)

        envs = self.highlander_admin('environment-list')
        self.assertNotIn(env_name, [en['Name'] for en in envs])

    def test_environment_update(self):
        env = self.environment_create('env.yaml')
        env_name = self.get_value_of_field(env, 'Name')
        env_desc = self.get_value_of_field(env, 'Description')
        env_created_at = self.get_value_of_field(env, 'Created at')
        env_updated_at = self.get_value_of_field(env, 'Updated at')

        self.assertIsNotNone(env_created_at)
        self.assertEqual(env_updated_at, 'None')

        self.create_file('env_upd.yaml',
                         'name: env\n'
                         'description: Updated env\n'
                         'variables:\n'
                         '  var: "value"')

        env = self.highlander_admin('environment-update', params='env_upd.yaml')
        self.assertTableStruct(env, ['Field', 'Value'])

        updated_env_name = self.get_value_of_field(env, 'Name')
        updated_env_desc = self.get_value_of_field(env, 'Description')
        updated_env_created_at = self.get_value_of_field(env, 'Created at')
        updated_env_updated_at = self.get_value_of_field(env, 'Updated at')

        self.assertEqual(env_name, updated_env_name)
        self.assertNotEqual(env_desc, updated_env_desc)
        self.assertEqual(updated_env_desc, 'Updated env')
        self.assertEqual(env_created_at.split('.')[0], updated_env_created_at)
        self.assertIsNotNone(updated_env_updated_at)

    @decorators.skip_because(bug="1418545")
    def test_environment_update_work_as_create(self):
        env = self.highlander_admin('environment-update', params='env.yaml')
        env_name = self.get_value_of_field(env, 'Name')
        env_desc = self.get_value_of_field(env, 'Description')

        self.assertTableStruct(env, ['Field', 'Value'])

        envs = self.highlander_admin('environment-list')
        self.assertIn(env_name, [en['Name'] for en in envs])
        self.assertIn(env_desc, [en['Description'] for en in envs])

        self.highlander_admin('environment-delete', params=env_name)

        envs = self.highlander_admin('environment-list')
        self.assertNotIn(env_name, [en['Name'] for en in envs])

    def test_environment_get(self):
        env = self.environment_create('env.yaml')
        env_name = self.get_value_of_field(env, 'Name')
        env_desc = self.get_value_of_field(env, 'Description')

        env = self.highlander_admin('environment-get', params=env_name)
        fetched_env_name = self.get_value_of_field(env, 'Name')
        fetched_env_desc = self.get_value_of_field(env, 'Description')

        self.assertTableStruct(env, ['Field', 'Value'])
        self.assertEqual(env_name, fetched_env_name)
        self.assertEqual(env_desc, fetched_env_desc)


class ActionExecutionCLITests(base_v1.HighlanderClientTestBase):
    """Test suite checks commands to work with action executions."""

    def setUp(self):
        super(ActionExecutionCLITests, self).setUp()

        wfs = self.workflow_create(self.wf_def)
        self.direct_wf = wfs[0]

        direct_wf_exec = self.execution_create(self.direct_wf['Name'])
        self.direct_ex_id = self.get_value_of_field(direct_wf_exec, 'ID')

    def test_act_execution_get(self):
        self.wait_execution_success(self.direct_ex_id)

        task = self.highlander_admin(
            'task-list', params=self.direct_ex_id)[0]

        act_ex_from_list = self.highlander_admin(
            'action-execution-list', params=task['ID'])[0]

        act_ex = self.highlander_admin(
            'action-execution-get', params=act_ex_from_list['ID'])

        wf_name = self.get_value_of_field(act_ex, 'Workflow name')
        status = self.get_value_of_field(act_ex, 'State')

        self.assertEqual(
            act_ex_from_list['ID'],
            self.get_value_of_field(act_ex, 'ID')
        )
        self.assertEqual(wf_name, self.direct_wf['Name'])
        self.assertEqual(status, 'SUCCESS')


class NegativeCLITests(base_v1.HighlanderClientTestBase):
    """This class contains negative tests."""

    def test_wb_list_extra_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-list',
                          params='param')

    def test_wb_get_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-get',
                          params='wb')

    def test_wb_get_without_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-get')

    def test_wb_create_same_name(self):
        self.workbook_create(self.wb_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.workbook_create,
                          self.wb_def)

    def test_wb_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook_create',
                          'wb')

    def test_wb_delete_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-delete',
                          params='wb')

    def test_wb_update_wrong_path_to_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-update',
                          params='wb')

    def test_wb_update_nonexistant_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-update',
                          params=self.wb_with_tags_def)

    def test_wb_create_empty_def(self):
        self.create_file('empty')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-create',
                          params='empty')

    def test_wb_update_empty_def(self):
        self.create_file('empty')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-update',
                          params='empty')

    def test_wb_get_definition_unexist_wb(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-get-definition',
                          params='wb')

    def test_wb_create_invalid_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-create',
                          params=self.wf_def)

    def test_wb_update_invalid_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-update',
                          params=self.wf_def)

    def test_wb_update_without_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workbook-update')

    def test_wf_list_extra_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-list',
                          params='param')

    def test_wf_get_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-get',
                          params='wf')

    def test_wf_get_without_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-get')

    def test_wf_create_without_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-create',
                          params='')

    def test_wf_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-create',
                          params='wf')

    def test_wf_delete_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-delete',
                          params='wf')

    def test_wf_update_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-update',
                          params='wf')

    def test_wf_get_definition_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-get-definition',
                          params='wf')

    def test_wf_get_definition_missed_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-get-definition')

    def test_wf_create_invalid_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-create',
                          params=self.wb_def)

    def test_wf_update_invalid_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-update',
                          params=self.wb_def)

    def test_wf_create_empty_def(self):
        self.create_file('empty')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-create',
                          params='empty')

    def test_wf_update_empty_def(self):
        self.create_file('empty')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'workflow-update',
                          params='empty')

    def test_ex_list_extra_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-list',
                          params='param')

    def test_ex_create_unexist_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-create',
                          params='wf')

    def test_ex_create_unexist_task(self):
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-create',
                          params='%s param {}' % wf[0]['Name'])

    def test_ex_create_with_invalid_input(self):
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-create',
                          params="%s input" % wf[0]['Name'])

    def test_ex_get_nonexist_execution(self):
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-get',
                          params='%s id' % wf[0]['Name'])

    def test_ex_create_without_wf_name(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-create')

    def test_ex_create_reverse_wf_without_start_task(self):
        wf = self.workflow_create(self.wf_def)
        self.create_file('input', '{\n    "farewell": "Bye"\n}\n')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-create ',
                          params=wf[1]['Name'])

    def test_ex_create_missed_input(self):
        self.create_file('empty')
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-create empty',
                          params=wf[1]['Name'])

    def test_ex_invalid_status_changing(self):
        wf = self.workflow_create(self.wf_def)
        execution = self.execution_create(params=wf[0]['Name'])
        exec_id = self.get_value_of_field(execution, 'ID')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-update',
                          params='%s ERROR' % exec_id)

    def test_ex_delete_nonexistent_execution(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution-delete', params='1a2b3c')

    def test_tr_create_without_pattern(self):
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr %s {}' % wf[0]['Name'])

    def test_tr_create_invalid_pattern(self):
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr %s {} --pattern "q"' % wf[0]['Name'])

    def test_tr_create_invalid_pattern_value_out_of_range(self):
        wf = self.workflow_create(self.wf_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr %s {}'
                                 ' --pattern "80 * * * *"' % wf[0]['Name'])

    def test_tr_create_nonexistent_wf(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr wb.wf1 {} --pattern "* * * * *"')

    def test_tr_delete_nonexistant_tr(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-delete',
                          params='tr')

    def test_tr_get_nonexistant_tr(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-get',
                          params='tr')

    def test_tr_create_invalid_count(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr wb.wf1 {}'
                                 ' --pattern "* * * * *" --count q')

    def test_tr_create_negative_count(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr wb.wf1 {}'
                                 ' --pattern "* * * * *" --count -1')

    def test_tr_create_invalid_first_date(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr wb.wf1 {}'
                                 ' --pattern "* * * * *"'
                                 ' --first-date "q"')

    def test_tr_create_count_only(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr wb.wf1 {} --count 42')

    def test_tr_create_date_and_count_without_pattern(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'cron-trigger-create',
                          params='tr wb.wf1 {} --count 42'
                                 ' --first-time "4242-12-25 13:37"')

    def test_action_get_nonexistent(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander,
                          'action-get',
                          params='nonexist')

    def test_action_double_creation(self):
        self.action_create(self.act_def)
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-create',
                          params='{0}'.format(self.act_def))

    def test_action_create_without_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-create',
                          params='')

    def test_action_create_invalid_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-create',
                          params='{0}'.format(self.wb_def))

    def test_action_delete_nonexistent_act(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-delete',
                          params='nonexist')

    def test_action_delete_standard_action(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-delete',
                          params='heat.events_get')

    def test_action_get_definition_nonexistent_action(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-get-definition',
                          params='nonexist')

    def test_task_get_nonexistent_task(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'task-get',
                          params='nonexist')

    def test_env_get_without_param(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'environment-get')

    def test_env_create_same_name(self):
        self.create_file('env.yaml',
                         'name: env\n'
                         'description: Test env\n'
                         'variables:\n'
                         '  var: "value"')

        self.environment_create('env.yaml')
        self.assertRaises(exceptions.CommandFailed,
                          self.environment_create,
                          'env.yaml')

    def test_env_create_with_wrong_path_to_definition(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'execution_create',
                          'env')

    def test_env_delete_unexist_env(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'environment-delete',
                          params='env')

    def test_env_update_wrong_path_to_def(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'environment-update',
                          params='env')

    def test_env_create_without_name(self):
        self.create_file('env.yaml',
                         'variables:\n  var: "value"')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'environment-create',
                          params='env.yaml')

    def test_env_create_without_variables(self):
        self.create_file('env.yaml',
                         'name: env')
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'environment-create',
                          params='env.yaml')

    def test_action_execution_get_without_params(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-execution-get')

    def test_action_execution_get_unexistent_obj(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-execution-get',
                          params='123456')

    def test_action_execution_update(self):
        wfs = self.workflow_create(self.wf_def)
        direct_wf_exec = self.execution_create(wfs[0]['Name'])
        direct_ex_id = self.get_value_of_field(direct_wf_exec, 'ID')

        self.assertRaises(exceptions.CommandFailed,
                          self.highlander_admin,
                          'action-execution-update',
                          params='%s ERROR' % direct_ex_id)
