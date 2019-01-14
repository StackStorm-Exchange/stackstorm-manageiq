#!/usr/bin/env python

import datetime
import dateutil.parser
import re
import requests

from st2common.runners.base_action import Action

# silence SSL warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    pass


class RemoveOldSnapshots(Action):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(RemoveOldSnapshots, self).__init__(config)

    def create_session(self, username, password):
        """Creates a new session object for HTTP communication
        :returns: the connection session
        """
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        return session

    def get_vms(self):
        """Retrieves a list of VMs and their snapshots from the server
        :returns: VM objects with embedded snapshots
        """
        response = self.session.get("https://{}/api/vms?expand=resources&attributes=id,"
                                    "snapshots,name".format(self.server))
        response.raise_for_status()
        vms = response.json()["resources"]
        return vms

    def compile_regexes(self, regex_list):
        """Compiles all of the regexes in the list into patterns
        :returns: list of compiled patterns
        """
        patterns = []
        for r in regex_list:
            patterns.append(re.compile(r))
        return patterns

    def matches_pattern_list(self, name, pattern_list):
        """Compares the name to each pattern in the list
        :returns: True if the name matches any of the patterns. False if nothing matches.
        """
        for p in pattern_list:
            if p.search(name):
                return True
        return False

    def current_time_utc(self):
        return datetime.datetime.utcnow()

    def delete_old_snapshots(self, vms, max_age_days, name_ignore_patterns):
        """Delets all of the snapshots older than max_age_days.
        Ignorning any snapshot with a name that matches one of the name_ignore_pattern.
        """
        date_now = self.current_time_utc()

        deleted_snapshots = []
        ignored_snapshots = []
        try:
            for vm in vms:
                for snap in vm.get("snapshots", []):
                    # ignore if the snapshot name matches one of the regexes
                    if self.matches_pattern_list(snap['name'], name_ignore_patterns):
                        ignored_snapshots.append("{0}: {1}".format(vm['name'], snap['name']))
                        continue

                    # Remove the trailing Z from the date
                    # Z and UTC time are the same
                    created = snap['created_on'][:-1]
                    # advanced the created date by max_age_days and compare to
                    # the current time to determine if it is too old
                    advanced = (dateutil.parser.parse(created) +  # noqa: W504
                                datetime.timedelta(days=max_age_days))

                    print "{}".format(advanced)
                    # Snapshots older than the max age will be deleted
                    if advanced < date_now:
                        deleted_snapshots.append("{0}: {1}".format(vm['name'], snap['name']))
                        self.session.delete("https://{0}/api/vms/{1}/snapshots/{2}".
                                            format(self.server,
                                                   snap['vm_or_template_id'],
                                                   snap['id']))
        except Exception as e:
            return (False, {'error': e,
                            'deleted_snapshots': deleted_snapshots,
                            'ignored_snapshots': ignored_snapshots})

        return (True, {'deleted_snapshots': deleted_snapshots,
                       'ignored_snapshots': ignored_snapshots})

    def run(self, **kwargs):
        """Main entry point for the StackStorm actions to execute the operation.
        """
        # Connect to the API and return the session
        self.session = self.create_session(kwargs['username'], kwargs['password'])
        self.server = kwargs['server']

        # get all of the VMs and snapshots
        vms = self.get_vms()

        # All snapshots older than the following age (in days) will be deleted
        max_age_days = kwargs['max_age_days']

        # compile the regexes (for faster performance)
        name_ignore_patterns = self.compile_regexes(kwargs["name_ignore_regexes"])

        # delete the old snapshots
        return self.delete_old_snapshots(vms, max_age_days, name_ignore_patterns)
