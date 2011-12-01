import os

from hosts.base import FabricEnvironmentUpdater
from hosts.staging.instance import StagingInstance


class StagingHost(FabricEnvironmentUpdater):
    """ Configuration for staging environment """

    instance = None
    settings = {
        'environment': 'staging',
        'hosts': ['', ],
        'project_root': os.path.join('/', 'var', 'www', 'vhosts'),
    }

    def __init__(self, *args, **kwargs):

        self.instance = StagingInstance(*args, **kwargs)

        self.update_settings(settings=kwargs['project_settings'])
        self.update_settings(settings=self._get_settings_for_host())
        self.update_settings(settings=self._get_settings_for_instance())

    def update_settings(self, settings):
        """ Appends settings to self and updates Fabric Environment """

        self.settings.update(settings)
        self.update_fabric_environment()

    def _get_settings_for_host(self):

        staging_project_name = 's-%s' % self.settings['project_name']
        project_path = os.path.join(self.settings['project_root'], staging_project_name)

        return {
            'cache_path': os.path.join(self.settings['project_root'], 'python_egg_cache'),
            'project_path': project_path,
            'log_path': os.path.join(project_path, 'log'),
            'scripts_path': os.path.join(project_path, 'scripts'),
            'database_name': staging_project_name,
            'user': staging_project_name,
        }

    def _get_settings_for_instance(self):

        instance_path = os.path.join(self.settings['project_path'], self.instance.stamp)

        return {
            'instance_stamp': self.instance.stamp,
            'instance_path': instance_path,
            'backup_path': os.path.join(instance_path, 'backup'),
            'virtualenv_path': os.path.join(instance_path, 'env'),
            'source_path': os.path.join(instance_path, self.settings['project_name']),
        }
