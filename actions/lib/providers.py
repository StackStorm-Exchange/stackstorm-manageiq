from lib import base_action


class Providers(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(Providers, self).__init__(config)

    def _get_providers_query(self):
        return {'expand': 'resources',
                'attributes': self._attributes_str(['authentication_status'])}

    def credentials_test(self, client, kwargs_dict):
        """Tests if the stored credentials is ManageIQ are valid for all providers (hypervisors)
         in the system.
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        query_dict = self._get_providers_query()
        providers = self._get_objects(client=client,
                                      collection_name="providers",
                                      query_dict=query_dict)
        results = []
        all_valid = True
        for p in providers:
            valid = True
            if p['authentication_status'].lower() == 'valid':
                status = 'OK'
            else:
                status = 'ERROR'
                valid = False
                all_valid = False

            results.append({'name': p['name'],
                            'status': status,
                            'valid': valid})

        return (all_valid, results)
