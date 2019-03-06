import base_action


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

    def refresh(self, client, kwargs_dict):
        """Refresh the specified provider in ManageIQ. If no ID is given then
         all providers will be refreshed.
        :param client: ManageIQClient class object from manageiq_client.api
        :param kwargs_dict: Inputs from the Stackstorm action
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        providers = self._get_objects(client=client,
                                      collection_name="providers",
                                      query_dict={'expand': 'resources'})

        resources = []
        # If a provider ID was specified, only refresh that one
        if kwargs_dict['provider_id']:
            print("Provider ID Given")
            for prov in providers:
                if str(prov['id']) == kwargs_dict['provider_id']:
                    resources.append(prov)
                    break
        else:
            resources = providers

        endpoint = "https://" + kwargs_dict['server'] + "/api/providers"

        result = client.post(url=endpoint, action="refresh", resources=resources)

        return result['results']
