=================
Fabric Deployment
=================

Project application for deployment, provisioning and local tasks.


Remote requirements:
====================
* Apache
* Cent OS
* gcc
* Nginx
* MYSQL
* MySQL-python
* MySQL-devel
* OpenSSH
* Pip (0.8.1+)
* Python (2.6)
* python-devel
* sudo
* virtualenv (1.6+)


Local requirements:
===================
* Fabric (1.2.2+)
* Git (1.6+)


Usage:
======
Add deployment app to Django project:

::

    $ cd /path/to/project
    $ git clone git@github.com:leukeleu/deployment-fabric.git
    $ mv ./deployment-fabric/deployment ./deployment
    $ mv ./deployment-fabric/fabfile.py ./fabfile.py
    $ rm -rf ./deployment-fabric

Prepare by having passwords at hand for these users:

* OS: provisioning user (SSH, sudo)
* OS: project user (deployment tasks)
* DB: mysql root user (database provisioning)
* DB: mysql project user (deployment tasks)
* DJ: django admin user (site admin access)

Provision & deploy the project:

* Update fabfile.py with correct settings
* Run setup ('fab staging setup')
* Manage access ('fab staging keys')
* First deploy ('fab staging deploy')


Examples:
=========

::

    # list all available tasks
    $ fab list

    # show detailed information for task
    $ fab -d TASKNAME

    # execute task with parameters
    $ fab TASKNAME:ARG=VALUE

    # example: deploy latest version of local current branch to staging server
    $ fab staging deploy

