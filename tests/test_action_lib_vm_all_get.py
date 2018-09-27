from manage_iq_base_action_test_case import ManageIQBaseActionTestCase
from lib.vm_all_get import GetAllVMs

from st2common.runners.base_action import Action
from mock import MagicMock

import mock


class TestGetAllVMs(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = GetAllVMs

    def _mock_response(self, status=200, content="CONTENT", json_data=None, raise_for_status=None):
        """Since we will be makeing alot of rest calls that
        all raise for status, we are creating this helper
        method to build the mock reponse for us to reduce
        duplicated code.
        """
        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        mock_resp.content = content
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, GetAllVMs)
        self.assertIsInstance(action, Action)

    def test_get_arg_present(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key1"
        expected_value = test_dict["key1"]
        result_value = action.get_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)

    def test_get_arg_missing(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key3"
        expected_value = None
        result_value = action.get_arg(test_key, test_dict)
        self.assertEqual(result_value, expected_value)

    def test_get_arg_delete_present(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key1"
        expected_dict = {"key2": "value2"}
        expected_value = test_dict["key1"]
        result_value = action.get_arg(test_key, test_dict, True)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    def test_get_arg_delete_missing(self):
        action = self.get_action_instance({})
        test_dict = {"key1": "value1",
                     "key2": "value2"}
        test_key = "key3"
        expected_dict = test_dict
        expected_value = None
        result_value = action.get_arg(test_key, test_dict, True)
        self.assertEqual(result_value, expected_value)
        self.assertEqual(test_dict, expected_dict)

    @mock.patch("lib.vm_all_get.requests")
    def test_build_session(self, mock_requests):
        action = self.get_action_instance({})

        kwargs_dict = {'server': 'test.dev.encore.tech',
                       'username': 'user',
                       'password': 'pass'}

        mock_session = mock_requests.Session()

        result_value = action.build_session(kwargs_dict)

        self.assertEqual(result_value, mock_session)

    @mock.patch("lib.vm_all_get.GetAllVMs.build_session")
    def test_run(self, mock_session):
        action = self.get_action_instance({})
        test_dict = {'server': 'test.dev.encore.tech',
                   'username': 'user',
                   'password': 'pass'}
        expected_result = {
            'vm_fqdn': "test-name",
            'vm_uuid': "1111",
            'vm_cmp_id': "1",
            'vendor': "test-vendor",
            'operating_system': "test-os"
        }
        test_get = {'resources': [{'name': expected_result['vm_fqdn'],
                                'uid_ems': expected_result['vm_uuid'],
                                'id': expected_result['vm_cmp_id'],
                                'vendor': expected_result['vendor'],
                                'archived': False,
                                'orphaned': False,
                                'operating_system': {
                                    'product_name': expected_result['operating_system']}}]}

        mock_connect = MagicMock()
        mock_session.return_value = mock_connect

        mock_response = self._mock_response(json_data=test_get)
        mock_connect.get.return_value = mock_response

        result_value = action.run(**test_dict)
        self.assertEqual(result_value, [expected_result])

    @mock.patch("lib.vm_all_get.GetAllVMs.build_session")
    def test_run_archived_vm_present(self, mock_session):
        action = self.get_action_instance({})
        test_dict = {'server': 'test.dev.encore.tech',
                   'username': 'user',
                   'password': 'pass'}
        expected_result = {
            'vm_fqdn': "test-name",
            'vm_uuid': "1111",
            'vm_cmp_id': "1",
            'vendor': "test-vendor",
            'operating_system': "test-os"
        }
        test_get = {'resources': [{'name': expected_result['vm_fqdn'],
                                'uid_ems': expected_result['vm_uuid'],
                                'id': expected_result['vm_cmp_id'],
                                'vendor': expected_result['vendor'],
                                'archived': False,
                                'orphaned': False,
                                'operating_system': {
                                    'product_name': expected_result['operating_system']}},
                                {'name': "test-name-2",
                                'uid_ems': "22222",
                                'id': "2",
                                'vendor': expected_result['vendor'],
                                'archived': True,
                                'orphaned': False,
                                'operating_system': {
                                    'product_name': expected_result['operating_system']}}]}

        mock_connect = MagicMock()
        mock_session.return_value = mock_connect

        mock_response = self._mock_response(json_data=test_get)
        mock_connect.get.return_value = mock_response

        result_value = action.run(**test_dict)
        self.assertEqual(result_value, [expected_result])

    @mock.patch("lib.vm_all_get.GetAllVMs.build_session")
    def test_run_orphaned_vm_present(self, mock_session):
        action = self.get_action_instance({})
        test_dict = {'server': 'test.dev.encore.tech',
                   'username': 'user',
                   'password': 'pass'}
        expected_result = {
            'vm_fqdn': "test-name",
            'vm_uuid': "1111",
            'vm_cmp_id': "1",
            'vendor': "test-vendor",
            'operating_system': "test-os"
        }
        test_get = {'resources': [{'name': expected_result['vm_fqdn'],
                                'uid_ems': expected_result['vm_uuid'],
                                'id': expected_result['vm_cmp_id'],
                                'vendor': expected_result['vendor'],
                                'archived': False,
                                'orphaned': False,
                                'operating_system': {
                                    'product_name': expected_result['operating_system']}},
                                {'name': "test-name-2",
                                'uid_ems': "22222",
                                'id': "2",
                                'vendor': expected_result['vendor'],
                                'archived': False,
                                'orphaned': True,
                                'operating_system': {
                                    'product_name': expected_result['operating_system']}}]}

        mock_connect = MagicMock()
        mock_session.return_value = mock_connect

        mock_response = self._mock_response(json_data=test_get)
        mock_connect.get.return_value = mock_response

        result_value = action.run(**test_dict)
        self.assertEqual(result_value, [expected_result])
