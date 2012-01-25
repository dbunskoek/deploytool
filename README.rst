=================
Fabric Deployment
=================

Deploy a project to an existing website on a remote server.

Remote dependencies:
====================
* MYSQL
* Pip (0.8.1+)
* distribute (0.6.14+)
* virtualenv (1.6+)

Local dependencies:
===================
* Fabric (1.2.2+)
* Git (1.6+)

Remote setup:
=============
NOTE: This setup is still a work in progress!

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

* TODO

Usage:
======

* TODO
