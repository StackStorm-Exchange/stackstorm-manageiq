from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.vm_get_ids import VmGetIDs
from st2common.runners.base_action import Action

import mock


class TestActionVmRetire(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = VmGetIDs

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, VmGetIDs)
        self.assertIsInstance(action, Action)

    def test_vm_get_ids(self):
        action = self.get_action_instance({})

        test_dict = {"vm_id": "10000001"}

        expected_return = {
            "vm_cmp_id": "10000001",
            "vm_uuid": "422f2290-e116-c407-9169-0da7dca8dac2",
            "vm_moid": "vm-152512"}

        # mocks
        mock_vm = mock.MagicMock(uid_ems="422f2290-e116-c407-9169-0da7dca8dac2",
                                 ems_ref="vm-152512")
        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action.get_ids(mock_client, test_dict)

        # asserts
        self.assertEquals(result, expected_return)
        mock_client.collections.vms.assert_called_with('10000001')
