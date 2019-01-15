from lib import base_action


class Tags(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(Tags, self).__init__(config)

    def _get_tags_query(self):
        return {'expand': 'resources',
                'attributes': self._attributes_str(['category',
                                                    'category.name',
                                                    'classification',
                                                    'classification.name'])}

    def _get_categories_query(self):
        return {'expand': 'resources'}

    def _validate_tag(self, tag, with_descriptions=None):
        if with_descriptions is None:
            with_descriptions = False

        required_keys = ['key', 'value']
        if with_descriptions:
            required_keys.extend(['key_description', 'value_description'])

        for required in required_keys:
            if required not in tag:
                raise RuntimeError("{} missing from tag: {}".format(required, tag))

        return True

    def _get_or_create_category(self, client, tag):
        name = tag['key']
        description = tag['key_description']
        payload = {'name': name,
                   'description': description}
        query_dict = self._get_categories_query()
        return self._get_or_create_object(client=client,
                                          collection_name="categories",
                                          name=name,
                                          query_dict=query_dict,
                                          payload=payload)

    def _get_category(self, client, tag):
        name = tag['key']
        query_dict = self._get_categories_query()
        return self._get_object(client=client,
                                collection_name="categories",
                                name=name,
                                query_dict=query_dict)

    def _get_or_create_tag(self, client, tag, category):
        name = "/managed/{category}/{tag}".format(category=tag['key'],
                                                  tag=tag['value'])
        description = tag['value_description']
        # the name in the payload is _just_ the tag name, not the
        # full path that's needed when querying
        payload = {'name': tag['value'],
                   'description': description,
                   'category': {'href': category['href']}}
        query_dict = self._get_tags_query()
        return self._get_or_create_object(client=client,
                                          collection_name="tags",
                                          name=name,
                                          query_dict=query_dict,
                                          payload=payload)

    def _get_tag(self, client, tag):
        name = "/managed/{category}/{tag}".format(category=tag['key'],
                                                  tag=tag['value'])
        query_dict = self._get_tags_query()
        return self._get_object(client=client,
                                collection_name="tags",
                                name=name,
                                query_dict=query_dict)

    def list(self, client, kwargs_dict):
        """List all of the tags in the system
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        query_dict = self._get_tags_query()
        search_results = client.collections.tags.query_string(**query_dict)
        return self._resources_from_search_results(search_results)

    def create(self, client, kwargs_dict):
        """Create a list of tags in the system
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        tags = self._get_arg("tags", kwargs_dict)
        results = {'categories': [],
                   'tags': []}
        for tag in tags:
            self._validate_tag(tag, with_descriptions=True)

            category = self._get_or_create_category(client, tag)
            results['categories'].append(category)

            tag = self._get_or_create_tag(client, tag, category)
            results['tags'].append(tag)

        return results

    def get(self, client, kwargs_dict):
        """ Gets all of the tags for an item in a collection
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        collection_name = self._get_arg("collection", kwargs_dict)
        id = self._get_arg("id", kwargs_dict)
        query_dict = self._get_tags_query()

        collection = getattr(client.collections, collection_name)
        object_response = collection(id)
        search_results = object_response.tags.query_string(**query_dict)
        return self._resources_from_search_results(search_results)

    def _tag_action(self, client, kwargs_dict, action):
        collection_name = self._get_arg("collection", kwargs_dict)
        id = self._get_arg("id", kwargs_dict)
        tags = self._get_arg("tags", kwargs_dict)

        resources = []
        for tag in tags:
            self._validate_tag(tag)
            resources.append({'category': tag['key'],
                              'name': tag['value']})

        collection = getattr(client.collections, collection_name)
        object_response = collection(id)
        action_obj = getattr(object_response.tags.action, action)
        action_result = action_obj(*resources)
        return self._data_from_entity_list(action_result)

    def assign(self, client, kwargs_dict):
        """ Assign a list of tags to an item in a collection
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        return self._tag_action(client=client,
                                kwargs_dict=kwargs_dict,
                                action="assign")

    def unassign(self, client, kwargs_dict):
        """ Removes a list of tags from an item in a collection
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        return self._tag_action(client=client,
                                kwargs_dict=kwargs_dict,
                                action="unassign")

    def _should_delete(self, tag, key, delete_key, default):
        should_delete = default
        if delete_key in tag:
            should_delete = tag[delete_key]

        if key in tag and should_delete:
            return True

        return False

    def delete(self, client, kwargs_dict):
        """ Deletes a set of tags and categories
        :param client:
        :param kwargs_dict:
        :returns: a dictionary of the results returned from ManageIQ
        :rtype: dict
        """
        del_keys = self._get_arg("delete_keys", kwargs_dict)
        del_vals = self._get_arg("delete_values", kwargs_dict)
        tags = self._get_arg("tags", kwargs_dict)

        results = {'keys': [],
                   'values': []}
        for tag in tags:
            existing_category = self._get_category(client, tag)

            if not existing_category:
                continue

            existing_tag = self._get_tag(client, tag)

            # delete tag (value)
            if existing_tag and self._should_delete(tag, 'value', 'delete_value', del_vals):
                results['values'].append(client.delete(existing_tag['href']))

            # delete category (key)
            if self._should_delete(tag, 'key', 'delete_key', del_keys):
                results['keys'].append(client.delete(existing_category['href']))

        return results

    # TODO

    # taggings
    # https://xxx/api/tags/100000000000182?expand=resources&attributes=taggings

    # collection tagged with
    # /api/vms?expand=resources&attributes=tags&filter[]=tags.name='/managed/category/tag'
