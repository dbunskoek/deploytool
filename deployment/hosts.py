from fabric.api import env
from fabric.colors import *
import os

from deployment.instances import RemoteInstance
import deployment.utils as utils


class RemoteHost(object):
    """
    Configuration for remote host
    =============================

    Collection of all settings (Project, Host, Instance).
    Updates fabric environment.

    Example project structure on staging server:

        /var/www/vhosts/
            /s-myprojectname/
                07aeb1319f4fbb2458028035c4c25a3044015be6/
                987e00fe968b891157794d9c9f488ff55c91cb9f/
                cache/
                current_instance/   => /var/www/vhosts/s-myprojectname/07aeb1319f4fbb2458028035c4c25a3044015be6/
                log/
                media/
                previous_instance/  => /var/www/vhosts/s-myprojectname/987e00fe968b891157794d9c9f488ff55c91cb9f/
                scripts/
                django.wsgi
                settings.py
    """

    instance = None
    settings = {}

    def __init__(self, *args, **kwargs):

        self.instance = RemoteInstance()

        self.settings.update(kwargs['project_settings'])
        self.settings.update(self.get_settings_for_host())
        self.settings.update(self.get_settings_for_instance())

        env.update(self.settings)

    def reload(self):

        print(green('\nRestarting website.'))
        utils.commands.touch_wsgi(env.project_path)

    def show_status(self):

        current_instance = utils.commands.read_link(env.current_instance_path)
        previous_instance = utils.commands.read_link(env.previous_instance_path)
        fabric_log_file = os.path.join(env.log_path, 'fabric.log')
        fabric_log_dump = utils.commands.tail_file(fabric_log_file)

        print(green('\nCurrent instance:'))
        print(current_instance)
        print(green('\nPrevious instance:'))
        print(previous_instance)
        print(green('\nFabric log:'))
        print(fabric_log_dump)

    def get_settings_for_host(self):
        """
        Available settings for Host
        ===========================

            cache_path                  Python pip egg cache path
            current_instance_path       Symlink to current instance
            database_name               Database name for project (same as project name)
            environment                 Name for deploy-environment
            hosts                       List of available hostnames to connect to
            log_path                    Project log folder for Apache, Nginx, Pip, Fabric
            previous_instance_path      Symlink to previous instance
            projects_root               Root folder for all projects on server
            project_path                Root folder for this project
            scripts_path                Folder with helper mysql-scripts
            user                        Remote user for this project (same as project name)
        """

        projects_root = self.settings['projects_root']
        project_name = '%s%s' % (self.settings['project_name_prefix'], self.settings['project_name'])
        project_path = os.path.join(projects_root, project_name)

        return {
            'cache_path': os.path.join(project_path, 'cache'),
            'current_instance_path': os.path.join(project_path, 'current_instance'),
            'database_name': project_name,
            'environment': self.settings['environment'],
            'hosts': self.settings['hosts'],
            'log_path': os.path.join(project_path, 'log'),
            'previous_instance_path': os.path.join(project_path, 'previous_instance'),
            'project_root': projects_root,
            'project_path': project_path,
            'scripts_path': os.path.join(project_path, 'scripts'),
            'user': project_name,
        }

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

        instance_path = os.path.join(self.settings['project_path'], self.instance.stamp)

        return {
            'backup_path': os.path.join(instance_path, 'backup'),
            'instance_stamp': self.instance.stamp,
            'instance_path': instance_path,
            'source_path': os.path.join(instance_path, self.settings['project_name']),
            'virtualenv_path': os.path.join(instance_path, 'env'),
        }

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
