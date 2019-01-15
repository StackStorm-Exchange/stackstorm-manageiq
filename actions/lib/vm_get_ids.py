from lib import base_action


class VmGetIDs(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(VmGetIDs, self).__init__(config)

    def get_ids(self, client, kwargs_dict):
        """Use the VMs MIQ ID to get its EMS UUID and MOID from the API
        :param client: connection from the base_action
        :param kwargs_dict:
        :returns: a dictionary of the VM IDs returned from ManageIQ
        :rtype: dict
        """
        id = self._get_arg("vm_id", kwargs_dict)
        vm = client.collections.vms(id)
        result = {
            'vm_cmp_id': id,
            'vm_uuid': vm.uid_ems,
            'vm_moid': vm.ems_ref
        }
        return result
