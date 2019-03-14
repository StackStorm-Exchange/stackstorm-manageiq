from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.tags import Tags
from st2common.runners.base_action import Action

import mock


class TestActionTags(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = Tags

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, Tags)
        self.assertIsInstance(action, Action)

    def test__get_tags_query(self):
        action = self.get_action_instance({})
        result = action._get_tags_query()
        self.assertEquals(result, {'expand': 'resources',
                                   'attributes': ('category,category.name,'
                                                  'classification,classification.name')})

    def test__get_categories_query(self):
        action = self.get_action_instance({})
        result = action._get_categories_query()
        self.assertEquals(result, {'expand': 'resources'})

    def test__validate_tag(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key0', 'value': 'test_value0'}
        result = action._validate_tag(custom_attributes)
        self.assertEquals(result, True)

    def test__validate_tag_missing_value_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key1'}
        with self.assertRaises(RuntimeError):
            action._validate_tag(custom_attributes)

    def test__validate_tag_missing_key_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'value': 'test_value1'}
        with self.assertRaises(RuntimeError):
            action._validate_tag(custom_attributes)

    def test__validate_tag_with_description(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key0',
                             'value': 'test_value0',
                             'key_description': 'test_key_desc0',
                             'value_description': 'test_value_desc0'}
        result = action._validate_tag(custom_attributes, with_descriptions=True)
        self.assertEquals(result, True)

    def test__validate_tag_with_description_missing_value_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key0',
                             'key_description': 'test_key_desc0',
                             'value_description': 'test_value_desc0'}
        with self.assertRaises(RuntimeError):
            action._validate_tag(custom_attributes, with_descriptions=True)

    def test__validate_tag_with_description_missing_key_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'value': 'test_value0',
                             'key_description': 'test_key_desc0',
                             'value_description': 'test_value_desc0'}
        with self.assertRaises(RuntimeError):
            action._validate_tag(custom_attributes, with_descriptions=True)

    def test__validate_tag_with_description_missing_key_description_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key0',
                             'value': 'test_value0',
                             'value_description': 'test_value_desc0'}
        with self.assertRaises(RuntimeError):
            action._validate_tag(custom_attributes, with_descriptions=True)

    def test__validate_tag_with_description_missing_value_description_raises(self):
        action = self.get_action_instance({})
        custom_attributes = {'key': 'test_key0',
                             'value': 'test_value0',
                             'key_description': 'test_key_desc0'}
        with self.assertRaises(RuntimeError):
            action._validate_tag(custom_attributes, with_descriptions=True)

    @mock.patch("lib.tags.base_action.BaseAction._get_or_create_object")
    def test__get_or_create_category(self, mock_get_or_create):
        action = self.get_action_instance({})
        client = "client"
        name = 'tag key'
        tag = {'key': name,
               'key_description': 'tag key description',
               'value': 'tag value',
               'value_description': 'tag value description'}
        expected_payload = {'name': tag['key'],
                            'description': tag['key_description']}
        expected_result = "result"

        mock_get_or_create.return_value = expected_result

        result = action._get_or_create_category(client, tag)

        self.assertEquals(result, expected_result)
        mock_get_or_create.assert_called_with(client=client,
                                              collection_name="categories",
                                              name=name,
                                              query_dict=action._get_categories_query(),
                                              payload=expected_payload)

    @mock.patch("lib.tags.base_action.BaseAction._get_object")
    def test__get_category(self, mock_get):
        action = self.get_action_instance({})
        client = "client"
        name = 'tag key'
        tag = {'key': name}
        expected_result = "result"

        mock_get.return_value = expected_result

        result = action._get_category(client, tag)

        self.assertEquals(result, expected_result)
        mock_get.assert_called_with(client=client,
                                    collection_name="categories",
                                    name=name,
                                    query_dict=action._get_categories_query())

    @mock.patch("lib.tags.base_action.BaseAction._get_or_create_object")
    def test__get_or_create_tag(self, mock_get_or_create):
        action = self.get_action_instance({})
        client = "client"
        tag = {'key': 'tag key',
               'key_description': 'tag key description',
               'value': 'tag value',
               'value_description': 'tag value description'}
        name = "/managed/{category}/{tag}".format(category=tag['key'],
                                                  tag=tag['value'])
        category = {'href': 'category_href'}
        expected_payload = {'name': tag['value'],
                            'description': tag['value_description'],
                            'category': category}
        expected_result = "result"

        mock_get_or_create.return_value = expected_result

        result = action._get_or_create_tag(client, tag, category)

        self.assertEquals(result, expected_result)
        mock_get_or_create.assert_called_with(client=client,
                                              collection_name="tags",
                                              name=name,
                                              query_dict=action._get_tags_query(),
                                              payload=expected_payload)

    @mock.patch("lib.tags.base_action.BaseAction._get_object")
    def test__get_tag(self, mock_get):
        action = self.get_action_instance({})
        client = "client"
        name = 'tag key'
        tag = {'key': 'tag key',
               'value': 'tag value'}
        name = "/managed/{category}/{tag}".format(category=tag['key'],
                                                  tag=tag['value'])
        expected_result = "result"

        mock_get.return_value = expected_result

        result = action._get_tag(client, tag)

        self.assertEquals(result, expected_result)
        mock_get.assert_called_with(client=client,
                                    collection_name="tags",
                                    name=name,
                                    query_dict=action._get_tags_query())

    def test_list(self):
        action = self.get_action_instance({})
        resources_data = [{'name': 'data0'},
                          {'name': 'data1'},
                          {'name': 'data2'}]
        kwargs_dict = {}

        # mock
        resources = [mock.MagicMock(_data=r) for r in resources_data]
        mock_search_results = mock.MagicMock(resources=resources)

        mock_client = mock.MagicMock()
        mock_client.collections.tags.query_string.return_value = mock_search_results

        # execute
        result = action.list(mock_client, kwargs_dict)

        # assert
        self.assertEquals(result, resources_data)

    @mock.patch("lib.tags.Tags._get_or_create_tag")
    @mock.patch("lib.tags.Tags._get_or_create_category")
    def test_create(self, mock_create_category, mock_create_tag):
        action = self.get_action_instance({})
        client = "client"
        tags = [{'key': 'key0',
                 'value': 'value0',
                 'key_description': 'key_desc0',
                 'value_description': 'value_desc0'},
                {'key': 'key1',
                 'value': 'value1',
                 'key_description': 'key_desc2',
                 'value_description': 'value_desc2'},
                {'key': 'key2',
                 'value': 'value2',
                 'key_description': 'key_desc2',
                 'value_description': 'value_desc2'}]
        kwargs_dict = {'tags': tags}

        expected_categories = ['cat0', 'cat1', 'cat2']
        expected_tags = ['tag0', 'tag1', 'tag2']
        mock_create_category.side_effect = expected_categories
        mock_create_tag.side_effect = expected_tags

        results = action.create(client, kwargs_dict)

        self.assertEquals(results, {'tags': expected_tags,
                                    'categories': expected_categories})

    @mock.patch("lib.tags.Tags._resources_from_search_results")
    def test_get(self, mock_resources_func):
        action = self.get_action_instance({})
        collection_name = "vms"
        id = 12
        kwargs_dict = {'collection': collection_name,
                       'id': id}
        search_results = "search results"
        expected_results = "results"
        query_dict = action._get_tags_query()

        # mock
        mock_vm = mock.MagicMock()
        mock_vm.tags.query_string.return_value = search_results

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        mock_resources_func.return_value = expected_results

        # execute
        result = action.get(mock_client, kwargs_dict)

        # assert
        self.assertEquals(result, expected_results)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.tags.query_string.assert_called_with(**query_dict)
        mock_resources_func.assert_called_with(search_results)

    def test__tag_action(self):
        action = self.get_action_instance({})

        collection_name = 'vms'
        id = "100"
        action_name = 'assign'
        tags = [{'key': 'key0', 'value': 'value0'},
                {'key': 'key1', 'value': 'value1'},
                {'key': 'key2', 'value': 'value2'}]
        kwargs_dict = {'collection': collection_name,
                       'id': id,
                       'tags': tags}

        # expected
        expected_result = [{'name': 'data0'},
                           {'name': 'data1'},
                           {'name': 'data2'}]
        assign_result = [mock.MagicMock(_data=r) for r in expected_result]
        expected_resources = []
        for tag in tags:
            expected_resources.append({'category': tag['key'],
                                       'name': tag['value']})

        # mock
        mock_vm = mock.MagicMock()
        mock_vm.tags.action.assign.return_value = assign_result

        mock_client = mock.MagicMock()
        mock_client.collections.vms.return_value = mock_vm

        # execute
        result = action._tag_action(mock_client, kwargs_dict, action_name)

        # assert
        self.assertEquals(result, expected_result)
        mock_client.collections.vms.assert_called_with(id)
        mock_vm.tags.action.assign.assert_called_with(*expected_resources)

    @mock.patch('lib.tags.Tags._tag_action')
    def test_assign(self, mock__tag_action):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {'junk': 'dict'}
        expected = "result"
        mock__tag_action.return_value = expected

        result = action.assign(client, kwargs_dict)

        self.assertEquals(result, expected)
        mock__tag_action.assert_called_with(client=client,
                                            kwargs_dict=kwargs_dict,
                                            action='assign')

    @mock.patch('lib.tags.Tags._tag_action')
    def test_unassign(self, mock__tag_action):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {'junk': 'dict'}
        expected = "result"
        mock__tag_action.return_value = expected

        result = action.unassign(client, kwargs_dict)

        self.assertEquals(result, expected)
        mock__tag_action.assert_called_with(client=client,
                                            kwargs_dict=kwargs_dict,
                                            action='unassign')

    def test__should_delete_missing_key(self):
        action = self.get_action_instance({})
        key = "value"
        delete_key = "delete_value"
        default = True
        tag = {}

        result = action._should_delete(tag, key, delete_key, default)

        self.assertEquals(result, False)

    def test__should_delete_default_true(self):
        action = self.get_action_instance({})
        key = "value"
        delete_key = "delete_value"
        default = True
        tag = {key: 'xxx'}

        result = action._should_delete(tag, key, delete_key, default)

        self.assertEquals(result, True)

    def test__should_delete_default_override_false(self):
        action = self.get_action_instance({})
        key = "value"
        delete_key = "delete_value"
        default = True
        tag = {key: 'xxx',
               delete_key: False}

        result = action._should_delete(tag, key, delete_key, default)

        self.assertEquals(result, False)

    def test__should_delete_default_override_true(self):
        action = self.get_action_instance({})
        key = "value"
        delete_key = "delete_value"
        default = False
        tag = {key: 'xxx',
               delete_key: True}

        result = action._should_delete(tag, key, delete_key, default)

        self.assertEquals(result, True)

    @mock.patch('lib.tags.Tags._get_tag')
    @mock.patch('lib.tags.Tags._get_category')
    def test_delete(self, mock_get_category, mock_get_tag):
        action = self.get_action_instance({})
        tags = [{'key': 'key_0', 'value': 'value_0'},
                {'key': 'key_1', 'value': 'value_1'},
                {'key': 'key_2', 'value': 'value_2'}]
        kwargs_dict = {'tags': tags,
                       'delete_keys': True,
                       'delete_values': True}

        mock_get_category.side_effect = [{'href': 'cat_href_0'},
                                         {'href': 'cat_href_1'},
                                         {'href': 'cat_href_2'}]

        mock_get_tag.side_effect = [{'href': 'tag_href_0'},
                                    {'href': 'tag_href_1'},
                                    {'href': 'tag_href_2'}]

        mock_client = mock.MagicMock()
        mock_client.delete.side_effect = ['value0', 'key0', 'value1', 'key1', 'value2', 'key2']

        result = action.delete(mock_client, kwargs_dict)

        self.assertEquals(result, {'keys': ['key0', 'key1', 'key2'],
                                   'values': ['value0', 'value1', 'value2']})
        calls = [mock.call(mock_client, t) for t in tags]
        mock_get_category.assert_has_calls(calls)
        mock_get_tag.assert_has_calls(calls)

    @mock.patch('lib.tags.Tags._get_tag')
    @mock.patch('lib.tags.Tags._get_category')
    def test_delete_empty(self, mock_get_category, mock_get_tag):
        action = self.get_action_instance({})
        tags = []
        kwargs_dict = {'tags': tags,
                       'delete_keys': True,
                       'delete_values': True}
        mock_client = mock.MagicMock()

        result = action.delete(mock_client, kwargs_dict)

        self.assertEquals(result, {'keys': [],
                                   'values': []})
        self.assertFalse(mock_get_category.called)
        self.assertFalse(mock_get_tag.called)

    @mock.patch('lib.tags.Tags._get_tag')
    @mock.patch('lib.tags.Tags._get_category')
    def test_delete_nonexisting_category(self, mock_get_category, mock_get_tag):
        action = self.get_action_instance({})
        tags = [{'key': 'key_0', 'value': 'value_0'},
                {'key': 'key_1', 'value': 'value_1'},
                {'key': 'key_2', 'value': 'value_2'}]
        kwargs_dict = {'tags': tags,
                       'delete_keys': True,
                       'delete_values': True}

        mock_client = mock.MagicMock()
        mock_get_category.side_effect = [None for t in tags]

        result = action.delete(mock_client, kwargs_dict)

        self.assertEquals(result, {'keys': [],
                                   'values': []})
        calls = [mock.call(mock_client, t) for t in tags]
        mock_get_category.assert_has_calls(calls)
        self.assertFalse(mock_get_tag.called)

    @mock.patch('lib.tags.Tags._get_tag')
    @mock.patch('lib.tags.Tags._get_category')
    def test_delete_values_global(self, mock_get_category, mock_get_tag):
        action = self.get_action_instance({})
        tags = [{'key': 'key_0', 'value': 'value_0'},
                {'key': 'key_1', 'value': 'value_1'},
                {'key': 'key_2', 'value': 'value_2'}]
        kwargs_dict = {'tags': tags,
                       'delete_keys': False,
                       'delete_values': True}

        expected_keys = []
        expected_values = [t['value'] for t in tags]

        mock_client = mock.MagicMock()
        mock_client.delete.side_effect = expected_values

        mock_get_category.side_effect = [{'href': t['key']} for t in tags]
        mock_get_tag.side_effect = [{'href': t['value']} for t in tags]

        result = action.delete(mock_client, kwargs_dict)

        self.assertEquals(result, {'keys': expected_keys,
                                   'values': expected_values})
        calls = [mock.call(mock_client, t) for t in tags]
        mock_get_category.assert_has_calls(calls)
        mock_get_tag.assert_has_calls(calls)

        calls = [mock.call(t['value']) for t in tags]
        mock_client.delete.assert_has_calls(calls)

    @mock.patch('lib.tags.Tags._get_tag')
    @mock.patch('lib.tags.Tags._get_category')
    def test_delete_keys_global(self, mock_get_category, mock_get_tag):
        action = self.get_action_instance({})
        tags = [{'key': 'key_0', 'value': 'value_0'},
                {'key': 'key_1', 'value': 'value_1'},
                {'key': 'key_2', 'value': 'value_2'}]
        kwargs_dict = {'tags': tags,
                       'delete_keys': True,
                       'delete_values': False}

        expected_keys = [t['key'] for t in tags]
        expected_values = []

        mock_client = mock.MagicMock()
        mock_client.delete.side_effect = expected_keys

        mock_get_category.side_effect = [{'href': t['key']} for t in tags]
        mock_get_tag.side_effect = [{'href': t['value']} for t in tags]

        result = action.delete(mock_client, kwargs_dict)

        self.assertEquals(result, {'keys': expected_keys,
                                   'values': expected_values})
        calls = [mock.call(mock_client, t) for t in tags]
        mock_get_category.assert_has_calls(calls)
        mock_get_tag.assert_has_calls(calls)

        calls = [mock.call(t['key']) for t in tags]
        mock_client.delete.assert_has_calls(calls)

    @mock.patch('lib.tags.Tags._get_tag')
    @mock.patch('lib.tags.Tags._get_category')
    def test_delete_individual(self, mock_get_category, mock_get_tag):
        action = self.get_action_instance({})
        tags = [{'key': 'key_0', 'value': 'value_0', 'delete_value': True},
                {'key': 'key_1', 'value': 'value_1', 'delete_key': True},
                {'key': 'key_2', 'value': 'value_2'}]
        kwargs_dict = {'tags': tags,
                       'delete_keys': False,
                       'delete_values': False}

        mock_client = mock.MagicMock()
        mock_client.delete.side_effect = ['value_0', 'key_1']

        mock_get_category.side_effect = [{'href': t['key']} for t in tags]
        mock_get_tag.side_effect = [{'href': t['value']} for t in tags]

        result = action.delete(mock_client, kwargs_dict)

        self.assertEquals(result, {'keys': ['key_1'],
                                   'values': ['value_0']})
