from fabric.api import env
from fabric.colors import *

import deployment.utils as utils


class RemoteHost(object):
    """
    Configuration for remote host
    =============================

    Collection of all settings (Project, Host, Instance).
    Updates fabric environment.

    Example project structure on staging server:

        /var/www/vhosts/
            /s-PROJECTNAME/
                07aeb1319f4fbb2458028035c4c25a3044015be6/
                987e00fe968b891157794d9c9f488ff55c91cb9f/
                cache/
                current_instance/   => /var/www/vhosts/s-PROJECTNAME/07aeb1319f4fbb2458028035c4c25a3044015be6/
                log/
                media/
                previous_instance/  => /var/www/vhosts/s-PROJECTNAME/987e00fe968b891157794d9c9f488ff55c91cb9f/
                scripts/
                django.wsgi
                settings.py
    """

    instance = None
    settings = {}

    def __init__(self, *args, **kwargs):

        self.settings.update(kwargs['project_settings'])
        self.settings.update(self.get_settings_for_host())
        self.settings.update(self.get_settings_for_instance())

        env.update(self.settings)

    def reload(self):

        print(green('\nRestarting website.'))
        utils.commands.touch_wsgi(env.project_path)

    def get_settings_for_host(self):
        """
        Available settings for Host
        ===========================

            cache_path                  Python pip egg cache
            current_instance_path       Symlink to current instance
            database_name               Database name for project (same as project name)
            hosts                       List of available hostnames to connect to
            log_path                    Project log folder for Apache, Nginx, Pip, Fabric
            previous_instance_path      Symlink to previous instance
            project_root                Root folder for all projects on server
            project_path                Root folder for this project
            scripts_path                Folder with helper mysql-scripts
            user                        Remote user for this project (same as project name)
        """

        raise NotImplementedError

    def get_settings_for_instance(self):
        """
        Available settings for Instance
        ======================================

            backup_path         Folder for database backup files
            instance_stamp      Identifier for instance (used as folder name for instance_path)
            instance_path       Root folder for an instance of this project
            source_path         Folder containing source code from Version Control System
            virtualenv_path     Virtualenv folder for this specific instance
        """

        raise NotImplementedError

    def load_current_instance(self):
        """ Configures settings for current(ly active) instance """

        print(green('\nUpdating settings for current instance.'))
        current_stamp = utils.instance.get_instance_stamp(env.current_instance_path)
        self.load_instance(stamp=current_stamp)

    def load_instance(self, stamp):
        """ Configures settings for specified instance """

        print(green('\nUpdating settings for instance %s.' % stamp))
        self.update_settings_for_instance(stamp=stamp)

    def update_settings_for_instance(self, stamp):

        self.instance.stamp = stamp
        self.settings.update(self.get_settings_for_instance())

        env.update(self.settings)
