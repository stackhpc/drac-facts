DRAC BIOS Facts
===============

Role providing a module to gather facts about BIOS configuration on Dell
machines with an iDRAC card.

Requirements
------------

The role provides a module, `drac_bios_facts`, that is dependent upon the
`python-dracclient` module. This must be installed in order for this module
to function correctly.


Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

This role may be used as follows:

    - hosts: dell-servers
      roles:
        - role: markgoddard.drac-bios-facts
      tasks:
        - name: Gather facts about BIOS settings via DRAC
          local_action:
            module: drac_bios_facts
            address: 1.2.3.4
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

License
-------

BSD

Author Information
------------------

- Authors: Mark Goddard & Stig Telfer
- Company: StackHPC Ltd
- Website: https://stackhpc.com
