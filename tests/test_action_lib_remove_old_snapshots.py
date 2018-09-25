from manage_iq_base_action_test_case import ManageIQBaseActionTestCase
from lib.remove_old_snapshots import RemoveOldSnapshots

from st2common.runners.base_action import Action

import mock
import datetime
import requests


class TestRemoveOldSnapshots(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = RemoveOldSnapshots

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
        self.assertIsInstance(action, RemoveOldSnapshots)
        self.assertIsInstance(action, Action)

    def test_create_session(self):
        action = self.get_action_instance({})

        result = action.create_session('user', 'pass')

        self.assertIsInstance(result, requests.Session)
        self.assertEqual(result.auth, ('user', 'pass'))
        self.assertEqual(result.verify, False)

    def test_get_vms(self):
        action = self.get_action_instance({})
        action.server = "server.tld"

        mock_response = mock.MagicMock()
        mock_response.json.return_value = {'resources': 'vms_json'}

        mock_session = mock.MagicMock()
        mock_session.get.return_value = mock_response
        action.session = mock_session

        result = action.get_vms()

        self.assertEquals(result, 'vms_json')
        mock_session.get.assert_called_with("https://server.tld/api/vms?"
                                            "expand=resources&attributes=id,"
                                            "snapshots,name")
        mock_response.raise_for_status.assert_called_with()

    def test_compile_regexes(self):
        action = self.get_action_instance({})
        regex_list = [".*", "^#DONTDELETE$"]

        result = action.compile_regexes(regex_list)

        self.assertIsInstance(result, list)
        self.assertEquals(len(result), len(regex_list))
        for i in range(len(result)):
            self.assertEquals(result[i].pattern, regex_list[i])

    def test_matches_pattern_list_match(self):
        action = self.get_action_instance({})
        regex_list = ["abc123", "^.*#DONTDELETE$"]
        pattern_list = action.compile_regexes(regex_list)

        name = "xxx #DONTDELETE"
        result = action.matches_pattern_list(name, pattern_list)

        self.assertTrue(result)

    def test_matches_pattern_list_no_match(self):
        action = self.get_action_instance({})
        regex_list = ["abc123", "^#DONTDELETE$"]
        pattern_list = action.compile_regexes(regex_list)

        name = "xxx"
        result = action.matches_pattern_list(name, pattern_list)

        self.assertFalse(result)

    # Test run when there are no old snapshots on any VMs
    @mock.patch("lib.remove_old_snapshots.RemoveOldSnapshots.create_session")
    @mock.patch("lib.remove_old_snapshots.RemoveOldSnapshots.current_time_utc")
    def test_run_no_old_snapshots(self, mock_current_time_utc, mock_create_session):
        action = self.get_action_instance({})

        # expected
        kwargs_dict = {'server': 'test.dev.encore.tech',
                       'username': 'user',
                       'password': 'pass',
                       'max_age_days': 3,
                       'name_ignore_regexes': ['^.*#DONTDELETE$']}
        test_get = {'resources': [{'name': 'test',
                                  'snapshots': [{'created_on': '2018-01-04T00:00:00Z',
                                                'vm_or_template_id': '1000000000001',
                                                'id': '1000000000002',
                                                'name': 'test1'},
                                                {'created_on': '2018-01-05T00:00:00Z',
                                                'vm_or_template_id': '1000000000003',
                                                'id': '1000000000004',
                                                'name': 'test2'}]}]}

        # mocks
        # One of the dates in "expected_results" is 4 days older than the following date
        mock_current_time_utc.return_value = datetime.datetime(2018, 1, 5, 0, 0)

        mock_session = mock.MagicMock()
        mock_create_session.return_value = mock_session

        mock_response = self._mock_response(json_data=test_get)
        mock_session.get.return_value = mock_response

        # execute
        result_value = action.run(**kwargs_dict)

        expected_results = (True, {'deleted_snapshots': [],
                                   'ignored_snapshots': []})

        # asserts
        mock_session.get.assert_called_with("https://test.dev.encore.tech/api/"
                                            "vms?expand=resources&attributes=id,snapshots,name")
        self.assertTrue(mock_response.raise_for_status.called)
        self.assertEqual(result_value, expected_results)

    # Test run when there are old snapshots on a VM
    @mock.patch("lib.remove_old_snapshots.RemoveOldSnapshots.create_session")
    @mock.patch("lib.remove_old_snapshots.RemoveOldSnapshots.current_time_utc")
    def test_run_old_snapshots(self, mock_current_time_utc, mock_create_session):
        action = self.get_action_instance({})

        # expected
        kwargs_dict = {'server': 'test.dev.encore.tech',
                       'username': 'user',
                       'password': 'pass',
                       'max_age_days': 3,
                       'name_ignore_regexes': ['^.*#DONTDELETE$']}
        test_get = {'resources': [{'name': 'test',
                                   'snapshots': [{'created_on': '2018-01-01T00:00:00Z',
                                                  'vm_or_template_id': '1000000000001',
                                                  'id': '1000000000002',
                                                  'name': 'test1'},
                                                 {'created_on': '2018-01-05T00:00:00Z',
                                                  'vm_or_template_id': '1000000000003',
                                                  'id': '1000000000004',
                                                  'name': 'test2'},
                                                 {'created_on': '2018-01-01T00:00:00Z',
                                                  'vm_or_template_id': '1000000000005',
                                                  'id': '1000000000005',
                                                  'name': 'abc #DONTDELETE'}]}]}

        expected_results = (True, {'deleted_snapshots': ['test: test1'],
                                   'ignored_snapshots': ['test: abc #DONTDELETE']})

        # mocks
        # One of the dates in "expected_results" is 4 days older than the following date
        mock_current_time_utc.return_value = datetime.datetime(2018, 1, 5, 0, 0)

        mock_session = mock.MagicMock()
        mock_create_session.return_value = mock_session

        mock_response = self._mock_response(json_data=test_get)
        mock_session.get.return_value = mock_response

        # execute
        result_value = action.run(**kwargs_dict)

        # asserts
        mock_session.get.assert_called_with("https://test.dev.encore.tech/api/"
                                            "vms?expand=resources&attributes=id,snapshots,name")
        mock_session.delete.assert_called_with("https://test.dev.encore.tech/api/vms/"
                                               "1000000000001/snapshots/1000000000002")
        self.assertTrue(mock_response.raise_for_status.called)
        self.assertEqual(result_value, expected_results)
