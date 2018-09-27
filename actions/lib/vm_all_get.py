#!/usr/bin/env python

import requests
from st2common.runners.base_action import Action


class GetAllVMs(Action):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(GetAllVMs, self).__init__(config)

    def get_arg(self, key, kwargs_dict, delete=False):
        """Attempts to retrieve an argument from kwargs with key.
        If the key is found, then delete it from the dict.
        :param key: the key of the argument to retrieve from kwargs
        :returns: The value of key in kwargs, if it exists, otherwise None
        """
        if key in kwargs_dict:
            value = kwargs_dict[key]
            if delete:
                del kwargs_dict[key]
            return value
        else:
            return None

    def build_session(self, kwargs_dict):
        """Connect to MIQ with credentials from the key/value store
        :returns: the connection session to manageiq
        """
        username = self.get_arg('username', kwargs_dict)
        password = self.get_arg('password', kwargs_dict)

        session = requests.Session()
        session.auth = (username, password)
        session.verify = False

        return session

    def run(self, **kwargs):
        """Main entry point for the StackStorm actions to execute the operation.
        """
        kwargs_dict = dict(kwargs)

        # Connect to the API and return the session
        session = self.build_session(kwargs_dict)

        server = self.get_arg('server', kwargs_dict)

        attributes_list = [
            "id",
            "name",
            "uid_ems",
            "vendor",
            "operating_system",
            "archived",
            "orphaned"
        ]

        response = session.get("https://{0}/api/vms?expand=resources&attributes={1}".format(server,
            ','.join(attributes_list)))
        response.raise_for_status()
        vms = response.json()["resources"]

        all_vms = []
        for vm in vms:
            if not vm['archived'] and not vm['orphaned']:
                vm_info = {
                    'vm_fqdn': vm['name'],
                    'vm_uuid': vm['uid_ems'],
                    'vm_cmp_id': str(vm['id']),
                    'vendor': vm['vendor'],
                    'operating_system': vm['operating_system']['product_name']
                }
                all_vms.append(vm_info)

        return all_vms
