from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.base_action import BaseAction
from st2common.runners.base_action import Action

import copy
import mock


class TestActionBaseAction(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = BaseAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    def test__get_arg_present(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key1"
        expected_dict = test_dict
        expected_value = test_dict["key1"]
        result_value = action._get_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test__get_arg_missing(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key3"
        expected_dict = test_dict
        expected_value = None
        result_value = action._get_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test__attributes_str(self):
        action = self.get_action_instance({})
        test_array = ["test_1", "test_2"]
        expected_value = "test_1,test_2"
        result_output = action._attributes_str(test_array)
        self.assertEqual(expected_value, result_output)

    def test__resourcs_from_search_results(self):
        action = self.get_action_instance({})
        resources_data = [{'name': 'data0'},
                          {'name': 'data1'},
                          {'name': 'data2'}]
        resources = []
        for resource in resources_data:
            r = mock.MagicMock(_data=resource)
            resources.append(r)

        mock_search_results = mock.MagicMock(resources=resources)
        results = action._resources_from_search_results(mock_search_results)
        self.assertEqual(results, resources_data)

    def test__get_objects(self):
        action = self.get_action_instance({})
        collection_name = "vms"
        resources_data = [{'key': 'aaa', 'value': 'value0'},
                          {'key': 'xxx', 'value': 'value2'}]
        query_dict = {'param': 'value'}
        expected_query = dict(query_dict)

        # mock
        resources = [mock.MagicMock(_data=r) for r in resources_data]
        mock_search_results = mock.MagicMock(resources=resources)
        mock_client = mock.MagicMock()
        mock_client.collections.vms.query_string.return_value = mock_search_results

        # execute
        result = action._get_objects(mock_client, collection_name, query_dict)

        # assert
        self.assertEquals(result, resources_data)
        mock_client.collections.vms.query_string.assert_called_with(**expected_query)

    @mock.patch('lib.base_action.BaseAction._get_objects')
    def test__get_object(self, mock__get_objects):
        action = self.get_action_instance({})
        name = "key 0"
        collection_name = "vms"
        resources = [{'key': name, 'value': 'value0'},
                     {'key': 'xxx', 'value': 'value2'}]
        query_dict = {'param': 'value'}
        expected_query = dict(query_dict)
        expected_query['filter[]'] = ['name = "{}"'.format(name)]

        # mock
        mock__get_objects.return_value = copy.deepcopy(resources)
        mock_client = mock.MagicMock()

        # execute
        result = action._get_object(mock_client, collection_name, name, query_dict)

        # assert
        self.assertEquals(result, resources[0])
        mock__get_objects.assert_called_with(mock_client, collection_name, expected_query)

    @mock.patch('lib.base_action.BaseAction._get_objects')
    def test__get_object_empty(self, mock__get_objects):
        action = self.get_action_instance({})
        name = "key 0"
        collection_name = "vms"
        resources = []
        query_dict = {'param': 'value'}
        expected_query = dict(query_dict)
        expected_query['filter[]'] = ['name = "{}"'.format(name)]

        # mock
        mock__get_objects.return_value = copy.deepcopy(resources)
        mock_client = mock.MagicMock()

        # execute
        result = action._get_object(mock_client, collection_name, name, query_dict)

        # assert
        self.assertEquals(result, None)
        mock__get_objects.assert_called_with(mock_client, collection_name, expected_query)

    def test__create_object(self):
        action = self.get_action_instance({})
        collection_name = "vms"
        query_dict = {'expand': 'resources'}
        payload = {'test': 'payload'}
        id = 12
        response_data = {'test': 'data',
                         'id': id}
        response_data_2 = {'test2': 'data2',
                           'id': id}

        mock_create = [mock.MagicMock(_data=response_data)]

        mock_object = mock.MagicMock(_data=response_data_2)
        mock_object.reload.return_value = "junk"

        mock_vms = mock.MagicMock()
        mock_vms.action.create.return_value = mock_create
        mock_vms.return_value = mock_object

        mock_client = mock.MagicMock()
        mock_client.collections.vms = mock_vms

        response = action._create_object(mock_client, collection_name, query_dict, payload)

        self.assertEquals(response, response_data_2)

    def test__create_object_empty_response(self):
        action = self.get_action_instance({})
        collection_name = "vms"
        query_dict = {'expand': 'resources'}
        payload = {'test': 'payload'}

        mock_client = mock.MagicMock()
        mock_client.collections.vms.action.create.return_value = []

        with self.assertRaises(RuntimeError):
            action._create_object(mock_client, collection_name, query_dict, payload)

    def test__create_object_no_id(self):
        action = self.get_action_instance({})
        collection_name = "vms"
        query_dict = {'expand': 'resources'}
        payload = {'test': 'payload'}

        mock_data = [mock.MagicMock(_data={"not_id": "value"})]
        mock_client = mock.MagicMock()
        mock_client.collections.vms.action.create.return_value = mock_data

        with self.assertRaises(KeyError):
            action._create_object(mock_client, collection_name, query_dict, payload)

    @mock.patch("lib.base_action.BaseAction._get_object")
    def test__get_or_create_object_get(self, mock_get):
        action = self.get_action_instance({})
        collection_name = "vms"
        name = "name"
        query_dict = {'expand': 'resources'}
        payload = {'test': 'payload'}
        expected = "result"
        client = None

        mock_get.return_value = expected

        result = action._get_or_create_object(client, collection_name, name, query_dict, payload)

        self.assertEquals(result, expected)

    @mock.patch("lib.base_action.BaseAction._create_object")
    @mock.patch("lib.base_action.BaseAction._get_object")
    def test__get_or_create_object_create(self, mock_get, mock_create):
        action = self.get_action_instance({})
        collection_name = "vms"
        name = "name"
        query_dict = {'expand': 'resources'}
        payload = {'test': 'payload'}
        expected = "result"
        client = None

        mock_get.return_value = None
        mock_create.return_value = expected

        result = action._get_or_create_object(client, collection_name, name, query_dict, payload)

        self.assertEquals(result, expected)

    @mock.patch("lib.base_action.BaseAction._foo", create=True)
    @mock.patch("lib.base_action.MiqApi")
    def test_run(self, mock_miq_api, mock__foo):
        action = self.get_action_instance({})

        # expected
        expected_kwargs_dict = {'server': 'testserver.domain.tld',
                                'username': 'admin',
                                'password': '$up3rSeCreT!',
                                'operation': '_foo'}
        expected_client = 'client'
        expected_result = 'result'

        # mocks
        mock_miq_api.return_value = expected_client
        mock__foo.return_value = expected_result

        # execute
        result = action.run(**expected_kwargs_dict)

        # asserts
        self.assertEquals(result, expected_result)
        mock_miq_api.assert_called_with('https://{}/api'.format(expected_kwargs_dict['server']),
                                        (expected_kwargs_dict['username'],
                                         expected_kwargs_dict['password']),
                                        verify_ssl=False)
        mock__foo.assert_called_with(expected_client, expected_kwargs_dict)
