from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.vm_custom_attributes import VmCustomAttributes
from st2common.runners.base_action import Action

import mock
import urllib


class TestActionVmCustomAttributes(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = VmCustomAttributes

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, VmCustomAttributes)
        self.assertIsInstance(action, Action)

    def test__get_query(self):
        action = self.get_action_instance({})
        result = action._get_query()
        self.assertEquals(result, {'expand': 'resources'})

    def test__validate(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key0', 'value': 'test_value0'}
        result = action._validate(custom_attributes)
        self.assertEquals(result, True)

    def test__validate_missing_value_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key1'}
        with self.assertRaises(RuntimeError):
            action._validate(custom_attributes)

    def test__validate_missing_key_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'value': 'test_value1'}
        with self.assertRaises(RuntimeError):
            action._validate(custom_attributes)

    def test__validate_missing_value_ok(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key1'}
        result = action._validate(custom_attributes, value_required=False)
        self.assertEquals(result, True)

    def test__post_action_add(self):
        action = self.get_action_instance({})

        id = "100"
        action_name = 'add'
        custom_attributes = [{'key': 'key0', 'value': 'value0'},
                             {'key': 'key1', 'value': 'value1'},
                             {'key': 'key2', 'value': 'value2'}]
        kwargs_dict = {'id': id,
                       'custom_attributes': custom_attributes}

        # expected
        expected_result = "result"
        expected_resources = []
        for attr in custom_attributes:
            expected_resources.append({'name': attr['key'],
                                       'value': attr['value']})

        # mock
        mock_vm = mock.MagicMock()
        mock_vm.custom_attributes.action.add.return_value = expected_result

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action._post_action(mock_client, kwargs_dict, action_name)

        # assert
        self.assertEquals(result, expected_result)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.custom_attributes.action.add.assert_called_with(*expected_resources)

    def test__post_action_delete(self):
        action = self.get_action_instance({})

        id = "100"
        action_name = 'delete'
        custom_attributes = [{'key': 'key0', 'value': 'value0'}]
        kwargs_dict = {'id': id,
                       'custom_attributes': custom_attributes}

        # expected
        expected_result = "result"
        expected_resources = []
        for attr in custom_attributes:
            expected_resources.append({'name': attr['key']})

        # mock
        mock_vm = mock.MagicMock()
        mock_vm.custom_attributes.action.delete.return_value = expected_result

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action._post_action(mock_client, kwargs_dict, action_name)

        # assert
        self.assertEquals(result, expected_result)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.custom_attributes.action.delete.assert_called_with(*expected_resources)

    def test__post_action_raises(self):
        action = self.get_action_instance({})
        id = "100"
        action_name = 'delete'
        kwargs_dict = {'id': id,
                       'custom_attributes': [{'value': 'value0'}]}
        mock_client = mock.MagicMock()
        with self.assertRaises(RuntimeError):
            action._post_action(mock_client, kwargs_dict, action_name)

    def test_list(self):
        action = self.get_action_instance({})
        id = "100"
        kwargs_dict = {'id': id}
        resources_data = [{'name': 'data0'},
                          {'name': 'data1'},
                          {'name': 'data2'}]
        query_dict = action._get_query()

        # mock
        resources = [mock.MagicMock(_data=r) for r in resources_data]
        mock_search_results = mock.MagicMock(resources=resources)

        mock_vm = mock.MagicMock()
        mock_vm.custom_attributes.query_string.return_value = mock_search_results

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action.list(mock_client, kwargs_dict)

        # assert
        self.assertEquals(result, resources_data)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.custom_attributes.query_string.assert_called_with(**query_dict)

    def test_get(self):
        action = self.get_action_instance({})
        id = "100"
        key = "test attribute"
        kwargs_dict = {'id': id,
                       'key': key}
        query_dict = action._get_query()
        query_dict['filter[]'] = 'name={}'.format(urllib.quote_plus(key))

        resources_data = [{'name': key}]

        # mock
        resources = [mock.MagicMock(_data=r) for r in resources_data]
        mock_search_results = mock.MagicMock(resources=resources)

        mock_vm = mock.MagicMock()
        mock_vm.custom_attributes.query_string.return_value = mock_search_results

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action.list(mock_client, kwargs_dict)

        # assert
        self.assertEquals(result, resources_data)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.custom_attributes.query_string.assert_called_with(**action._get_query())

    @mock.patch('lib.vm_custom_attributes.VmCustomAttributes._post_action')
    def test_set(self, mock__post_action):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {'key': 'value'}
        expected_result = "result"
        mock__post_action.return_value = expected_result

        result = action.set(client, kwargs_dict)

        self.assertEquals(result, expected_result)
        mock__post_action.assert_called_with(client, kwargs_dict, 'add')

    @mock.patch('lib.vm_custom_attributes.VmCustomAttributes._post_action')
    def test_delete(self, mock__post_action):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {'key': 'value'}
        expected_result = "result"
        mock__post_action.return_value = expected_result

        result = action.delete(client, kwargs_dict)

        self.assertEquals(result, expected_result)
        mock__post_action.assert_called_with(client, kwargs_dict, 'delete')
