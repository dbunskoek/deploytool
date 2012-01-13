import os

from hosts.host import Host
from hosts.staging.instance import StagingInstance


class StagingHost(Host):
    """ Configuration for staging environment """

    host_names = None # e.g. ['127.0.0.1', ]

    def __init__(self, *args, **kwargs):

        self.instance = StagingInstance()
        super(StagingHost, self).__init__(*args, **kwargs)

    def get_settings_for_host(self):

        staging_project_name = 's-%s' % self.settings['project_name']
        project_root = os.path.join('/', 'var', 'www', 'vhosts')
        project_path = os.path.join(project_root, staging_project_name)

        return {
            'cache_path': os.path.join(project_root, 'python_egg_cache'),
            'current_instance_path': os.path.join(project_path, 'current_instance'),
            'database_name': staging_project_name,
            'hosts': self.host_names,
            'log_path': os.path.join(project_path, 'log'),
            'previous_instance_path': os.path.join(project_path, 'previous_instance'),
            'project_root': project_root,
            'project_path': project_path,
            'scripts_path': os.path.join(project_path, 'scripts'),
            'user': staging_project_name,
        }

    def get_settings_for_instance(self):

        instance_path = os.path.join(self.settings['project_path'], self.instance.stamp)

        return {
            'backup_path': os.path.join(instance_path, 'backup'),
            'instance_stamp': self.instance.stamp,
            'instance_path': instance_path,
            'source_path': os.path.join(instance_path, self.settings['project_name']),
            'virtualenv_path': os.path.join(instance_path, 'env'),
        }
