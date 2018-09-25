import base_action


class VmRetireNow(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(VmRetireNow, self).__init__(config)

    def retire_now(self, client, kwargs_dict):
        """Initiates the custom retire now action that doesn't wait for a grace period
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        id = self._get_arg("id", kwargs_dict)
        action = self._get_arg("action", kwargs_dict)
        vm = client.collections.vms(id)
        retire_action = getattr(vm.action, action)
        result = retire_action(check_box="t")
        return result._data
