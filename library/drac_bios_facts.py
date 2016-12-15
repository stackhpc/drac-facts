#!/usr/bin/python

from ansible.module_utils.basic import *

# Store a list of import errors to report to the user.
IMPORT_ERRORS = []
try:
    import dracclient.client as drac
except Exception as e:
    IMPORT_ERRORS.append(e)


DOCUMENTATION = """
WM
"""

EXAMPLES = """
WM
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


def get_jobs(bmc, only_unfinished):
    """Get all jobs for this DRAC.

    :param bmc: A dracclient.client.DRACClient instance
    :param only_unfinished: Whether to return only unfinished jobs
    :returns: A list of dicts describing jobs
    """
    jobs = bmc.list_jobs(only_unfinished)
    return [dict(job._asdict()) for job in jobs]


def get_bios_facts(module):
    """Get facts about the DRAC-managed BIOS.

    :param module: The Module instance
    :returns: A dict of BIOS facts
    """
    bmc = build_client(module)
    settings = get_bios_settings(bmc)
    jobs = get_jobs(bmc, False)
    unfinished_jobs = get_jobs(bmc, True)
    return {
        "drac_bios_settings": settings,
        "drac_jobs": jobs,
        "drac_unfinished_jobs": unfinished_jobs,
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
        facts = get_bios_facts(module)
    except Exception as e:
        module.fail_json(msg="Failed to get BIOS facts: %s" % repr(e))
    else:
        module.exit_json(changed=False,
                         ansible_facts=facts,
                         **facts)


if __name__ == '__main__':
    main()
