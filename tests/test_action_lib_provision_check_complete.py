from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.provision_check_complete import ProvCheckComplete
from st2common.runners.base_action import Action

import mock


class TestActionProvCheck(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = ProvCheckComplete

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, ProvCheckComplete)
        self.assertIsInstance(action, Action)

    def test_provision_check_complete(self):
        action = self.get_action_instance({})
        request_id = '100008'
        kwargs_dict = {'request_id': request_id}

        # mocks
        mock_request = mock.MagicMock(request_state='finished')
        mock_client = mock.MagicMock()
        mock_client.collections.provision_requests.return_value = mock_request

        # execute
        result = action.provision_check_complete(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, True)
        mock_client.collections.provision_requests.assert_called_with(request_id)

    def test_provision_check_complete_not_finished(self):
        action = self.get_action_instance({})
        request_id = '100008'
        kwargs_dict = {'request_id': request_id}

        # mocks
        mock_request = mock.MagicMock(tasks='Test Tasks', request_state='running')
        mock_client = mock.MagicMock()
        mock_client.collections.provision_requests.return_value = mock_request

        # execute
        with self.assertRaises(RuntimeError):
            action.provision_check_complete(mock_client, kwargs_dict)
