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

    @mock.patch("lib.providers.base_action.BaseAction._get_objects")
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

    @mock.patch("lib.providers.base_action.BaseAction._get_objects")
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

    @mock.patch("lib.providers.base_action.BaseAction._get_objects")
    def test_refresh_all_providers(self, mock__get_objects):
        action = self.get_action_instance({})
        kwargs_dict = {'server': 'test.com',
                       'provider_id': None}
        test_result = "test result"
        test_providers = [{'name': 'provider1.domain.tld',
                           'id': '123456'},
                          {'name': 'provider2.domain.tld',
                           'id': '654321'}]

        # mock
        mock_client = mock.MagicMock()
        mock_client.post.return_value = {'results': test_result}
        mock__get_objects.return_value = test_providers

        # execute
        result = action.refresh(mock_client, kwargs_dict)

        # assert
        self.assertEquals(result, test_result)
        mock__get_objects.assert_called_with(client=mock_client,
                                             collection_name="providers",
                                             query_dict={'expand': 'resources'})

        mock_client.post.assert_called_with(url="https://test.com/api/providers",
                                            action="refresh",
                                            resources=test_providers)

    @mock.patch("lib.providers.base_action.BaseAction._get_objects")
    def test_refresh_one_provider(self, mock__get_objects):
        action = self.get_action_instance({})
        kwargs_dict = {'server': 'test.com',
                       'provider_id': '654321'}
        test_result = "test result"
        test_providers = [{'name': 'provider1.domain.tld',
                           'id': '123456'},
                          {'name': 'provider2.domain.tld',
                           'id': '654321'}]

        # mock
        mock_client = mock.MagicMock()
        mock_client.post.return_value = {'results': test_result}
        mock__get_objects.return_value = test_providers

        # execute
        result = action.refresh(mock_client, kwargs_dict)
        # assert
        self.assertEquals(result, test_result)
        mock__get_objects.assert_called_with(client=mock_client,
                                             collection_name="providers",
                                             query_dict={'expand': 'resources'})

        mock_client.post.assert_called_with(url="https://test.com/api/providers",
                                            action="refresh",
                                            resources=[{'name': 'provider2.domain.tld',
                                                        'id': '654321'}])
