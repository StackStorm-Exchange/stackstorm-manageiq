from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.task_check_complete import TaskCheckComplete
from st2common.runners.base_action import Action

import mock


class TestActionTaskCheck(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = TaskCheckComplete

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, TaskCheckComplete)
        self.assertIsInstance(action, Action)

    def test_task_check_complete(self):
        action = self.get_action_instance({})
        task_id = '100008'
        kwargs_dict = {'task_id': task_id}

        # mocks
        mock_task = mock.MagicMock(state='Finished')
        mock_client = mock.MagicMock()
        mock_client.collections.tasks.return_value = mock_task

        # execute
        result = action.task_check_complete(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, True)
        mock_client.collections.tasks.assert_called_with(task_id)

    def test_task_check_complete_not_finished(self):
        action = self.get_action_instance({})
        task_id = '100008'
        kwargs_dict = {'task_id': task_id}

        # mocks
        mock_task = mock.MagicMock(state='running')
        mock_client = mock.MagicMock()
        mock_client.collections.tasks.return_value = mock_task

        # execute
        with self.assertRaises(RuntimeError):
            action.task_check_complete(mock_client, kwargs_dict)
