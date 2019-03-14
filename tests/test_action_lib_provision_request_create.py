from manage_iq_base_action_test_case import ManageIQBaseActionTestCase

from lib.provision_request_create import ProvisionRequestCreate
from st2common.runners.base_action import Action

from mock import patch, MagicMock


class TestActionVm(ManageIQBaseActionTestCase):
    __test__ = True
    action_cls = ProvisionRequestCreate

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, ProvisionRequestCreate)
        self.assertIsInstance(action, Action)

    def test_create_request_payload(self):
        action = self.get_action_instance({})
        kwargs_dict = {
            'vm_dns_records': 'test_dns_record',
            'owner_name': 'Test Name',
            'template_guid': '1234567',
            'cpu_count': 1,
            'hostname': 'testname',
            'dns_domain': 'domain.tech',
            'memory_mb': '1024',
            'owner_email': 'test_email@gmail.com',
            'folder': '/test/folder/path',
            'ad_dns_domain': 'name.tech',
            'ad_username': 'user',
            'ad_password': 'pass',
            'host_id': '1000000123',
            'datastore_id': '1000000789',
            'domain_type': 'domain',
            'num_adapters': 1,
            'tags_list': {'tag': 'test'},
            'description': 'test notes'
        }

        expected_results = {
            'version': '1.1',
            'template_fields': {
                'guid': '1234567'
            },
            'vm_fields': {
                'number_of_sockets': 1,
                'vm_name': 'testname.domain.tech',
                'vm_memory': '1024'
            },
            'requester': {
                'owner_first_name': 'Test',
                'owner_last_name': 'Name',
                'owner_email': 'test_email@gmail.com',
                'auto_approve': True
            },
            'tags': {
                'tag': 'test'
            },
            'additional_values': {
                'domain': 'domain.tech',
                'folder': '/test/folder/path',
                'hostname': 'testname',
                'st2_vars': {
                    'ad_dns_domain': 'name.tech',
                    'ad_username': 'user',
                    'ad_password': 'pass',
                    'host_id': '1000000123',
                    'datastore_id': '1000000789',
                    'domain_type': 'domain',
                    'num_adapters': 1,
                    'vm_dns_records': 'test_dns_record'
                },
                'vm_notes': 'test notes'
            },
            'ems_custom_attributes': {},
            'miq_custom_attributes': {}
        }

        # execute
        results = action.create_request_payload(kwargs_dict)

        # asserts
        self.assertEquals(results, expected_results)

    @patch("lib.provision_request_create.base_action.BaseAction._create_object")
    def test_provision_request_create(self, mock_create_object):
        action = self.get_action_instance({})

        kwargs_dict = {
            'vm_dns_records': 'test_dns_record',
            'owner_name': 'Test Name',
            'template_guid': '1234567',
            'cpu_count': 1,
            'hostname': 'testname',
            'dns_domain': 'domain.tech',
            'memory_mb': '1024',
            'owner_email': 'test_email@gmail.com',
            'folder': '/test/folder/path',
            'ad_dns_domain': 'name.tech',
            'ad_username': 'user',
            'ad_password': 'pass',
            'host_id': '1000000123',
            'datastore_id': '1000000789',
            'domain_type': 'domain',
            'num_adapters': 1,
            'tags_list': {'tag': 'test'},
            'description': 'test notes'
        }

        client = MagicMock()

        # Mock the post result content from the make_api_request function
        mock_create_object.return_value = "expected result"

        payload = action.create_request_payload(kwargs_dict)
        result = action.provision_request_create(client, kwargs_dict)

        self.assertEqual(result, "expected result")
        # The JSON loads function must be called with the post result
        mock_create_object.assert_called_with(client, 'provision_requests', {}, payload)
