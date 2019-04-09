#!/usr/bin/python

from ansible.module_utils.basic import *

# Store a list of import errors to report to the user.
IMPORT_ERRORS = []
try:
    import dracclient.client as drac
except Exception as e:
    IMPORT_ERRORS.append(e)


DOCUMENTATION = """
module: drac_facts
short_description: Ansible module for gathering facts via DRAC
description:
  - Ansible module for gathering BIOS settings and RAID configuration on Dell
    machines with an iDRAC card.
author: Mark Goddard (@markgoddard) & Stig Telfer (@oneswig)
requirements:
  - python-dracclient python module
options:
  address:
    description: Address to use when communicating with the DRAC
    required: True
  username:
    description: Username to use when communicating with the DRAC
    required: True
  password:
    description: Address to use when communicating with the DRAC
    required: True
"""

EXAMPLES = """
# Gather DRAC facts
- drac_facts:
    address: 1.2.3.4
    username: admin
    password: secretpass
"""

RETURN = """
drac_bios_settings:
  description: >
    Dict mapping names of BIOS settings to a dict containing at least one item,
    'current_value'. If there is a pending value for the setting then
    a 'pending_value' item will exist. If the setting is a multiple choice
    value, then 'possible_values' may be a list of possible values for the
    setting.
  returned: success
  type: dict
  sample:
    NumLock:
      current_value: "On"
      pending_value: "Off"
      possible_values: ["On", "Off"]
drac_jobs:
  description: >
    List of dicts containing DRAC jobs.
  returned: success
  type: list
  sample:
    - id: "JID_831286578145"
      message: "Job completed successfully."
      name: "Config:RAID:RAID.Integrated.1-1"
      percent_complete: "100"
      start_time: "TIME_NOW"
      status: "Completed"
      until_time: "TIME_NA"
drac_unfinished_jobs:
  description: >
    List of dicts containing unfinished DRAC jobs.
  returned: success
  type: list
  sample:
    - id: "JID_831286578145"
      message: "Job completed successfully."
      name: "Config:RAID:RAID.Integrated.1-1"
      percent_complete: "100"
      start_time: "TIME_NOW"
      status: "Completed"
      until_time: "TIME_NA"
drac_raid_controllers:
  description: >
    List of dicts containing information about RAID controllers in the system.
  returned: success
  type: list
  sample:
    - description: "Integrated RAID Controller 1"
      firmware_version: "25.4.0.0017"
      id: "RAID.Integrated.1-1"
      manufacturer: "DELL"
      model: "PERC H730 Mini"
      primary_status: "ok"
drac_physical_disks:
  description: >
    List of dicts containing information about physical disks in the system.
  returned: success
  type: list
  sample:
    - controller: "RAID.Integrated.1-1"
      description: "Disk 0 in Backplane 1 of Integrated RAID Controller 1"
      firmware_version: "G201DL29"
      free_size_mb: 267008
      id: "Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1"
      interface_type: "sata"
      manufacturer: "ATA"
      media_type: "ssd"
      model: "INTEL SSDSC2BX40"
      raid_status: "online"
      serial_number: "BTHC549600A8400VGN"
      size_mb: 380928
      status: "ok"
drac_virtual_disks:
  description: >
    List of dicts containing information about virtual disks in the system.
  returned: success
  type: list
  sample:
    - controller: "RAID.Integrated.1-1"
      description: "Virtual Disk 0 on Integrated RAID Controller 1"
      id: "Disk.Virtual.0:RAID.Integrated.1-1"
      name: "Virtual Disk0"
      pending_operations: null
      raid_level: "1"
      raid_status: "online"
      size_mb: 113920
      span_depth: 1
      span_length: 2
"""


def build_client(module):
    """Build a DRAC client instance.

    :param module: The AnsibleModule instance
    :returns: dracclient.client.DRACClient instance
    """
    return drac.DRACClient(module.params['address'],
                           module.params['username'],
                           module.params['password'])


def get_bios_settings(bmc):
    """Get all available settings and permitted values for this BIOS.

    :param bmc: A dracclient.client.DRACClient instance
    :returns: A dict of BIOS settings
    """
    bios_settings = bmc.list_bios_settings()
    # Convert the settings to something that is JSON-serialisable.
    settings = {}
    for param, value in bios_settings.items():
        setting = {}
        # Not all attributes exist on all settings, so allow them to be absent.
        attrs = {
            'current_value',
            'pending_value',
            'possible_values',
        }
        for attr in attrs:
            if hasattr(value, attr):
                setting[attr] = getattr(value, attr)
        settings[param] = setting
    return settings


def get_nic_settings(bmc):
    """Get all available NIC settings and permitted values.

    :param bmc: A dracclient.client.DRACClient instance
    :returns: A dict of NIC settings
    """
    nic_settings = bmc.list_nics()
    return nic_settings


def namedtuples_to_dicts(nts):
    """Convert a list of namedtuples to a list of dicts.

    :param nts: A list of collections.namedtuple objects
    :returns: A list of dicts
    """
    return [dict(nt._asdict()) for nt in nts]


def get_raid_config(bmc):
    """Get RAID configuration for this DRAC.

    :param bmc: A dracclient.client.DRACClient instance
    :returns: A 3-tuple containing RAID controllers, physical disks and virtual
        disks.
    """
    controllers = bmc.list_raid_controllers()
    pdisks = bmc.list_physical_disks()
    vdisks = bmc.list_virtual_disks()
    controllers = namedtuples_to_dicts(controllers)
    pdisks = namedtuples_to_dicts(pdisks)
    vdisks = namedtuples_to_dicts(vdisks)
    return controllers, pdisks, vdisks


def get_jobs(bmc, only_unfinished):
    """Get all jobs for this DRAC.

    :param bmc: A dracclient.client.DRACClient instance
    :param only_unfinished: Whether to return only unfinished jobs
    :returns: A list of dicts describing jobs
    """
    jobs = bmc.list_jobs(only_unfinished)
    return namedtuples_to_dicts(jobs)


def get_facts(module):
    """Get facts about the DRAC-managed system.

    :param module: The Module instance
    :returns: A dict of facts
    """
    bmc = build_client(module)
    bios_settings = get_bios_settings(bmc)
    nic_settings = get_nic_settings(bmc)
    controllers, pdisks, vdisks = get_raid_config(bmc)
    jobs = get_jobs(bmc, False)
    unfinished_jobs = get_jobs(bmc, True)
    return {
        "drac_bios_settings": bios_settings,
        "drac_nic_settings": nic_settings,
        "drac_jobs": jobs,
        "drac_unfinished_jobs": unfinished_jobs,
        "drac_raid_controllers": controllers,
        "drac_physical_disks": pdisks,
        "drac_virtual_disks": vdisks,
    }


def main():
    """Module entry point."""
    module = AnsibleModule(
        argument_spec=dict(
            address=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
        ),
        supports_check_mode=True,
    )

    # Fail if there were any exceptions when importing modules.
    if IMPORT_ERRORS:
        module.fail_json(msg="Import errors: %s" %
                         ", ".join([repr(e) for e in IMPORT_ERRORS]))

    try:
        facts = get_facts(module)
    except Exception as e:
        module.fail_json(msg="Failed to get facts: %s" % repr(e))
    else:
        module.exit_json(changed=False,
                         ansible_facts=facts,
                         **facts)


if __name__ == '__main__':
    main()
