import base_action


class ProvCheckComplete(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(ProvCheckComplete, self).__init__(config)

    def provision_check_complete(self, client, kwargs_dict):
        """Check if a given provision request is complete and fail if it isn't
        :param client: connection from the base_action
        :param kwargs_dict:
        """
        id = self._get_arg("request_id", kwargs_dict)
        request = client.collections.provision_requests(id)

        if(request.request_state != 'finished'):
            raise RuntimeError('The Provision Request is not finished executing!')

        return True
