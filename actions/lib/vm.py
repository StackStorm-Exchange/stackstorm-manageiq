from manageiq_client.filters import Q
from lib import base_action


class Vm(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(Vm, self).__init__(config)

    def list(self, client, kwargs_dict):
        """List all of the VMs in the system
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        list_query = {'expand': 'resources',
                      'attributes': self._attributes_str(['id', 'name'])}
        search_results = client.collections.vms.query_string(**list_query)
        return self._resources_from_search_results(search_results)

    def find_by_name(self, client, kwargs_dict):
        """Finds a VM by name
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        name = self._get_arg("name", kwargs_dict)
        attributes = self._get_arg("attributes", kwargs_dict)
        params = {'expand': 'resources',
                  'filter[]': Q.from_dict({'name': name}).as_filters}
        search_results = client.collections.vms.query_string(**params)
        vm = search_results.resources[0]

        # If needing to get additional attributes
        if len(attributes) > 0:
            vm.reload(attributes=attributes)

        return vm._data

    def scan(self, client, kwargs_dict):
        """Initiates a SmartState Analysis scan asynchronously on a VM
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        id = self._get_arg("id", kwargs_dict)
        vm = client.collections.vms(id)
        result = vm.action.scan()
        return result._data

    def retire(self, client, kwargs_dict):
        """Initiates a retirement on a VM
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        id = self._get_arg("id", kwargs_dict)
        vm = client.collections.vms(id)
        result = vm.action.retire()
        return result._data

    def check_removed(self, client, kwargs_dict):
        """Return an error if a given VM has not been removed from the VMDB
        :param client: connection from the base_action
        :param kwargs_dict:
        """
        id = self._get_arg("id", kwargs_dict)
        vm = client.collections.vms(id)
        # If the VM exists, raise an error so a retry loop can check again
        if vm.exists:
            raise RuntimeError('VM found with ID: ' + str(vm.id))

        return True
