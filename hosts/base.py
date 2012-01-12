from fabric.api import env


class FabricEnvironmentUpdater(object):
    """
    Collection of all settings (Project, Host, Instance).
    Updates fabric environment.
    """

    instance = None
    settings = {}

    def __init__(self, *args, **kwargs):

        self.settings.update(kwargs['project_settings'])
        self.settings.update(self.get_settings_for_host())
        self.settings.update(self.get_settings_for_instance())

        self.update_fabric_environment()

    def update_fabric_environment(self):

        env.update(self.settings)

    def get_settings_for_host(self):

        raise NotImplementedError

    def get_settings_for_instance(self):

        raise NotImplementedError
