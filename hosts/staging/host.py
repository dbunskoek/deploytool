import os

from deployment.hosts.host import Host
from instance import StagingInstance


class StagingHost(Host):
    """
    Configuration for staging environment
    =====================================

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

    def __init__(self, *args, **kwargs):

        self.instance = StagingInstance()
        super(StagingHost, self).__init__(*args, **kwargs)

    def get_settings_for_host(self):
        """
        Available settings for StagingHost
        ==================================

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

        project_name = 's-%s' % self.settings['project_name']
        project_root = self.settings['project_root_staging']
        project_path = os.path.join(project_root, project_name)

        return {
            'cache_path': os.path.join(project_path, 'cache'),
            'current_instance_path': os.path.join(project_path, 'current_instance'),
            'database_name': project_name,
            'hosts': self.settings['host_staging'],
            'log_path': os.path.join(project_path, 'log'),
            'previous_instance_path': os.path.join(project_path, 'previous_instance'),
            'project_root': project_root,
            'project_path': project_path,
            'scripts_path': os.path.join(project_path, 'scripts'),
            'user': project_name,
        }

    def get_settings_for_instance(self):
        """
        Available settings for StagingInstance
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
