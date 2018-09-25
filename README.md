[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-manageiq.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-manageiq) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


# ManageIQ Integration Pack

This pack provides an integration between StackStorm and [ManageIQ](http://manageiq.org/).
The actions in this pack are designed to mimic the [ManageIQ REST API](http://manageiq.org/docs/api).

# <a name="quickstart"></a> Quick Start

**Steps**

1. Install the pack

    ``` shell
    st2 pack install manageiq
    ```

2. Run an action to list all VMs

    ``` shell
    st2 run manageiq.vm_list server='manageiq.domain.tld' username='admin' password='xxx'
    ```

# <a name="configuration"></a> Configuration

This pack does not require a configuration file. All connection parameters must be passed
into each action individually. A configuration file to store connection information
maybe be added in a future release.

# <a name="actions"></a> Actions

Actions in this pack are based off of the [ManageIQ REST API](http://manageiq.org/docs/api).

| Action | Description |
|--------|-------------|
| manageiq.bestfit | Determine the BestFit for new VM via ManageIQ |
| manageiq.credentials_test | Tests if a set of credentials is valid for a ManageIQ server |
| manageiq.hosts_credentials_test | Tests if the stored credentials is ManageIQ are valid for all hosts (hypervisors) in the system. |
| manageiq.providers_credentials_test | Tests if the stored credentials is ManageIQ are valid for all providers (hypervisors) in the system. |
| manageiq.provision_check_complete | Check if a given provision request is complete and return the new VM ID |
| manageiq.provision_check_success | Check if a given provision request is complete and return the new VM ID |
| manageiq.provision_request_create | Create a provision request via the MIQ API |
| manageiq.remove_old_snapshots | Removes any snapshots older than the specified age |
| manageiq.tags_assign | Assigns a set of tags to an item in a collection |
| manageiq.tags_create | Creates a set of tags in ManageIQ |
| manageiq.tags_delete | Delets a set of tags (and categories) in ManageIQ |
| manageiq.tags_get | Retrieves tags for an item in a collection |
| manageiq.tags_list | List all tags in the ManageIQ system |
| manageiq.tags_unassign | Removes a set of tags from an item in a collection |
| manageiq.template_get_info | Get the Operating System and template name from the MIQ template |
| manageiq.vm_all_get | Gets all VMs that are not archived or orphaned. |
| manageiq.vm_check_removed | Check if a given VM ID is found in the VMDB |
| manageiq.vm_custom_attributes_delete | Deletes custom attributes on a VM |
| manageiq.vm_custom_attributes_get | Reads a single custom attributes on the VM |
| manageiq.vm_custom_attributes_list | Reads all of the custom attributes on the VM |
| manageiq.vm_custom_attributes_set | Sets custom attributes on a VM (use this for both add and update) |
| manageiq.vm_find_by_name | Finds a VM by name |
| manageiq.vm_get_ids | Use the VMs MIQ ID to get its EMS UUID and MOID from the API |
| manageiq.vm_list | List all VMs in the ManageIQ system |
| manageiq.vm_retire | Retire a VM with a given ID |
| manageiq.vm_retire_now | Retire a VM with a given ID |
| manageiq.vm_scan | Initiates a SmartState Analysis scan asynchronously on a VM |

# Future

- Create a config file for storing commonly used credentials
- Auto-generate actions from the API (unfortunately there is no spec)

