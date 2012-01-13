from fabric.api import env

import utils


class Host(object):
    """
    Generic Host class.
    Collection of all settings (Project, Host, Instance).
    Updates fabric environment.
    """

    instance = None
    settings = {}

    def __init__(self, *args, **kwargs):

        self.settings.update(kwargs['project_settings'])
        self.settings.update(self.get_settings_for_host())
        self.settings.update(self.get_settings_for_instance())

        env.update(self.settings)

    def reload(self):

        utils.commands.touch_wsgi(env.project_path)

    def get_settings_for_host(self):

        raise NotImplementedError

    def get_settings_for_instance(self):

        raise NotImplementedError

    def update_settings_for_instance(self, stamp):

        self.instance.stamp = stamp
        self.settings.update(self.get_settings_for_instance())

        env.update(self.settings)
