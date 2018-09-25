import base_action


class ProvisionRequestCreate(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(ProvisionRequestCreate, self).__init__(config)

    def create_request_payload(self, kwargs_dict):
        """Create the payload for the CloudForms or ManageIQ API call
        :param kwargs_dict: inputs in dict form
        """
        vm_dns_records = kwargs_dict['vm_dns_records']

        owner_name = kwargs_dict['owner_name'].split(' ')
        owner_first = owner_name[0]

        owner_last = owner_name[1] if len(owner_name) > 1 else ''

        payload = {
            'version': '1.1',
            'template_fields': {
                'guid': kwargs_dict['template_guid']
            },
            'vm_fields': {
                'number_of_sockets': kwargs_dict['cpu_count'],
                'vm_name': kwargs_dict['hostname'] + '.' + kwargs_dict['dns_domain'],
                'vm_memory': kwargs_dict['memory_mb']
            },
            'requester': {
                'owner_first_name': owner_first,
                'owner_last_name': owner_last,
                'owner_email': kwargs_dict['owner_email'],
                'auto_approve': True
            },
            'tags': kwargs_dict['tags_list'],
            'additional_values': {
                'domain': kwargs_dict['dns_domain'],
                'folder': kwargs_dict['folder'],
                'hostname': kwargs_dict['hostname'],
                'st2_vars': {
                    'ad_dns_domain': kwargs_dict['ad_dns_domain'],
                    'ad_username': kwargs_dict['ad_username'],
                    'ad_password': kwargs_dict['ad_password'],
                    'host_id': kwargs_dict['host_id'],
                    'datastore_id': kwargs_dict['datastore_id'],
                    'domain_type': kwargs_dict['domain_type'],
                    'num_adapters': int(kwargs_dict['num_adapters']),
                    'vm_dns_records': vm_dns_records
                },
                'vm_notes': kwargs_dict['description']
            },
            'ems_custom_attributes': {},
            'miq_custom_attributes': {}
        }
        return payload

    def provision_request_create(self, client, kwargs_dict):
        """Create a provision request via the MIQ API
        :param client: connection from the base_action
        :param kwargs_dict:
        :returns: a list of provision tasks
        :rtype: list
        """
        payload = self.create_request_payload(kwargs_dict)

        result = self._create_object(client, 'provision_requests', {}, payload)

        return result
