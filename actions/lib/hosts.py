import base_action


class Hosts(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(Hosts, self).__init__(config)

    def _get_hosts_query(self):
        return {'expand': 'resources',
                'attributes': self._attributes_str(['power_status',
                                                    'authentication_status'])}

    def credentials_test(self, client, kwargs_dict):
        """Tests if the stored credentials is ManageIQ are valid for all hosts (hypervisors)
         in the system.
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        query_dict = self._get_hosts_query()
        hosts = self._get_objects(client=client,
                                  collection_name="hosts",
                                  query_dict=query_dict)
        results = []
        all_valid = True
        for h in hosts:
            valid = True
            if h['power_state'].lower() == 'maintenance':
                status = 'MAINTENANCE'
            elif h['power_state'].lower() == 'off':
                status = 'POWERED OFF'
            elif h['authentication_status'].lower() == 'valid':
                status = 'OK'
            else:
                status = 'ERROR'
                valid = False
                all_valid = False

            results.append({'name': h['name'],
                            'status': status,
                            'valid': valid})

        return (all_valid, results)
