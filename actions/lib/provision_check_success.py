import base_action


class ProvCheckSuccess(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(ProvCheckSuccess, self).__init__(config)

    def get_vm_miq_id(self, provision_tasks):
        """Parse the Provision Message from ManageIQ to get the VM ID
        :param provision_tasks: List of provision tasks from ManageIQ
        """
        # There should be only one task in the list
        for task in provision_tasks:
            if 'destination_id' in task:
                return str(task['destination_id'])

        return 'error'

    def provision_check_success(self, client, kwargs_dict):
        """Check if a given provision request succeeded and return the new VM ID
        :param client: connection from the base_action
        :param kwargs_dict:
        :returns: ID of the VM that was provisioned
        :rtype: string
        """
        id = self._get_arg("request_id", kwargs_dict)
        request = client.collections.provision_requests(id)
        request.reload(attributes='tasks')

        prov_task_list = self._data_from_entity_list(request.tasks)

        vm_id = self.get_vm_miq_id(prov_task_list)

        if(vm_id == 'error'):
            raise ValueError("CloudForms Error: " + request.message)

        # Return the task list that contains the ID for the new VM
        return vm_id
