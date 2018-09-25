from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.vm import Vm
from st2common.runners.base_action import Action

import mock


class TestActionVm(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = Vm

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, Vm)
        self.assertIsInstance(action, Action)

    def test_find_by_name(self):
        action = self.get_action_instance({})

        kwargs_dict = {'name': 'vmname.domain.tld', 'attributes': []}

        # mocks
        expected_resources = []
        expected_results = []
        for i in range(1, 10):
            mock_resource = mock.MagicMock()
            mock_resource._data = {'results': i}
            expected_resources.append(mock_resource)
            expected_results.append(mock_resource._data)

        mock_query_results = mock.MagicMock()
        mock_query_results.resources = expected_resources

        mock_client = mock.MagicMock()
        mock_client.collections.vms.query_string.return_value = mock_query_results

        # execute
        results = action.find_by_name(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(results, expected_results[0])

    def test_scan(self):
        action = self.get_action_instance({})
        id = '100008'
        kwargs_dict = {'id': id}
        expected_result = 'expected_result'

        # mocks
        mock_result = mock.MagicMock(_data=expected_result)
        mock_vm = mock.MagicMock()
        mock_vm.action.scan.return_value = mock_result
        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action.scan(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, expected_result)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.action.scan.assert_called_with()

    def test_retire(self):
        action = self.get_action_instance({})
        id = '100008'
        kwargs_dict = {'id': id}
        expected_result = 'expected_result'

        # mocks
        mock_result = mock.MagicMock(_data=expected_result)
        mock_vm = mock.MagicMock()
        mock_vm.action.retire.return_value = mock_result
        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action.retire(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, expected_result)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.action.retire.assert_called_with()

    def test_check_removed_true(self):
        action = self.get_action_instance({})
        id = '100008'
        kwargs_dict = {'id': id}

        # mocks
        mock_vm = mock.MagicMock(exists=False)
        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action.check_removed(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, True)
        mock_client.collections.vms.assert_called_with(id)

    def test_check_removed_false(self):
        action = self.get_action_instance({})
        id = '100008'
        kwargs_dict = {'id': id}

        # mocks
        mock_vm = mock.MagicMock(exists=True)
        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        with self.assertRaises(RuntimeError):
            action.check_removed(mock_client, kwargs_dict)

        # asserts
        mock_client.collections.vms.assert_called_with(id)
