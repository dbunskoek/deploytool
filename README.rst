=================
Fabric Deployment
=================

Project application for deployment, provisioning and local tasks.

Remote requirements:
====================
* Apache
* gcc
* Nginx
* MYSQL
* MySQL-python
* OpenSSH
* Pip (0.8.1+)
* Python (2.6)
* virtualenv (1.6+)

Local requirements:
===================
* Fabric (1.2.2+)
* Git (1.6+)

Usage:
======
TODO ...

::

    # list all available tasks
    $ fab list

    # show detailed information for task
    $ fab -d TASKNAME

    # execute task with parameters
    $ fab TASKNAME:ARG=VALUE

    # example: deploy latest version of local current branch to staging server
    $ fab staging deploy

