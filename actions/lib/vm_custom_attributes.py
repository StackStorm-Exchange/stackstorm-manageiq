import base_action
from manageiq_client.filters import Q


class VmCustomAttributes(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(VmCustomAttributes, self).__init__(config)

    def _get_query(self):
        return {'expand': 'resources'}

    def _validate(self, custom_attribute, value_required=None):
        if value_required is None:
            value_required = True

        required_keys = ['key']
        if value_required:
            required_keys.append('value')

        for required in required_keys:
            if required not in custom_attribute:
                raise RuntimeError("{} missing from custom_attribute: {}"
                                   .format(required, custom_attribute))

        return True

    def _post_action(self, client, kwargs_dict, action):
        id = self._get_arg("id", kwargs_dict)
        custom_attributes = self._get_arg("custom_attributes", kwargs_dict)

        resources = []
        for attr in custom_attributes:
            self._validate(attr, value_required=False)
            resource = {'name': attr['key']}
            if action == 'add':
                resource['value'] = attr['value']

            resources.append(resource)

        object_response = client.collections.vms(id)
        action_obj = getattr(object_response.custom_attributes.action, action)
        return action_obj(*resources)

    def list(self, client, kwargs_dict):
        """List all of the custom attributes on a VM
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        id = self._get_arg("id", kwargs_dict)
        query_dict = self._get_query()

        object_response = client.collections.vms(id)
        search_results = object_response.custom_attributes.query_string(**query_dict)
        return self._resources_from_search_results(search_results)

    def get(self, client, kwargs_dict):
        """Reads a single custom attributes on the VM
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        id = self._get_arg("id", kwargs_dict)
        key = self._get_arg("key", kwargs_dict)

        query_dict = self._get_query()
        query_dict['filter[]'] = Q.from_dict({'name': key}).as_filters

        object_response = client.collections.vms(id)
        search_results = object_response.custom_attributes.query_string(**query_dict)
        return self._resources_from_search_results(search_results)

    def set(self, client, kwargs_dict):
        """Set a custom attribute on a VM
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        return self._post_action(client, kwargs_dict, "add")

    def delete(self, client, kwargs_dict):
        """ Deletes a set of custom attributes on a VM
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        return self._post_action(client, kwargs_dict, "delete")
