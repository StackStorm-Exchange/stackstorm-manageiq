from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.provision_check_success import ProvCheckSuccess
from st2common.runners.base_action import Action

import mock


class TestActionProvCheck(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = ProvCheckSuccess

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, ProvCheckSuccess)
        self.assertIsInstance(action, Action)

    def test_get_vm_miq_id(self):
        action = self.get_action_instance({})
        test_tasks = [{'destination_id': '10000001'}]

        result = action.get_vm_miq_id(test_tasks)

        self.assertEquals(result, '10000001')

    def test_get_vm_miq_id_error(self):
        action = self.get_action_instance({})
        test_tasks = [{}]

        result = action.get_vm_miq_id(test_tasks)

        self.assertEquals(result, 'error')

    @mock.patch("lib.provision_check_success.base_action.BaseAction._data_from_entity_list")
    def test_provision_check_success(self, mock_task_list):
        action = self.get_action_instance({})
        request_id = '100008'
        vm_id = '10000001'
        test_tasks = [{'destination_id': vm_id}]
        kwargs_dict = {'request_id': request_id}

        # mocks
        mock_request = mock.MagicMock(tasks='Test Tasks', request_state='finished')
        mock_task_list.return_value = test_tasks
        mock_client = mock.MagicMock()
        mock_client.collections.provision_requests.return_value = mock_request

        # execute
        result = action.provision_check_success(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, vm_id)
        mock_client.collections.provision_requests.assert_called_with(request_id)
        mock_task_list.assert_called_with('Test Tasks')

    @mock.patch("lib.provision_check_success.base_action.BaseAction._data_from_entity_list")
    def test_provision_check_success_error(self, mock_task_list):
        action = self.get_action_instance({})
        request_id = '100008'
        test_tasks = []
        kwargs_dict = {'request_id': request_id}

        # mocks
        mock_request = mock.MagicMock(tasks='Test Tasks', request_state='running')
        mock_task_list.return_value = test_tasks
        mock_client = mock.MagicMock()
        mock_client.collections.provision_requests.return_value = mock_request

        # execute
        with self.assertRaises(ValueError):
            action.provision_check_success(mock_client, kwargs_dict)
