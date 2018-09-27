from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.bestfit import BestFit
from st2common.runners.base_action import Action

import mock


class BestFitTestCase(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = BestFit

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, BestFit)
        self.assertIsInstance(action, Action)

    def test_filter_datastores_regex_match(self):
        action = self.get_action_instance({})
        test_dict = {'datastoreFilterRegEx': {"filters": ["(?i)(iso)"]}}
        test_name = "dev_isos"
        expected_output = False
        result_output = action._filter_datastores(test_name, test_dict)
        self.assertEqual(expected_output, result_output)

    def test_filter_datastores_regex_no_match(self):
        action = self.get_action_instance({})
        test_dict = {'datastoreFilterRegEx': {"filters": ["(?i)(iso)"]}}
        test_name = "testdatastore"
        expected_output = True
        result_output = action._filter_datastores(test_name, test_dict)
        self.assertEqual(expected_output, result_output)

    def test_filter_datastores_name_match(self):
        action = self.get_action_instance({})
        test_dict = {'datastoreFilterRegEx': {"filters": ["dev_isos"]}}
        test_name = "dev_isos"
        expected_output = False
        result_output = action._filter_datastores(test_name, test_dict)
        self.assertEqual(expected_output, result_output)

    def test_filter_datastores_name_no_match(self):
        action = self.get_action_instance({})
        test_dict = {'datastoreFilterRegEx': {"filters": ["dev_isos"]}}
        test_name = "testdatastore"
        expected_output = True
        result_output = action._filter_datastores(test_name, test_dict)
        self.assertEqual(expected_output, result_output)

    def test_check_storages(self):
        action = self.get_action_instance({})
        test_dict = {'datastoreFilterRegEx': {"filters": ["dev_isos"]}}
        test_storages = [{'storage_id': 1}]
        expected_result = {'id': 1,
                           'name': "abc",
                           'free_space': 100}

        mock_datastore = mock.Mock(id=expected_result['id'],
                                   free_space=expected_result['free_space'])
        name_property = mock.PropertyMock(return_value=expected_result['name'])
        type(mock_datastore).name = name_property
        mock_client = mock.MagicMock()
        mock_client.collections.data_stores.return_value = mock_datastore

        result_name, result_id = action._check_storages(mock_client, test_storages, test_dict)
        self.assertEquals(result_name, expected_result['name'])
        self.assertEquals(result_id, str(expected_result['id']))

    def test_find_storage(self):
        action = self.get_action_instance({})
        test_datastore_name = "test"
        expected_result = {'id': 1,
                           'name': test_datastore_name,
                           'free_space': 100}

        mock_datastore = mock.Mock(id=expected_result['id'],
                                   free_space=expected_result['free_space'])
        name_property = mock.PropertyMock(return_value=expected_result['name'])
        type(mock_datastore).name = name_property
        mock_data_stores = mock.Mock(all=[mock_datastore])
        mock_collections = mock.Mock(data_stores=mock_data_stores)
        mock_client = mock.Mock(collections=mock_collections)

        result_name, result_id = action._find_storage(mock_client, test_datastore_name)
        self.assertEquals(result_name, expected_result['name'])
        self.assertEquals(result_id, str(expected_result['id']))

    @mock.patch("lib.bestfit.BestFit._find_storage")
    def test__load_disks(self, mock__find_storage):
        action = self.get_action_instance({})
        test_json = {"all_disks":
                    [{"size_gb": "35",
                    "uuid": "6000C29c-8b35-69bc-dcb6-efd847c579e7",
                    "key": "2000",
                    "datastore": "abc"}]}
        test_datastore = {'id': 1,
                          'name': "abc",
                          'free_space': 100}
        expected_result = (test_datastore['name'], str(test_datastore['id']))
        mock__find_storage.return_value = expected_result
        mock_client = mock.MagicMock()
        result = action._load_disks(mock_client, test_json)
        self.assertEqual(result, expected_result)

    def test_check_hosts(self):
        action = self.get_action_instance({})
        test_dict = {'clusterName': "test_cluster",
                     'datastoreFilterRegEx': {"filters": ["dev_isos"]}}
        test_storages = [{'storage_id': 1}]
        test_datastore = {'id': 1,
                          'name': "abc",
                          'free_space': 100}
        test_hosts = [{'v_owning_cluster': "test_cluster",
                       'v_total_vms': 5,
                       'id': 1,
                       'name': "test_host_1",
                       'host_storages': test_storages}]
        expected_result = (True, {'clusterName': test_dict['clusterName'],
                                  'hostName': test_hosts[0]['name'],
                                  'hostID': str(test_hosts[0]['id']),
                                  'datastoreName': test_datastore['name'],
                                  'datastoreID': str(test_datastore['id'])})

        mock_datastore = mock.Mock(id=test_datastore['id'],
                                   free_space=test_datastore['free_space'])
        datastore_name_property = mock.PropertyMock(return_value=test_datastore['name'])
        type(mock_datastore).name = datastore_name_property

        mock_host = mock.Mock(v_owning_cluster=test_hosts[0]['v_owning_cluster'],
                              v_total_vms=test_hosts[0]['v_total_vms'],
                              id=test_hosts[0]['id'],
                              host_storages=test_hosts[0]['host_storages'],
                              power_state='on')
        host_name_property = mock.PropertyMock(return_value=test_hosts[0]['name'])
        type(mock_host).name = host_name_property
        mock_client = mock.MagicMock()
        mock_client.collections.data_stores.return_value = mock_datastore

        result = action._check_hosts(mock_client, [mock_host], test_dict)
        self.assertEquals(result, expected_result)

    def test_check_hosts_empty_cluster_raises(self):
        action = self.get_action_instance({})
        client = None
        hosts = []
        kwargs = {'clusterName': None}
        with self.assertRaises(ValueError):
            action._check_hosts(client, hosts, kwargs)

    def test_check_hosts_empty_hosts_fails(self):
        action = self.get_action_instance({})
        client = None
        hosts = []
        kwargs = {'clusterName': 'testCluster'}
        result = action._check_hosts(client, hosts, kwargs)
        self.assertEquals(result, (False, {'clusterName': 'testCluster',
                                           'hostName': None,
                                           'hostID': None,
                                           'datastoreName': None,
                                           'datastoreID': None}))

    def test_check_hosts_no_hosts_in_cluster_fails(self):
        action = self.get_action_instance({})
        client = None
        hosts = [
            mock.MagicMock(v_own_cluster='otherCluster'),
            mock.MagicMock(v_own_cluster='testCluster', power_state='off'),
        ]
        kwargs = {'clusterName': 'testCluster'}
        result = action._check_hosts(client, hosts, kwargs)
        self.assertEquals(result, (False, {'clusterName': 'testCluster',
                                           'hostName': None,
                                           'hostID': None,
                                           'datastoreName': None,
                                           'datastoreID': None}))

    @mock.patch("lib.bestfit.BestFit._check_storages")
    def test_check_hosts_no_datastore_fails(self, mock_check_storages):
        action = self.get_action_instance({})
        mock_check_storages.return_value = (None, None)
        client = None
        hosts = [
            mock.MagicMock(v_own_cluster='testCluster', power_state='on'),
        ]

        kwargs = {'clusterName': 'testCluster'}
        result = action._check_hosts(client, hosts, kwargs)
        self.assertEquals(result, (False, {'clusterName': 'testCluster',
                                           'hostName': None,
                                           'hostID': None,
                                           'datastoreName': None,
                                           'datastoreID': None}))

    @mock.patch("lib.bestfit.BestFit._load_disks")
    def test_check_hosts_disk_datastore(self, mock__load_disks):
        action = self.get_action_instance({})
        test_storages = [{'storage_id': 1}]
        test_datastore = {'id': 1,
                          'name': "abc",
                          'free_space': 100}
        test_dict = {'clusterName': "test_cluster",
                     'datastoreFilterRegEx': {"filters": ["dev_isos"]},
                     'disk_json': '[{"datastore":"abc"}]'}
        test_hosts = [{'v_owning_cluster': "test_cluster",
                       'v_total_vms': 5,
                       'id': 1,
                       'name': "test_host_1",
                       'host_storages': test_storages}]
        expected_result = (True, {'clusterName': test_dict['clusterName'],
                                  'hostName': test_hosts[0]['name'],
                                  'hostID': str(test_hosts[0]['id']),
                                  'datastoreName': test_datastore['name'],
                                  'datastoreID': str(test_datastore['id'])})

        mock_host = mock.Mock(v_owning_cluster=test_hosts[0]['v_owning_cluster'],
                              v_total_vms=test_hosts[0]['v_total_vms'],
                              id=test_hosts[0]['id'],
                              host_storages=test_hosts[0]['host_storages'],
                              power_state='on')
        host_name_property = mock.PropertyMock(return_value=test_hosts[0]['name'])
        type(mock_host).name = host_name_property
        mock_client = mock.MagicMock()
        mock__load_disks.return_value = (test_datastore['name'], str(test_datastore['id']))

        result = action._check_hosts(mock_client, [mock_host], test_dict)
        self.assertEquals(result, expected_result)

    @mock.patch("lib.bestfit.BestFit._check_hosts")
    def test_bestfit(self, mock_check_hosts):
        action = self.get_action_instance(self.config_blank)
        test_dict = {'username': 'user',
                     'password': 'pass',
                     'endpoint': 'endpoint'}
        test_storages = [{'storage_id': 1}]
        test_hosts = [{'v_owning_cluster': "test_cluster",
                       'v_total_vms': 5,
                       'id': 1,
                       'name': "test_host_1",
                       'host_storages': test_storages}]

        check_hosts_result = (True, "check_hosts result")
        mock_check_hosts.return_value = check_hosts_result

        mock_host = mock.Mock(v_owning_cluster=test_hosts[0]['v_owning_cluster'],
                              v_total_vms=test_hosts[0]['v_total_vms'],
                              id=test_hosts[0]['id'],
                              host_storages=test_hosts[0]['host_storages'])
        host_name_property = mock.PropertyMock(return_value=test_hosts[0]['name'])
        type(mock_host).name = host_name_property
        mock_client = mock.MagicMock()
        mock_client.collections.hosts.query_string.return_value = [mock_host]

        result = action.bestfit(mock_client, test_dict)
        self.assertEquals(result, check_hosts_result)
