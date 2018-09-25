import base_action


class Temp(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(Temp, self).__init__(config)

    def tmpl_get_info(self, client, kwargs_dict):
        """Return the name of the template and its Operating System
        :param client: connection from base_action
        :param kwargs_dict:
        :returns: dict containing the name of the template and its OS
        :rtype: string
        """
        id = self._get_arg("template_id", kwargs_dict)
        tmpl = client.collections.templates(id)
        tmpl.reload(attributes='operating_system')
        result = {
            'operating_system': tmpl.operating_system['product_name'],
            'name': tmpl.name
        }
        return result
