from fabric.api import env


class FabricEnvironmentUpdater(object):
    """
    Base class for hosts
        - collects all settings (Project, Host, Instance)
        - updates fabric environment
    """

    settings = {}

    def update_fabric_environment(self):
        """ Append supplied settings to global Fabric environment """

        env.update(self.settings)
