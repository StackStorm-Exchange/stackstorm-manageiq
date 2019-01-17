import base_action
import re
import json


class BestFit(base_action.BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(BestFit, self).__init__(config)

    def _load_disks(self, client, disks):
        """If disks json is present this gets the first disk information
        and returns the proper information.
        """
        datastoreName = None
        datastoreID = None
        first_disk = disks['all_disks'][0]
        datastore_name = first_disk['datastore']
        if datastore_name is not "automatic":
            datastoreName, datastoreID = self._find_storage(client, datastore_name)

        return (datastoreName, datastoreID)

    def _check_hosts(self, client, hosts, kwargs_dict):
        cluster = self._get_arg("clusterName", kwargs_dict)
        if not cluster:
            raise ValueError("Cluster Name can not be empty.")

        leastVMs = None
        hostID = None
        hostName = None
        datastoreName = None
        datastoreID = None

        disks = self._get_arg("disk_json", kwargs_dict)
        if disks is not None:
            datastoreName, datastoreID = self._load_disks(client, disks)

        for host in hosts:
            # Need to verify that the host is on and connected (not in maintenance mode)
            # power_state can be 'on' 'maintenance' 'off'
            if (host.v_owning_cluster == cluster and host.power_state == "on"):
                if (leastVMs is None or host.v_total_vms < leastVMs):
                    hostID = str(host.id)
                    hostName = str(host.name)
                    leastVMs = host.v_total_vms
                    if (datastoreName is None and datastoreID is None):
                        datastoreName, datastoreID = self._check_storages(client,
                                                                         host.host_storages,
                                                                         kwargs_dict)

        # only success if all of these are not None
        # fail otherwise
        success = cluster is not None and hostID is not None and datastoreID is not None
        result = {'clusterName': cluster,
                  'hostName': hostName,
                  'hostID': hostID,
                  'datastoreName': datastoreName,
                  'datastoreID': datastoreID}
        return (success, result)

    def _check_storages(self, client, storages, kwargs_dict):
        mostSpace = 0
        dName = None
        dId = None
        for datastore in storages:
            ds = client.collections.data_stores(datastore["storage_id"])
            if self._filter_datastores(ds.name, kwargs_dict):
                if ds.free_space > mostSpace:
                    dName = ds.name
                    dId = str(ds.id)
                    mostSpace = ds.free_space

        return (dName, dId)

    def _find_storage(self, client, datastore_name):
        all_datastores = client.collections.data_stores.all
        dName = None
        dId = None
        for datastore in all_datastores:
            if datastore.name == datastore_name:
                dName = datastore.name
                dId = str(datastore.id)
                break

        return (dName, dId)

    def _filter_datastores(self, datastore, kwargs_dict):
        datastoreFilters = self._get_arg("datastoreFilterRegEx", kwargs_dict)
        if not type(datastoreFilters) is dict:
            datastoreFilters = json.loads(datastoreFilters)

        datastoreFilterRegEx = datastoreFilters["filters"]
        """Filter out the datastores by name
        Include if the datastore name does NOT match any of the regex expressions
        """
        for regex in datastoreFilterRegEx:
            if re.search(regex.strip(), datastore):
                return False
        return True

    def bestfit(self, client, kwargs_dict):
        attributes = self._attributes_str(["v_owning_cluster", "v_total_vms", "host_storages"])
        allHosts = client.collections.hosts.query_string(  # pylint: disable=no-member
            expand="resources", attributes=attributes)
        if not allHosts:
            raise ValueError("No Hosts were returned from ManageIQ")

        return self._check_hosts(client, allHosts, kwargs_dict)
