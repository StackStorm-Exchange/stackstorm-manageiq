from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.template_get_info import Temp
from st2common.runners.base_action import Action

import mock


class TestActionTempOSName(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = Temp

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, Temp)
        self.assertIsInstance(action, Action)

    def test_tmpl_get_info(self):
        action = self.get_action_instance({})
        id = '100008'
        kwargs_dict = {'template_id': id}
        expected_os = {'product_name': 'expected_os'}
        expected_result = {
            'operating_system': 'expected_os',
            'name': "RHEL7"
        }

        # mocks
        mock_tmpl = mock.MagicMock(operating_system=expected_os)
        # Mock the 'name' attribute to use for the template name
        p = mock.PropertyMock(return_value='RHEL7')
        type(mock_tmpl).name = p

        mock_client = mock.MagicMock()
        mock_client.collections.templates.return_value = mock_tmpl

        # execute
        result = action.tmpl_get_info(mock_client, kwargs_dict)

        # asserts
        self.assertEquals(result, expected_result)
        mock_tmpl.reload.assert_called_with(attributes='operating_system')
        mock_client.collections.templates.assert_called_with(id)
