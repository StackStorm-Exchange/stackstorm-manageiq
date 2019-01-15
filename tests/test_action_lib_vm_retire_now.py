from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.vm_retire_now import VmRetireNow
from st2common.runners.base_action import Action

import mock


class TestActionVmRetireNow(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = VmRetireNow

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, VmRetireNow)
        self.assertIsInstance(action, Action)

    @mock.patch("lib.vm_retire_now.VmRetireNow._foo", create=True)
    def test_retire_now(self, mock__foo):
        action = self.get_action_instance({})
        id = '100008'
        kwargs_dict = {'id': id, 'action': '_foo'}
        expected_result = 'expected_result'

        # mocks
        mock_action = mock.MagicMock(_foo=mock__foo)
        mock_vm = mock.MagicMock(action=mock_action)

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        mock_result = mock.MagicMock()
        mock_vm.return_value = mock_result

        p = mock.PropertyMock(return_value=expected_result)
        type(mock__foo.return_value)._data = p

        # execute
        result = action.retire_now(mock_client, kwargs_dict)

        print(result)

        # asserts
        self.assertEquals(result, expected_result)
        mock_client.collections.vms.assert_called_with(id)
        mock__foo.assert_called_with(check_box="t")
