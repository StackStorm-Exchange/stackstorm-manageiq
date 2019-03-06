from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.hosts import Hosts
from st2common.runners.base_action import Action

import mock


# class TestActionHosts(ManageIQBaseActionTestCase):
class TestActionHosts(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = Hosts

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, Hosts)
        self.assertIsInstance(action, Action)

    def test__get_hosts_query(self):
        action = self.get_action_instance({})
        result = action._get_hosts_query()
        self.assertEquals(result, {'expand': 'resources',
                                   'attributes': ('power_status,'
                                                  'authentication_status')})

    @mock.patch("lib.hosts.base_action.BaseAction._get_objects")
    def test_credentials_test(self, mock__get_objects):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {}

        # mock
        mock__get_objects.return_value = [{'name': 'host1.domain.tld',
                                           'power_state': 'on',
                                           'authentication_status': 'valid'},
                                          {'name': 'host2.domain.tld',
                                           'power_state': 'on',
                                           'authentication_status': 'VaLiD'}]

        # execute
        result = action.credentials_test(client, kwargs_dict)

        # assert
        self.assertEquals(result, (True,
                                   [{'name': 'host1.domain.tld',
                                     'status': 'OK',
                                     'valid': True},
                                    {'name': 'host2.domain.tld',
                                     'status': 'OK',
                                     'valid': True}]))
        mock__get_objects.assert_called_with(client=client,
                                             collection_name="hosts",
                                             query_dict=action._get_hosts_query())

    @mock.patch("lib.hosts.base_action.BaseAction._get_objects")
    def test_credentials_test_maintenance(self, mock__get_objects):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {}

        # mock
        mock__get_objects.return_value = [{'name': 'host1.domain.tld',
                                           'power_state': 'maintenance',
                                           'authentication_status': 'some bad state'},
                                          {'name': 'host2.domain.tld',
                                           'power_state': 'MaiNTeNanCe',
                                           'authentication_status': 'valid'}]

        # execute
        result = action.credentials_test(client, kwargs_dict)

        # assert
        self.assertEquals(result, (True,
                                   [{'name': 'host1.domain.tld',
                                     'status': 'MAINTENANCE',
                                     'valid': True},
                                    {'name': 'host2.domain.tld',
                                     'status': 'MAINTENANCE',
                                     'valid': True}]))
        mock__get_objects.assert_called_with(client=client,
                                             collection_name="hosts",
                                             query_dict=action._get_hosts_query())

    @mock.patch("lib.hosts.base_action.BaseAction._get_objects")
    def test_credentials_test_powered_off(self, mock__get_objects):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {}

        # mock
        mock__get_objects.return_value = [{'name': 'host1.domain.tld',
                                           'power_state': 'off',
                                           'authentication_status': 'some bad state'},
                                          {'name': 'host2.domain.tld',
                                           'power_state': 'OfF',
                                           'authentication_status': 'valid'}]

        # execute
        result = action.credentials_test(client, kwargs_dict)

        # assert
        self.assertEquals(result, (True,
                                   [{'name': 'host1.domain.tld',
                                     'status': 'POWERED OFF',
                                     'valid': True},
                                    {'name': 'host2.domain.tld',
                                     'status': 'POWERED OFF',
                                     'valid': True}]))
        mock__get_objects.assert_called_with(client=client,
                                             collection_name="hosts",
                                             query_dict=action._get_hosts_query())

    @mock.patch("lib.hosts.base_action.BaseAction._get_objects")
    def test_credentials_test_error(self, mock__get_objects):
        action = self.get_action_instance({})
        client = "client"
        kwargs_dict = {}

        # mock
        mock__get_objects.return_value = [{'name': 'host1.domain.tld',
                                           'power_state': 'on',
                                           'authentication_status': 'some bad state'}]

        # execute
        result = action.credentials_test(client, kwargs_dict)

        # assert
        self.assertEquals(result, (False,
                                   [{'name': 'host1.domain.tld',
                                     'status': 'ERROR',
                                     'valid': False}]))
        mock__get_objects.assert_called_with(client=client,
                                             collection_name="hosts",
                                             query_dict=action._get_hosts_query())
