from fabric.api import env
from fabric.colors import *

import deployment.utils


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

        print(green('\nRestarting website.'))
        deployment.utils.commands.touch_wsgi(env.project_path)

    def get_settings_for_host(self):

        raise NotImplementedError

    def get_settings_for_instance(self):

        raise NotImplementedError

    def load_current_instance(self):
        """ Configures settings for current(ly active) instance """

        print(green('\nUpdating settings for current instance.'))
        current_instance_stamp = utils.instance.get_current_instance_stamp(env.current_instance_path)
        self.update_settings_for_instance(stamp=current_instance_stamp)

    def update_settings_for_instance(self, stamp):

        self.instance.stamp = stamp
        self.settings.update(self.get_settings_for_instance())

        env.update(self.settings)
