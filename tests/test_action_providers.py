from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.providers import Providers
from st2common.runners.base_action import Action

import mock


class TestActionProviders(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = Providers

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, Providers)
        self.assertIsInstance(action, Action)

    def test__get_providers_query(self):
        action = self.get_action_instance({})
        result = action._get_providers_query()
        self.assertEquals(result, {'expand': 'resources',
                                   'attributes': ('authentication_status')})

    @mock.patch("lib.base_action.BaseAction._get_objects")
    def test_credentials_test(self, mock__get_objects):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {}

        # mock
        mock__get_objects.return_value = [{'name': 'provider1.domain.tld',
                                           'authentication_status': 'valid'},
                                          {'name': 'provider2.domain.tld',
                                           'authentication_status': 'VaLiD'}]

        # execute
        result = action.credentials_test(client, kwargs_dict)

        # assert
        self.assertEquals(result, (True,
                                   [{'name': 'provider1.domain.tld',
                                     'status': 'OK',
                                     'valid': True},
                                    {'name': 'provider2.domain.tld',
                                     'status': 'OK',
                                     'valid': True}]))
        mock__get_objects.assert_called_with(client=client,
                                             collection_name="providers",
                                             query_dict=action._get_providers_query())

    @mock.patch("lib.base_action.BaseAction._get_objects")
    def test_credentials_test_error(self, mock__get_objects):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {}

        # mock
        mock__get_objects.return_value = [{'name': 'provider1.domain.tld',
                                           'authentication_status': 'some bad state'}]

        # execute
        result = action.credentials_test(client, kwargs_dict)

        # assert
        self.assertEquals(result, (False,
                                   [{'name': 'provider1.domain.tld',
                                     'status': 'ERROR',
                                     'valid': False}]))
        mock__get_objects.assert_called_with(client=client,
                                             collection_name="providers",
                                             query_dict=action._get_providers_query())
