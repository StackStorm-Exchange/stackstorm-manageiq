from st2common.runners.base_action import Action
from manageiq_client.api import ManageIQClient as MiqApi
from manageiq_client.filters import Q

# silence SSL warnings
try:
    import requests
    requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member
except:
    pass

try:
    import urllib3
    urllib3.disable_warnings()
except:
    pass


class BaseAction(Action):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(BaseAction, self).__init__(config)

    def _get_arg(self, key, kwargs_dict):
        """Attempts to retrieve an argument from kwargs with key.
        If the key is found, then delete it from the dict.
        :param key: the key of the argument to retrieve from kwargs
        :returns: The value of key in kwargs, if it exists, otherwise None
        """
        if key in kwargs_dict:
            value = kwargs_dict[key]
            del key
            return value
        else:
            return None

    def _attributes_str(self, attributes_list):
        return ','.join(attributes_list)

    def _data_from_entity_list(self, entity_list):
        data = []
        for e in entity_list:
            data.append(e._data)
        return data

    def _resources_from_search_results(self, search_results):
        return self._data_from_entity_list(search_results.resources)

    def _get_objects(self, client, collection_name, query_dict):
        _query_dict = dict(query_dict)

        # run the query
        collection = getattr(client.collections, collection_name)
        search_results = collection.query_string(**_query_dict)
        resources = self._resources_from_search_results(search_results)
        return resources

    def _get_object(self, client, collection_name, name, query_dict):
        _query_dict = dict(query_dict)
        _query_dict['filter[]'] = Q.from_dict({'name': name}).as_filters

        resources = self._get_objects(client, collection_name, _query_dict)

        obj = None
        if len(resources) > 0:
            self.logger.debug("{} '{}' already exists.".format(collection_name, name))
            # this object already exists
            obj = resources[0]
        else:
            self.logger.debug("{} '{}' does not exists.".format(collection_name, name))

        return obj

    def _create_object(self, client, collection_name, query_dict, payload):
        self.logger.debug("creating {} '{}' .".format(collection_name, payload))

        # create a new object
        collection = getattr(client.collections, collection_name)
        create_response = collection.action.create(**payload)

        if len(create_response) <= 0:
            raise RuntimeError("create {} response is empty! {}".format(collection,
                                                                        create_response))

        obj = create_response[0]._data

        if 'id' not in obj:
            raise KeyError("'id' field is not in the returned {}! obj={} response={}"
                           .format(collection_name, obj, create_response))

        obj_id = obj['id']

        # get the object after creating (so we can get all the right fields)
        obj_response = collection(obj_id)
        obj_response.reload(**query_dict)
        return obj_response._data

    def _get_or_create_object(self, client, collection_name, name, query_dict, payload):
        obj = self._get_object(client, collection_name, name, query_dict)
        if obj is None:
            obj = self._create_object(client, collection_name, query_dict, payload)

        return obj

    def run(self, **kwargs):
        kwargs_dict = dict(kwargs)
        server = self._get_arg("server", kwargs_dict)
        username = self._get_arg("username", kwargs_dict)
        password = self._get_arg("password", kwargs_dict)
        operation = self._get_arg("operation", kwargs_dict)

        client = MiqApi("https://" + server + "/api",
                        (username, password),
                        verify_ssl=False)

        # call the operation by name
        operation_func = getattr(self, operation)
        return operation_func(client, kwargs_dict)
