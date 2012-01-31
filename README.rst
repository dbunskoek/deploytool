=================
Fabric Deployment
=================

Deploy a project to an existing website on a remote server.

Remote requirements:
====================
* MYSQL
* Pip (0.8.1+)
* virtualenv (1.6+)

Local requirements:
===================
* Fabric (1.2.2+)
* Git (1.6+)

Remote setup:
=============
NOTE: This section is still WIP.

::

    # connect to server (install remote requirements if needed!)
    $ ssh LOCALUSER@REMOTESERVER

    # add and swith to project user
    $ sudo adduser PROJECTUSER
    $ su PROJECTUSER

    # create/copy files and folders for project
    $ cd /var/www/vhost
    $ mkdir PROJECTNAME
    $ cd PROJECTNAME
    $ mkdir PROJECTNAME/cache
    $ mkdir PROJECTNAME/log
    $ mkdir PROJECTNAME/media
    $ mkdir PROJECTNAME/scripts
    "copy assets/scripts to scripts" (TODO command)

    # configuration (see assets for examples)
    $ vim PROJECTNAME/scripts/credentials.py
    $ vim PROJECTNAME/settings.py
    $ vim PROJECTNAME/django.wsgi
    $ vim /etc/nginx/sites-available/PROJECTNAME
    $ vim /etc/apache/sites-available/PROJECTNAME

    ... (TODO)

Local setup:
============
NOTE: This section is still WIP.

* TODO

Usage:
======
NOTE: This section is still WIP.

::

    # list all available tasks
    $ fab --list

    # show detailed information for task
    $ fab -d TASKNAME

    # execute task with parameters
    $ fab TASKNAME:ARG=VALUE

...
