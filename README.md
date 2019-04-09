DRAC Facts
==========

Role providing a module to gather facts about BIOS settings and RAID
configuration on Dell machines with an iDRAC card.

Requirements
------------

The role provides a module, `drac_facts`, that is dependent upon the
`python-dracclient` module. This must be installed in order for this module
to function correctly.

Role Variables
--------------

`address`: IP address or hostname of the iDRAC BMC.

`username`: Username credentials for the iDRAC.

`password`: Password credentials for the iDRAC.

Dependencies
------------

None

Example Playbook
----------------

With the iDRAC BMCs in the inventory, this role may be used as follows:

    - hosts: dell-server-bmcs
      gather_facts: false
      roles:
        - role: stackhpc.drac-facts
      tasks:
        - name: Gather facts via DRAC
          local_action:
            module: drac_facts
            address: "{{ ansible_host }}"
            username: foo
            password: bar

        - name: Show gathered facts about BIOS settings
          debug:
            var: drac_bios_settings

        - name: Show gathered facts about jobs
          debug:
            var: drac_jobs

        - name: Show gathered facts about unfinished jobs
          debug:
            var: drac_unfinished_jobs

        - name: Show gathered facts about RAID controllers
          debug:
            var: drac_raid_controllers

        - name: Show gathered facts about physical disks
          debug:
            var: drac_physical_disks

        - name: Show gathered facts about virtual disks
          debug:
            var: drac_virtual_disks

License
-------

BSD

Author Information
------------------

- Authors: Mark Goddard & Stig Telfer
- Company: StackHPC Ltd
- Website: https://stackhpc.com
